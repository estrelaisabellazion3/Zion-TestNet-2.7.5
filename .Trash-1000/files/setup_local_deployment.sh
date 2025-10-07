#!/usr/bin/env bash
#
# ZION 2.7.5 - Complete Local Deployment Script
# Vytvoří kompletní lokální blockchain stack pro vývoj a testování
#
set -e

echo "🚀 ZION 2.7.5 Local Deployment Setup"
echo "===================================="

# Barevné výstupy
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Konfigurace
ZION_ROOT="/media/maitreya/ZION1"
LOCAL_DATA_DIR="$HOME/zion_local_deployment"
VENV_DIR="$LOCAL_DATA_DIR/venv"

# Porty pro lokální stack
BLOCKCHAIN_RPC_PORT=8332
P2P_PORT=8333  
MINING_POOL_PORT=3335
API_PORT=3336
FRONTEND_PORT=3000

echo -e "${BLUE}📂 Nastavuji adresářovou strukturu...${NC}"

# Vytvořit lokální deployment adresář
mkdir -p "$LOCAL_DATA_DIR"/{data,logs,config,scripts,db}

cd "$ZION_ROOT"

echo -e "${BLUE}🐍 Nastavuji Python prostředí...${NC}"

# Vytvoření virtual environment
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}✅ Virtual environment vytvořen${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment již existuje${NC}"
fi

# Aktivace venv
source "$VENV_DIR/bin/activate"

# Upgrade pip a instalace dependencies  
pip install --upgrade pip
pip install -r requirements.txt
pip install -r requirements-pool.txt 2>/dev/null || true
pip install -r requirements-bridge.txt 2>/dev/null || true

echo -e "${GREEN}✅ Python dependencies nainstalovány${NC}"

echo -e "${BLUE}📋 Vytvářím lokální konfiguraci...${NC}"

# Vytvořit lokální .env pro development
cat > "$LOCAL_DATA_DIR/.env.local" << EOF
# ZION 2.7.5 Local Development Configuration
# Generated $(date)

# Database paths
BLOCKCHAIN_DB_PATH=$LOCAL_DATA_DIR/db/zion_blockchain.db
POOL_DB_PATH=$LOCAL_DATA_DIR/db/zion_pool.db  
NETWORK_DATA_PATH=$LOCAL_DATA_DIR/data

# Network configuration
BLOCKCHAIN_RPC_HOST=127.0.0.1
BLOCKCHAIN_RPC_PORT=$BLOCKCHAIN_RPC_PORT
P2P_HOST=127.0.0.1
P2P_PORT=$P2P_PORT
MINING_POOL_HOST=127.0.0.1
MINING_POOL_PORT=$MINING_POOL_PORT
API_HOST=127.0.0.1
API_PORT=$API_PORT

# Development settings
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Pool configuration
POOL_ADDRESS=ZION_SACRED_B0FA7E2A234D8C2F08545F02295C98
POOL_FEE_PERCENT=1.0
PAYOUT_THRESHOLD=1.0

# Mining configuration  
MINING_DIFFICULTY=4
BLOCK_REWARD=333

# Security (development only)
RPC_REQUIRE_AUTH=false
RATE_LIMIT_ENABLED=false
EOF

echo -e "${GREEN}✅ Lokální konfigurace vytvořena${NC}"

echo -e "${BLUE}📝 Vytvářím spouštěcí skripty...${NC}"

# Blockchain node script
cat > "$LOCAL_DATA_DIR/scripts/start_blockchain.sh" << 'EOF'
#!/bin/bash
source $(dirname $0)/../.env.local
cd /media/maitreya/ZION1

echo "🚀 Starting ZION Blockchain Node..."
echo "RPC: http://$BLOCKCHAIN_RPC_HOST:$BLOCKCHAIN_RPC_PORT"
echo "P2P: $P2P_HOST:$P2P_PORT"

python3 -c "
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
import time

# Initialize blockchain with local config
blockchain = NewZionBlockchain(
    db_file='$BLOCKCHAIN_DB_PATH',
    enable_p2p=True, 
    p2p_port=$P2P_PORT,
    enable_rpc=True,
    rpc_port=$BLOCKCHAIN_RPC_PORT
)

print('✅ ZION Blockchain initialized')
print(f'📊 Block height: {len(blockchain.blocks)}')
print(f'💰 Total supply: {blockchain.get_total_supply():.2f} ZION')

# Start services
blockchain.start_p2p_network()
blockchain.start_rpc_server()

print('🌐 P2P Network started on port $P2P_PORT')
print('🔌 RPC Server started on port $BLOCKCHAIN_RPC_PORT')
print('📈 Blockchain node running. Press Ctrl+C to stop.')

try:
    while True:
        time.sleep(10)
        if len(blockchain.blocks) % 10 == 0:
            blockchain.print_status()
except KeyboardInterrupt:
    print('\\n🛑 Stopping blockchain node...')
    blockchain.stop_p2p_network() 
    blockchain.stop_rpc_server()
    print('✅ Blockchain node stopped')
"
EOF

# Mining pool script  
cat > "$LOCAL_DATA_DIR/scripts/start_mining_pool.sh" << 'EOF'
#!/bin/bash
source $(dirname $0)/../.env.local
cd /media/maitreya/ZION1

echo "⛏️  Starting ZION Mining Pool..."
echo "Stratum: stratum+tcp://$MINING_POOL_HOST:$MINING_POOL_PORT"
echo "API: http://$API_HOST:$API_PORT"

python3 -c "
import sys
import asyncio
sys.path.append('.')
from zion_universal_pool_v2 import ZionUniversalPool

async def run_pool():
    pool = ZionUniversalPool(port=$MINING_POOL_PORT)
    print('⛏️  ZION Mining Pool starting on port $MINING_POOL_PORT')
    print('🌐 API server will start on port $API_PORT')
    await pool.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(run_pool())
    except KeyboardInterrupt:
        print('\\n🛑 Mining pool stopped')
"
EOF

# Test connectivity script
cat > "$LOCAL_DATA_DIR/scripts/test_connectivity.sh" << 'EOF'
#!/bin/bash
source $(dirname $0)/../.env.local

echo "🧪 Testing ZION Local Stack Connectivity"
echo "======================================="

# Test RPC
echo "📡 Testing Blockchain RPC..."
if curl -s "http://$BLOCKCHAIN_RPC_HOST:$BLOCKCHAIN_RPC_PORT" >/dev/null; then
    echo "✅ Blockchain RPC responding"
else  
    echo "❌ Blockchain RPC not responding"
fi

# Test Pool API
echo "⛏️  Testing Mining Pool API..."
if curl -s "http://$MINING_POOL_HOST:$((MINING_POOL_PORT + 1))/api/stats" >/dev/null; then
    echo "✅ Mining Pool API responding"
else
    echo "❌ Mining Pool API not responding"  
fi

# Test P2P port
echo "🌐 Testing P2P port..."
if timeout 3 bash -c "</dev/tcp/$P2P_HOST/$P2P_PORT"; then
    echo "✅ P2P port open"
else
    echo "❌ P2P port closed"
fi

echo ""
echo "📊 Service URLs:"
echo "  Blockchain RPC: http://$BLOCKCHAIN_RPC_HOST:$BLOCKCHAIN_RPC_PORT"
echo "  Mining Pool: stratum+tcp://$MINING_POOL_HOST:$MINING_POOL_PORT" 
echo "  Pool API: http://$MINING_POOL_HOST:$((MINING_POOL_PORT + 1))"
echo "  P2P Network: $P2P_HOST:$P2P_PORT"
EOF

# Master start script
cat > "$LOCAL_DATA_DIR/scripts/start_all.sh" << 'EOF'
#!/bin/bash

echo "🚀 Starting Complete ZION 2.7.5 Local Stack"
echo "==========================================="

SCRIPT_DIR=$(dirname $0)
source "$SCRIPT_DIR/../.env.local"

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "new_zion_blockchain" 2>/dev/null || true
pkill -f "zion_universal_pool" 2>/dev/null || true
sleep 2

# Start services in correct order
echo ""
echo "1️⃣  Starting Blockchain Node..."
gnome-terminal --tab --title="ZION Blockchain" -- bash -c "cd '$SCRIPT_DIR' && bash start_blockchain.sh; exec bash"
sleep 5

echo "2️⃣  Starting Mining Pool..."
gnome-terminal --tab --title="ZION Mining Pool" -- bash -c "cd '$SCRIPT_DIR' && bash start_mining_pool.sh; exec bash"
sleep 3

echo "3️⃣  Testing connectivity..."
bash "$SCRIPT_DIR/test_connectivity.sh"

echo ""
echo "✅ ZION 2.7.5 Local Stack Started!"
echo ""
echo "📋 Service Overview:"
echo "  🔗 Blockchain: http://127.0.0.1:$BLOCKCHAIN_RPC_PORT"
echo "  ⛏️  Mining Pool: stratum+tcp://127.0.0.1:$MINING_POOL_PORT"
echo "  📊 Pool Stats: http://127.0.0.1:$((MINING_POOL_PORT + 1))/api/stats"
echo ""
echo "🔧 Test XMRig connection:"
echo "  xmrig --url 127.0.0.1:$MINING_POOL_PORT --user testWorker --algo rx/0"
EOF

# Stop script
cat > "$LOCAL_DATA_DIR/scripts/stop_all.sh" << 'EOF'
#!/bin/bash

echo "🛑 Stopping ZION 2.7.5 Local Stack"
echo "=================================="

# Kill all ZION processes
pkill -f "new_zion_blockchain" 2>/dev/null && echo "✅ Blockchain node stopped" || echo "ℹ️  No blockchain process found"
pkill -f "zion_universal_pool" 2>/dev/null && echo "✅ Mining pool stopped" || echo "ℹ️  No mining pool process found"

echo "✅ All ZION services stopped"
EOF

# Make scripts executable
chmod +x "$LOCAL_DATA_DIR/scripts"/*.sh

echo -e "${GREEN}✅ Spouštěcí skripty vytvořeny${NC}"

echo -e "${BLUE}🧪 Vytvářím test skripty...${NC}"

# Quick test script
cat > "$LOCAL_DATA_DIR/scripts/quick_test.sh" << 'EOF'
#!/bin/bash
source $(dirname $0)/../.env.local
cd /media/maitreya/ZION1

echo "🧪 ZION Quick Test"
echo "=================="

# Test import 
echo "📦 Testing imports..."
python3 -c "
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
from zion_universal_pool_v2 import ZionUniversalPool 
from zion_rpc_server import ZIONRPCServer
from zion_p2p_network import ZIONP2PNetwork
print('✅ All core modules imported successfully')
"

# Test blockchain creation
echo "🔗 Testing blockchain initialization..."
python3 -c "
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
blockchain = NewZionBlockchain(enable_p2p=False, enable_rpc=False)
print(f'✅ Blockchain created with {len(blockchain.blocks)} blocks')
print(f'💰 Total supply: {blockchain.get_total_supply():.2f} ZION')
"

echo "✅ Quick test completed successfully"
EOF

chmod +x "$LOCAL_DATA_DIR/scripts/quick_test.sh"

echo -e "${GREEN}✅ Test skripty vytvořeny${NC}"

echo -e "${BLUE}📚 Vytvářím dokumentaci...${NC}"

# Create README for local deployment
cat > "$LOCAL_DATA_DIR/README.md" << EOF
# ZION 2.7.5 Local Deployment

Lokální deployment ZION blockchain stacku pro vývoj a testování.

## 🚀 Rychlý start

\`\`\`bash
# Spustit celý stack
./scripts/start_all.sh

# Test konektivity
./scripts/test_connectivity.sh

# Zastavit všechny služby
./scripts/stop_all.sh
\`\`\`

## 🔧 Individuální služby

\`\`\`bash
# Pouze blockchain node
./scripts/start_blockchain.sh

# Pouze mining pool  
./scripts/start_mining_pool.sh

# Quick test
./scripts/quick_test.sh
\`\`\`

## 📊 Služby

| Služba | URL | Port |
|--------|-----|------|
| Blockchain RPC | http://127.0.0.1:8332 | 8332 |
| P2P Network | 127.0.0.1:8333 | 8333 |
| Mining Pool | stratum+tcp://127.0.0.1:3335 | 3335 |
| Pool API | http://127.0.0.1:3336 | 3336 |

## 🧪 Testování

### XMRig Test
\`\`\`bash
xmrig --url 127.0.0.1:3335 --user testWorker --algo rx/0 --keepalive
\`\`\`

### RPC Test
\`\`\`bash
curl http://127.0.0.1:8332/api/status
\`\`\`

### Pool Stats
\`\`\`bash
curl http://127.0.0.1:3336/api/stats  
\`\`\`

## 📁 Struktura

- \`data/\` - Runtime data
- \`db/\` - Database soubory
- \`logs/\` - Log soubory
- \`config/\` - Konfigurační soubory
- \`scripts/\` - Spouštěcí skripty

Generated: $(date)
EOF

echo -e "${GREEN}✅ Dokumentace vytvořena${NC}"

echo ""
echo -e "${GREEN}🎉 ZION 2.7.5 Local Deployment Setup Complete!${NC}"
echo ""
echo -e "${BLUE}📂 Deployment Path:${NC} $LOCAL_DATA_DIR"
echo -e "${BLUE}📚 Documentation:${NC} $LOCAL_DATA_DIR/README.md"
echo ""
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1️⃣  Run quick test: $LOCAL_DATA_DIR/scripts/quick_test.sh"
echo "2️⃣  Start full stack: $LOCAL_DATA_DIR/scripts/start_all.sh" 
echo "3️⃣  Test with XMRig: xmrig --url 127.0.0.1:3335 --user testWorker --algo rx/0"
echo ""
echo -e "${GREEN}Happy mining! ⛏️${NC}"