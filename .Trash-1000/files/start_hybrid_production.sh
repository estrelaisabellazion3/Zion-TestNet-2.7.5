#!/bin/bash
#
# ZION Production Hybrid - Based on 2.7.1 Best Practices
# No P2P complexity, stable standalone node
#

set -e

PROD_DIR="/root/zion_production"
cd "$PROD_DIR"

echo "🌟 Starting ZION 2.7.5 Hybrid Production Stack"
echo "==============================================="
echo "Based on ZION 2.7.1 stability improvements"

# Cleanup existing processes  
echo "🧹 Cleaning up..."
pkill -f "zion_blockchain" 2>/dev/null || true
pkill -f "zion_pool" 2>/dev/null || true
sleep 2

mkdir -p data logs

echo ""
echo "1️⃣ Starting Standalone Blockchain Node (No P2P)..."

# Create stable blockchain wrapper - inspired by 2.7.1
cat > blockchain_standalone.py << 'EOF'
#!/usr/bin/env python3
"""
ZION 2.7.5 Standalone Blockchain Node
Inspired by 2.7.1 stability approach - No P2P complications
"""
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info('🌟 Starting ZION 2.7.5 Standalone Node')
    
    # Create blockchain with stable config - NO P2P!
    blockchain = NewZionBlockchain(
        db_file='data/zion_blockchain.db',
        enable_p2p=False,  # Disable P2P for stability - key lesson from 2.7.1
        enable_rpc=True,
        rpc_port=8332
    )
    
    logger.info(f'📊 Block height: {len(blockchain.blocks)}')
    logger.info(f'💰 Total supply: {blockchain.get_total_supply():.2f} ZION')
    
    # Start RPC server
    blockchain.start_rpc_server()
    logger.info('✅ RPC Server started on port 8332')
    logger.info('🚀 Standalone node running (P2P disabled for stability)')
    
    try:
        while True:
            time.sleep(60)
            logger.info(f'⏰ Height: {len(blockchain.blocks)}, Supply: {blockchain.get_total_supply():.2f} ZION')
    except KeyboardInterrupt:
        logger.info('🛑 Stopping standalone node...')
        blockchain.stop_rpc_server()
        logger.info('✅ Node stopped cleanly')

if __name__ == '__main__':
    main()
EOF

nohup bash -c "source venv/bin/activate && python3 blockchain_standalone.py" > logs/blockchain.log 2>&1 &
BLOCKCHAIN_PID=$!
echo "✅ Standalone Blockchain started (PID: $BLOCKCHAIN_PID)"

sleep 3

echo ""
echo "2️⃣ Starting Enhanced Mining Pool..."

# Create enhanced pool wrapper - inspired by 2.7.1 
cat > pool_enhanced.py << 'EOF'
#!/usr/bin/env python3
"""
ZION 2.7.5 Enhanced Mining Pool  
Inspired by 2.7.1 consciousness-based approach
"""
import sys
import asyncio
sys.path.append('.')
from zion_universal_pool_v2 import ZionUniversalPool
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def main():
    logger.info('⛏️ Starting ZION 2.7.5 Enhanced Pool')
    
    pool = ZionUniversalPool(port=3335)
    logger.info('✅ Pool instance created with algorithms:')
    for algo, diff in pool.difficulty.items():
        reward = pool.eco_rewards.get(algo, 1.0)
        logger.info(f'   - {algo}: difficulty={diff}, eco_reward={reward:.2f}x')
    
    logger.info('🌐 Pool ready on port 3335 (stratum)')
    logger.info('📊 API ready on port 3336 (stats)')
    
    await pool.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('🛑 Pool stopped')
EOF

nohup bash -c "source venv/bin/activate && python3 pool_enhanced.py" > logs/mining_pool.log 2>&1 &
POOL_PID=$!
echo "✅ Enhanced Pool started (PID: $POOL_PID)"

# Save PIDs
echo "$BLOCKCHAIN_PID" > data/blockchain.pid
echo "$POOL_PID" > data/pool.pid

sleep 3

echo ""
echo "🎉 ZION 2.7.5 Hybrid Production Stack Running!"
echo ""
echo "📊 Configuration:"
echo "  - Blockchain: Standalone (No P2P complexity)"  
echo "  - RPC: Active on port 8332"
echo "  - Mining: RandomX, YesCrypt, Autolykos v2"
echo "  - Pool: Port 3335 (stratum)"
echo "  - API: Port 3336 (stats)"
echo ""
echo "🔌 External Access:"
echo "  - RPC: http://91.98.122.165:8332" 
echo "  - Pool: stratum+tcp://91.98.122.165:3335"
echo "  - Stats: http://91.98.122.165:3336/api/stats"
echo ""
echo "📋 Process IDs:"
echo "  - Blockchain: $BLOCKCHAIN_PID"
echo "  - Pool: $POOL_PID"
echo ""
echo "📜 Logs:"
echo "  - tail -f logs/blockchain.log"
echo "  - tail -f logs/mining_pool.log"