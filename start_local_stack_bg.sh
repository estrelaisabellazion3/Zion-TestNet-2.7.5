#!/bin/bash

echo "🚀 Starting Complete ZION 2.7.5 Local Stack (Background)"
echo "======================================================="

SCRIPT_DIR=$(dirname $0)
source "$SCRIPT_DIR/../.env.local"

# Kill existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "new_zion_blockchain" 2>/dev/null || true
pkill -f "zion_universal_pool" 2>/dev/null || true
sleep 2

echo ""
echo "1️⃣  Starting Blockchain Node in background..."
cd /media/maitreya/ZION1
source /home/maitreya/zion_local_deployment/venv/bin/activate

# Start blockchain node in background
bash /home/maitreya/zion_local_deployment/scripts/start_blockchain.sh > /home/maitreya/zion_local_deployment/logs/blockchain.log 2>&1 &
BLOCKCHAIN_PID=$!
echo "🔗 Blockchain PID: $BLOCKCHAIN_PID"
sleep 5

echo ""
echo "2️⃣  Starting Mining Pool in background..."
bash /home/maitreya/zion_local_deployment/scripts/start_mining_pool.sh > /home/maitreya/zion_local_deployment/logs/mining_pool.log 2>&1 &
MINING_POOL_PID=$!
echo "⛏️  Mining Pool PID: $MINING_POOL_PID"
sleep 3

echo ""
echo "3️⃣  Testing connectivity..."
bash "$SCRIPT_DIR/test_connectivity.sh"

echo ""
echo "✅ ZION 2.7.5 Local Stack Started!"
echo ""
echo "📋 Service PIDs:"
echo "  🔗 Blockchain: $BLOCKCHAIN_PID"
echo "  ⛏️  Mining Pool: $MINING_POOL_PID"
echo ""
echo "📊 Service URLs:"
echo "  🔗 Blockchain: http://127.0.0.1:$BLOCKCHAIN_RPC_PORT"
echo "  ⛏️  Mining Pool: stratum+tcp://127.0.0.1:$MINING_POOL_PORT"
echo "  📊 Pool Stats: http://127.0.0.1:$((MINING_POOL_PORT + 1))/api/stats"
echo ""
echo "📋 Logs:"
echo "  🔗 Blockchain: tail -f /home/maitreya/zion_local_deployment/logs/blockchain.log"
echo "  ⛏️  Mining Pool: tail -f /home/maitreya/zion_local_deployment/logs/mining_pool.log"
echo ""
echo "🔧 Test XMRig connection:"
echo "  xmrig --url 127.0.0.1:$MINING_POOL_PORT --user testWorker --algo rx/0"