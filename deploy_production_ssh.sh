#!/usr/bin/env bash
#
# ZION 2.7.5 SSH Production Deployment Script
# Nasadí funkčního ZION stacku na produkční server
#
set -e

echo "🚀 ZION 2.7.5 SSH Production Deployment"
echo "======================================="

# Konfigurace serveru
SERVER_HOST="91.98.122.165"
SERVER_USER="root"
SERVER_PORT="22"
SERVER_PATH="/root/zion_production"

# Lokální konfigurace
LOCAL_ROOT="/Users/yeshuae/Desktop/ZION/Zion-TestNet-2.7.5-github"
VENV_PATH=""

# Production porty (odlišné od lokálních pro avoiding konfliktů)
PROD_BLOCKCHAIN_RPC_PORT=8332
PROD_P2P_PORT=8333
PROD_MINING_POOL_PORT=3335
PROD_API_PORT=3336

echo "🔍 Pre-deployment checks..."

# Check if we have essential files
if [ ! -f "new_zion_blockchain.py" ] || [ ! -f "zion_unified.py" ]; then
    echo "❌ Essential ZION files not found"
    exit 1
fi

# Test server connectivity
if ! ssh -o ConnectTimeout=5 "$SERVER_USER@$SERVER_HOST" "echo 'SSH OK'" >/dev/null 2>&1; then
    echo "❌ Cannot connect to server $SERVER_HOST"
    echo "💡 Check SSH keys and network connectivity"
    exit 1
fi

echo "✅ Pre-deployment checks passed"

echo ""
echo "📦 Preparing deployment package..."

# Create deployment package
DEPLOY_DIR="/tmp/zion_deployment_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$DEPLOY_DIR"

# Copy essential files
echo "📄 Copying core files..."
cp "$LOCAL_ROOT/new_zion_blockchain.py" "$DEPLOY_DIR/"
cp "$LOCAL_ROOT/zion_universal_pool_v2.py" "$DEPLOY_DIR/"
cp "$LOCAL_ROOT/zion_rpc_server.py" "$DEPLOY_DIR/"
cp "$LOCAL_ROOT/zion_p2p_network.py" "$DEPLOY_DIR/"
cp "$LOCAL_ROOT/crypto_utils.py" "$DEPLOY_DIR/"
cp "$LOCAL_ROOT/requirements.txt" "$DEPLOY_DIR/"

# Create production configuration
echo "⚙️  Creating production config..."
cat > "$DEPLOY_DIR/production_config.py" << EOF
#!/usr/bin/env python3
"""
ZION Production Configuration
"""

# Database paths
BLOCKCHAIN_DB_PATH = "/root/zion_production/data/zion_blockchain.db"
POOL_DB_PATH = "/root/zion_production/data/zion_pool.db"

# Network configuration
BLOCKCHAIN_RPC_HOST = "0.0.0.0"
BLOCKCHAIN_RPC_PORT = $PROD_BLOCKCHAIN_RPC_PORT
P2P_HOST = "0.0.0.0" 
P2P_PORT = $PROD_P2P_PORT
MINING_POOL_HOST = "0.0.0.0"
MINING_POOL_PORT = $PROD_MINING_POOL_PORT

# Production settings
ENVIRONMENT = "production"
LOG_LEVEL = "INFO"
DEBUG = False

# Pool configuration
POOL_ADDRESS = "ZION_SACRED_B0FA7E2A234D8C2F08545F02295C98"
POOL_FEE_PERCENT = 1.0
PAYOUT_THRESHOLD = 10.0

# Security (production)
RPC_REQUIRE_AUTH = True
RATE_LIMIT_ENABLED = True

EOF

# Create production startup script
echo "📝 Creating production scripts..."
cat > "$DEPLOY_DIR/start_production.sh" << 'EOF'
#!/bin/bash
#
# ZION Production Startup Script
#

set -e

PROD_DIR="/root/zion_production"
cd "$PROD_DIR"

echo "🚀 Starting ZION 2.7.5 Production Stack"
echo "======================================"

# Load production config
source production_config.sh

# Kill existing processes
echo "🧹 Cleaning up..."
pkill -f "new_zion_blockchain" 2>/dev/null || true
pkill -f "zion_universal_pool" 2>/dev/null || true
sleep 2

