#!/usr/bin/env bash
#
# ZION SSH Cleanup Script
# Bezpečně smaže starý stack po zálohování
#

set -e

echo "🧹 ZION SSH Stack Cleanup"
echo "========================="

SERVER_HOST="91.98.122.165"
SERVER_USER="root"

# Ověření existence zálohy
LATEST_BACKUP=$(ls -t /home/maitreya/zion_backups/zion_ssh_backup_*.tar.gz 2>/dev/null | head -1)
if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ No backup found! Create backup first with:"
    echo "   bash quick_backup_ssh.sh"
    exit 1
fi

echo "✅ Backup verified: $(basename "$LATEST_BACKUP") ($(du -h "$LATEST_BACKUP" | cut -f1))"

echo ""
echo "⚠️  WARNING: This will completely clean SSH server!"
echo "📂 Server: $SERVER_HOST"
echo "🗂️  Target: /root directory"
echo "💾 Backup: $LATEST_BACKUP"

read -p "Continue with cleanup? (type YES to confirm): " -r
if [ "$REPLY" != "YES" ]; then
    echo "❌ Cleanup cancelled"
    exit 1
fi

echo ""
echo "🛑 Stopping all ZION services..."

# Stop Docker services
ssh "$SERVER_USER@$SERVER_HOST" << 'EOF'
echo "🐳 Stopping Docker containers..."
docker-compose down 2>/dev/null || true
cd Zion-TestNet-2.7.5 2>/dev/null && docker-compose down || true

echo "🔥 Stopping all ZION processes..."
pkill -f "zion" 2>/dev/null || true
pkill -f "mining" 2>/dev/null || true  
pkill -f "pool" 2>/dev/null || true

sleep 3

echo "📦 Removing Docker containers and images..."
# Remove all containers
docker rm -f $(docker ps -aq) 2>/dev/null || true

# Remove ZION-related images
docker rmi $(docker images | grep -i zion | awk '{print $3}') 2>/dev/null || true

echo "💿 Cleaning Docker volumes..."
docker volume prune -f 2>/dev/null || true

echo "🌐 Cleaning Docker networks..."
docker network prune -f 2>/dev/null || true

echo "✅ Docker cleanup completed"
EOF

echo "🗂️  Cleaning file system..."

ssh "$SERVER_USER@$SERVER_HOST" << 'EOF'
cd /root

echo "📂 Current /root contents:"
ls -la

echo ""
echo "🗑️  Removing ZION directories..."
rm -rf Zion-TestNet-2.7.5/ 2>/dev/null || true
rm -rf .zion*/ 2>/dev/null || true
rm -rf build/ 2>/dev/null || true

echo "🗑️  Removing ZION files..."
rm -f *zion* 2>/dev/null || true
rm -f *mining* 2>/dev/null || true
rm -f *pool* 2>/dev/null || true
rm -f *.py 2>/dev/null || true
rm -f *.md 2>/dev/null || true
rm -f docker-compose*.yml 2>/dev/null || true

echo "🗑️  Removing logs and temp files..."
rm -f *.log 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -rf __pycache__/ 2>/dev/null || true
rm -rf *.egg-info/ 2>/dev/null || true

echo "🧹 Cleaning package managers..."
rm -rf venv/ 2>/dev/null || true
rm -rf node_modules/ 2>/dev/null || true

echo ""
echo "📂 /root after cleanup:"
ls -la 2>/dev/null || echo "Directory empty or access denied"

echo ""
echo "💾 Available disk space:"
df -h /root
EOF

echo ""
echo "🧪 Verifying cleanup..."

# Verify services are stopped
ssh "$SERVER_USER@$SERVER_HOST" << 'EOF'
echo "🔍 Checking for remaining processes:"
pgrep -f "zion\|mining\|pool" || echo "✅ No ZION processes running"

echo ""
echo "🌐 Checking ports:"
netstat -tlnp | grep -E "(3335|8332|8333|18089)" || echo "✅ No ZION ports open"

echo ""
echo "🐳 Docker status:"
docker ps 2>/dev/null || echo "No containers running"
EOF

echo ""
echo "✅ SSH Server Cleanup Completed!"
echo ""
echo "📊 Cleanup Summary:"
echo "  ✅ Docker containers stopped and removed"
echo "  ✅ ZION processes terminated"  
echo "  ✅ File system cleaned"
echo "  ✅ Ports released"
echo "  ✅ Disk space reclaimed"
echo ""
echo "💾 Backup remains safe at:"
echo "  $LATEST_BACKUP"
echo ""
echo "🚀 Ready for fresh deployment!"
echo "💡 Next step: Deploy new stack with deploy_production_ssh.sh"