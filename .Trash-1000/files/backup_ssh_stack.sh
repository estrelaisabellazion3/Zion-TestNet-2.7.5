#!/usr/bin/env bash
#
# ZION SSH Stack Backup Script
# Zazálohuje celý současný ZION stack z SSH serveru
#

set -e

echo "💾 ZION SSH Stack Backup"
echo "========================"

# Konfigurace
SERVER_HOST="91.98.122.165"
SERVER_USER="root"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/maitreya/zion_backups"
BACKUP_NAME="zion_ssh_backup_$TIMESTAMP"
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

mkdir -p "$BACKUP_DIR"

echo "📅 Backup timestamp: $TIMESTAMP"
echo "📂 Local backup path: $FULL_BACKUP_PATH"

echo ""
echo "🔍 Analyzing current SSH stack..."

# Get current status
ssh "$SERVER_USER@$SERVER_HOST" << 'EOF'
echo "=== Current ZION Stack Status ==="
echo ""
echo "📦 Docker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "📂 Directory structure:"
find /root -maxdepth 2 -name "*zion*" -o -name "*mining*" -o -name "*pool*" 2>/dev/null | head -10

echo ""
echo "🗂️  Files in /root:"
ls -la /root/ | grep -i zion || true

echo ""
echo "📊 Disk usage:"
df -h /root

echo ""
echo "🌐 Open ports (ZION related):"
netstat -tlnp | grep -E "(3335|8332|8333|18089)" || true
EOF

echo ""
echo "💾 Creating backup..."

# Create docker-compose backup
echo "🐳 Backing up Docker stack..."
ssh "$SERVER_USER@$SERVER_HOST" "cd /root && docker-compose logs > docker-compose.logs 2>&1 || true"

# Backup entire /root directory structure (but exclude large files)
echo "📁 Backing up file system..."
rsync -avz \
    --exclude='*.log' \
    --exclude='*.db-journal' \
    --exclude='venv/' \
    --exclude='node_modules/' \
    --exclude='.git/' \
    --exclude='*.tmp' \
    "$SERVER_USER@$SERVER_HOST:/root/" \
    "$FULL_BACKUP_PATH/filesystem/" || {
    echo "⚠️  Rsync failed, trying alternative backup method..."
    
    # Alternative: tar-based backup
    ssh "$SERVER_USER@$SERVER_HOST" "cd /root && tar -czf /tmp/zion_backup_$TIMESTAMP.tar.gz \
        --exclude='*.log' \
        --exclude='*.db-journal' \
        --exclude='venv' \
        --exclude='node_modules' \
        --exclude='.git' \
        . 2>/dev/null"
    
    scp "$SERVER_USER@$SERVER_HOST:/tmp/zion_backup_$TIMESTAMP.tar.gz" "$FULL_BACKUP_PATH/"
    ssh "$SERVER_USER@$SERVER_HOST" "rm -f /tmp/zion_backup_$TIMESTAMP.tar.gz"
}

# Backup Docker images and volumes
echo "🐳 Backing up Docker configuration..."
mkdir -p "$FULL_BACKUP_PATH/docker"

ssh "$SERVER_USER@$SERVER_HOST" << EOF > "$FULL_BACKUP_PATH/docker/docker_info.txt"
echo "=== Docker Images ==="
docker images

echo ""
echo "=== Docker Containers ==="
docker ps -a

echo ""
echo "=== Docker Volumes ==="
docker volume ls

echo ""
echo "=== Docker Networks ==="
docker network ls

echo ""
echo "=== Docker Compose Config ==="
if [ -f docker-compose.yml ]; then
    echo "Found docker-compose.yml:"
    cat docker-compose.yml
fi

if [ -f docker-compose.production.yml ]; then
    echo "Found docker-compose.production.yml:"
    cat docker-compose.production.yml
fi
EOF

# Export Docker images
echo "💿 Exporting Docker images..."
IMAGES=$(ssh "$SERVER_USER@$SERVER_HOST" "docker images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' | head -5")

for image in $IMAGES; do
    if [[ "$image" =~ zion ]]; then
        echo "📦 Exporting image: $image"
        image_file=$(echo "$image" | tr '/:' '_')
        ssh "$SERVER_USER@$SERVER_HOST" "docker save '$image'" | gzip > "$FULL_BACKUP_PATH/docker/${image_file}.tar.gz" &
    fi
done
wait

# Backup databases if found
echo "🗄️  Backing up databases..."
mkdir -p "$FULL_BACKUP_PATH/databases"