mkdir -p data logs

echo ""
echo "1️⃣  Starting Blockchain Node..."

# Start blockchain node
nohup python3 -c "
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
import time

print('🚀 ZION Production Blockchain Node')
blockchain = NewZionBlockchain(
    db_file='data/zion_blockchain.db',
    enable_p2p=True, 
    p2p_port=8333,
    enable_rpc=True,
    rpc_port=8332
)

print(f'📊 Block height: {len(blockchain.blocks)}')
print(f'💰 Total supply: {blockchain.get_total_supply():.2f} ZION')

# Start RPC only (P2P has event loop issues)
blockchain.start_rpc_server()
print('✅ RPC Server started on port 8332')
print('📈 Production node running...')

try:
    while True:
        time.sleep(60)
        print(f'📊 Height: {len(blockchain.blocks)}, Supply: {blockchain.get_total_supply():.2f}')
except KeyboardInterrupt:
    print('🛑 Stopping...')
    blockchain.stop_rpc_server()
" > logs/blockchain.log 2>&1 &

BLOCKCHAIN_PID=$!
echo "✅ Blockchain Node started (PID: $BLOCKCHAIN_PID)"

sleep 3

echo ""
echo "2️⃣  Starting Mining Pool..."

# Start mining pool
nohup python3 -c "
import sys
import asyncio
sys.path.append('.')
from zion_universal_pool_v2 import ZionUniversalPool

async def run_pool():
    print('⛏️  ZION Production Mining Pool')
    pool = ZionUniversalPool(port=3335)
    print('⛏️  Pool ready for miners on port 3335')
    print('📊 API available on port 3336')
    await pool.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(run_pool())
    except KeyboardInterrupt:
        print('🛑 Pool stopped')
" > logs/mining_pool.log 2>&1 &

MINING_POOL_PID=$!
echo "✅ Mining Pool started (PID: $MINING_POOL_PID)"

# Save PIDs for monitoring
echo "$BLOCKCHAIN_PID" > data/blockchain.pid
echo "$MINING_POOL_PID" > data/mining_pool.pid

sleep 3

echo ""
echo "✅ ZION Production Stack Running!"
echo ""
echo "📋 Process IDs:"
echo "  🔗 Blockchain: $BLOCKCHAIN_PID"
echo "  ⛏️  Mining Pool: $MINING_POOL_PID"
echo ""
echo "📊 External URLs:"
echo "  🔗 Blockchain RPC: http://91.98.122.165:8332"
echo "  ⛏️  Mining Pool: stratum+tcp://91.98.122.165:3335"
echo "  📊 Pool Stats: http://91.98.122.165:3336/api/stats"
echo ""
echo "📋 Logs:"
echo "  tail -f logs/blockchain.log"
echo "  tail -f logs/mining_pool.log"

EOF

# Create production stop script
cat > "$DEPLOY_DIR/stop_production.sh" << 'EOF'
#!/bin/bash
echo "🛑 Stopping ZION Production Stack"

PROD_DIR="/root/zion_production"

if [ -f "$PROD_DIR/data/blockchain.pid" ]; then
    BLOCKCHAIN_PID=$(cat "$PROD_DIR/data/blockchain.pid")
    kill $BLOCKCHAIN_PID 2>/dev/null && echo "✅ Blockchain stopped" || echo "ℹ️  Blockchain not running"
    rm -f "$PROD_DIR/data/blockchain.pid"
fi

if [ -f "$PROD_DIR/data/mining_pool.pid" ]; then
    MINING_POOL_PID=$(cat "$PROD_DIR/data/mining_pool.pid")
    kill $MINING_POOL_PID 2>/dev/null && echo "✅ Mining pool stopped" || echo "ℹ️  Mining pool not running"
    rm -f "$PROD_DIR/data/mining_pool.pid"
fi

# Fallback cleanup
pkill -f "new_zion_blockchain" 2>/dev/null || true
pkill -f "zion_universal_pool" 2>/dev/null || true

echo "✅ All ZION services stopped"
EOF

# Create monitoring script
cat > "$DEPLOY_DIR/monitor_production.sh" << 'EOF'
#!/bin/bash
echo "📊 ZION Production Monitor"
echo "========================"

