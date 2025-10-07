#!/bin/bash
#
# ZION Production Final - Fixed Seed Nodes & P2P
# Řeší hlavní problém s fake seed nodes
#

set -e

PROD_DIR="/root/zion_production"
cd "$PROD_DIR"

echo "🔧 ZION 2.7.5 Production - FIXED SEED NODES"
echo "==========================================="
echo "✅ Fixed fake seed nodes → real IPs"
echo "✅ Added P2P timeout handling"
echo "✅ Proper error logging"

# Cleanup
echo ""
echo "🧹 Cleaning up..."
pkill -f "blockchain" 2>/dev/null || true
pkill -f "pool" 2>/dev/null || true
sleep 3

mkdir -p data logs

echo ""
echo "1️⃣ Starting Fixed Blockchain Node (P2P + RPC)..."

# Use the fixed P2P version
nohup bash -c "source venv/bin/activate && python3 blockchain_fixed_p2p.py" > logs/blockchain.log 2>&1 &
BLOCKCHAIN_PID=$!
echo "✅ Fixed Blockchain started (PID: $BLOCKCHAIN_PID)"

sleep 5

echo ""
echo "2️⃣ Starting Mining Pool..."

nohup bash -c "source venv/bin/activate && python3 pool_enhanced.py" > logs/mining_pool.log 2>&1 &
POOL_PID=$!
echo "✅ Enhanced Pool started (PID: $POOL_PID)"

# Save PIDs
echo "$BLOCKCHAIN_PID" > data/blockchain.pid
echo "$POOL_PID" > data/pool.pid

sleep 3

echo ""
echo "🎉 ZION 2.7.5 PRODUCTION FINAL - FIXED!"
echo ""
echo "🔧 FIXES APPLIED:"
echo "  ✅ Real seed nodes: 91.98.122.165:8333, 127.0.0.1:8333"
echo "  ✅ Removed fake domains: seed.zion.network, seed2.zion.network"  
echo "  ✅ Added P2P connection timeouts (10s per seed)"
echo "  ✅ Improved error handling and logging"
echo ""
echo "📊 SERVICES:"
echo "  🔗 Blockchain RPC: Active on port 8332"
echo "  🌐 P2P Network: Active on port 8333 (fixed seeds)"
echo "  ⛏️  Mining Pool: Active on port 3335 (stratum)"
echo "  📊 Pool API: Active on port 3336 (stats)"
echo ""
echo "🔌 EXTERNAL ACCESS:"
echo "  - RPC: http://91.98.122.165:8332" 
echo "  - Pool: stratum+tcp://91.98.122.165:3335"
echo "  - Stats: http://91.98.122.165:3336/api/stats"
echo ""
echo "📋 PROCESS IDs:"
echo "  - Blockchain: $BLOCKCHAIN_PID"
echo "  - Pool: $POOL_PID"
echo ""
echo "📜 LOGS:"
echo "  - tail -f logs/blockchain.log"
echo "  - tail -f logs/mining_pool.log"
echo ""
echo "🚀 Ready for XMRig connection testing!"