ssh "$SERVER_USER@$SERVER_HOST" "find /root -name '*.db' -type f 2>/dev/null" | while read db_file; do
    if [ -n "$db_file" ]; then
        relative_path=$(echo "$db_file" | sed 's|/root/||')
        mkdir -p "$FULL_BACKUP_PATH/databases/$(dirname "$relative_path")" 2>/dev/null || true
        scp "$SERVER_USER@$SERVER_HOST:$db_file" "$FULL_BACKUP_PATH/databases/$relative_path" 2>/dev/null || true
    fi
done

# Create backup summary
echo "📋 Creating backup summary..."
cat > "$FULL_BACKUP_PATH/BACKUP_INFO.md" << EOF
# ZION SSH Stack Backup

**Backup Date:** $(date)
**Backup Timestamp:** $TIMESTAMP
**Server:** $SERVER_HOST
**Backup Location:** $FULL_BACKUP_PATH

## Backup Contents

### 1. File System
- Complete /root directory structure (excluding logs, large temporary files)
- Configuration files, scripts, source code
- Location: \`filesystem/\`

### 2. Docker Configuration  
- Docker images, containers, volumes info
- Docker Compose configurations
- Exported Docker images (ZION related)
- Location: \`docker/\`

### 3. Databases
- All .db files found in /root
- SQLite databases, blockchain data
- Location: \`databases/\`

## Restoration Instructions

### Restore File System:
\`\`\`bash
rsync -avz filesystem/ root@$SERVER_HOST:/root/
\`\`\`

### Restore Docker Images:
\`\`\`bash
for image in docker/*.tar.gz; do
    gunzip -c "\$image" | ssh root@$SERVER_HOST "docker load"
done
\`\`\`

### Restore Databases:
\`\`\`bash
rsync -avz databases/ root@$SERVER_HOST:/root/
\`\`\`

## Backup Size
EOF

# Calculate backup size
du -sh "$FULL_BACKUP_PATH" >> "$FULL_BACKUP_PATH/BACKUP_INFO.md"

echo "" >> "$FULL_BACKUP_PATH/BACKUP_INFO.md"
echo "## File List" >> "$FULL_BACKUP_PATH/BACKUP_INFO.md"
find "$FULL_BACKUP_PATH" -type f | sort >> "$FULL_BACKUP_PATH/BACKUP_INFO.md"

# Create quick restore script
cat > "$FULL_BACKUP_PATH/quick_restore.sh" << EOF
#!/bin/bash
#
# Quick ZION Stack Restore Script
#

echo "🔄 Restoring ZION Stack from backup $TIMESTAMP"
echo "=============================================="

SERVER_HOST="$SERVER_HOST"
SERVER_USER="$SERVER_USER"
BACKUP_PATH="$FULL_BACKUP_PATH"

echo "⚠️  WARNING: This will overwrite current files on \$SERVER_HOST"
read -p "Continue? (y/N): " -n 1 -r
echo
if [[ ! \$REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Restore cancelled"
    exit 1
fi

echo "📁 Restoring filesystem..."
rsync -avz "\$BACKUP_PATH/filesystem/" "\$SERVER_USER@\$SERVER_HOST:/root/"

echo "🗄️  Restoring databases..."
rsync -avz "\$BACKUP_PATH/databases/" "\$SERVER_USER@\$SERVER_HOST:/root/"

echo "🐳 Restoring Docker images..."
for image in "\$BACKUP_PATH/docker"/*.tar.gz; do
    if [ -f "\$image" ]; then
        echo "📦 Loading \$(basename \$image)..."
        gunzip -c "\$image" | ssh "\$SERVER_USER@\$SERVER_HOST" "docker load"
    fi
done

echo "✅ Restore completed!"
echo "💡 You may need to restart Docker Compose manually"
EOF

chmod +x "$FULL_BACKUP_PATH/quick_restore.sh"

echo ""
echo "✅ Backup completed successfully!"
echo ""
echo "📊 Backup Summary:"
echo "  📂 Location: $FULL_BACKUP_PATH"
echo "  📏 Size: $(du -sh "$FULL_BACKUP_PATH" | cut -f1)"
echo "  📄 Files: $(find "$FULL_BACKUP_PATH" -type f | wc -l)"
echo ""
echo "📋 Backup Contents:"
echo "  🗂️  File system: filesystem/"
echo "  🐳 Docker config: docker/"
echo "  🗄️  Databases: databases/"
echo "  📄 Summary: BACKUP_INFO.md"
echo "  🔄 Restore script: quick_restore.sh"
echo ""
echo "💡 To restore later:"
echo "  bash $FULL_BACKUP_PATH/quick_restore.sh"
echo ""
echo "🗑️  This backup is safe to keep as archive"
echo "📅 Created: $(date)"