# Check processes
if pgrep -f "new_zion_blockchain" > /dev/null; then
    echo "✅ Blockchain node running"
else
    echo "❌ Blockchain node stopped"
fi

if pgrep -f "zion_universal_pool" > /dev/null; then
    echo "✅ Mining pool running"
else
    echo "❌ Mining pool stopped"
fi

# Check ports
echo ""
echo "🌐 Port Status:"
netstat -tlnp | grep -E "(8332|3335|3336)" || echo "No ZION ports open"

# Recent logs
echo ""
echo "📋 Recent Activity:"
echo "--- Blockchain (last 3 lines) ---"
tail -n 3 /root/zion_production/logs/blockchain.log 2>/dev/null || echo "No blockchain logs"

echo "--- Mining Pool (last 3 lines) ---"
tail -n 3 /root/zion_production/logs/mining_pool.log 2>/dev/null || echo "No pool logs"

# API test
echo ""
echo "🧪 API Test:"
curl -s http://127.0.0.1:3336/api/stats | head -5 2>/dev/null || echo "API not responding"
EOF

chmod +x "$DEPLOY_DIR"/*.sh

echo "✅ Deployment package prepared"

echo ""
echo "📤 Uploading to server..."

# Upload deployment package
scp -r "$DEPLOY_DIR" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH" || {
    echo "❌ Upload failed"
    exit 1
}

echo "✅ Upload completed"

echo ""
echo "⚙️  Setting up production environment..."

# Setup on server
ssh "$SERVER_USER@$SERVER_HOST" << REMOTE_SETUP
set -e

cd "$SERVER_PATH"
echo "📂 Production directory: \$PWD"

# Install Python dependencies
echo "🐍 Installing dependencies..."
apt-get update -qq
apt-get install -y python3 python3-pip python3-venv curl netstat-nat

# Create virtual environment
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install ecdsa==0.19.0

# Set up firewall if needed
echo "🔥 Configuring firewall..."
ufw allow 8332/tcp comment "ZION RPC"
ufw allow 3335/tcp comment "ZION Mining Pool"  
ufw allow 3336/tcp comment "ZION Pool API"

echo "✅ Production environment ready"

REMOTE_SETUP

echo "✅ Server setup completed"

echo ""
echo "🚀 Starting production services..."

# Start production services
ssh "$SERVER_USER@$SERVER_HOST" "cd $SERVER_PATH && source venv/bin/activate && bash start_production.sh"

echo ""
echo "🧪 Testing production deployment..."

# Wait for services to start
sleep 5

# Test external connectivity
echo -n "📡 Testing Pool API: "
if curl -s "http://$SERVER_HOST:$PROD_API_PORT/api/stats" >/dev/null; then
    echo "✅ Responding"
else
    echo "❌ Not responding"
fi

# Test mining connection
echo -n "⛏️  Testing Mining Port: "
if timeout 5 bash -c "</dev/tcp/$SERVER_HOST/$PROD_MINING_POOL_PORT" 2>/dev/null; then
    echo "✅ Port open"
else
    echo "❌ Port closed"
fi

echo ""
echo "🎉 ZION 2.7.5 Production Deployment Complete!"
echo ""
echo "📊 Production URLs:"
echo "  🔗 Blockchain RPC: http://$SERVER_HOST:$PROD_BLOCKCHAIN_RPC_PORT"
echo "  ⛏️  Mining Pool: stratum+tcp://$SERVER_HOST:$PROD_MINING_POOL_PORT"
echo "  📊 Pool Stats: http://$SERVER_HOST:$PROD_API_PORT/api/stats"
echo ""
echo "🧪 Test mining:"
echo "  xmrig --url $SERVER_HOST:$PROD_MINING_POOL_PORT --user productionMiner --algo rx/0"
echo ""
echo "📋 Server management:"
echo "  ssh $SERVER_USER@$SERVER_HOST"
echo "  cd $SERVER_PATH"
echo "  bash monitor_production.sh"
echo "  bash stop_production.sh"
echo ""
echo "🗑️  Cleanup local deployment package:"
echo "  rm -rf $DEPLOY_DIR"

# Cleanup
rm -rf "$DEPLOY_DIR"