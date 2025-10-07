#!/bin/bash
#
# ZION Production Startup Script - Simple Version
#

set -e

PROD_DIR="/root/zion_production"
cd "$PROD_DIR"

echo "Starting ZION 2.7.5 Production Stack"
echo "===================================="

# Kill existing processes
echo "Cleaning up..."
pkill -f "new_zion_blockchain" 2>/dev/null || true
pkill -f "zion_universal_pool" 2>/dev/null || true
sleep 2

mkdir -p data logs

echo ""
echo "Starting Blockchain Node..."

# Start blockchain node with simple wrapper
cat > run_blockchain.py << 'EOF'
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
import time

print('ZION Production Blockchain Node')
blockchain = NewZionBlockchain(
    db_file='data/zion_blockchain.db',
    enable_p2p=True, 
    p2p_port=8333,
    enable_rpc=True,
    rpc_port=8332
)

print(f'Block height: {len(blockchain.blocks)}')
print(f'Total supply: {blockchain.get_total_supply():.2f} ZION')

blockchain.start_rpc_server()
print('RPC Server started on port 8332')
print('Production node running...')

try:
    while True:
        time.sleep(60)
        print(f'Height: {len(blockchain.blocks)}, Supply: {blockchain.get_total_supply():.2f}')
except KeyboardInterrupt:
    print('Stopping...')
    blockchain.stop_rpc_server()
EOF

nohup bash -c "source venv/bin/activate && python3 run_blockchain.py" > logs/blockchain.log 2>&1 &
BLOCKCHAIN_PID=$!
echo "Blockchain Node started (PID: $BLOCKCHAIN_PID)"

sleep 3

echo ""
echo "Starting Mining Pool..."

# Start mining pool with simple wrapper  
cat > run_pool.py << 'EOF'
import sys
import asyncio
sys.path.append('.')
from zion_universal_pool_v2 import ZionUniversalPool

async def run_pool():
    print('ZION Production Mining Pool')
    pool = ZionUniversalPool(port=3335)
    print('Pool ready for miners on port 3335')
    print('API available on port 3336')
    await pool.start_server()

if __name__ == '__main__':
    try:
        asyncio.run(run_pool())
    except KeyboardInterrupt:
        print('Pool stopped')
EOF

nohup bash -c "source venv/bin/activate && python3 run_pool.py" > logs/mining_pool.log 2>&1 &
MINING_POOL_PID=$!
echo "Mining Pool started (PID: $MINING_POOL_PID)"

# Save PIDs for monitoring
echo "$BLOCKCHAIN_PID" > data/blockchain.pid
echo "$MINING_POOL_PID" > data/mining_pool.pid

sleep 3

echo ""
echo "ZION Production Stack Running!"
echo ""
echo "Process IDs:"
echo "  Blockchain: $BLOCKCHAIN_PID"
echo "  Mining Pool: $MINING_POOL_PID"
echo ""
echo "External URLs:"
echo "  Blockchain RPC: http://91.98.122.165:8332"
echo "  Mining Pool: stratum+tcp://91.98.122.165:3335"
echo "  Pool Stats: http://91.98.122.165:3336/api/stats"
echo ""
echo "Logs:"
echo "  tail -f logs/blockchain.log"
echo "  tail -f logs/mining_pool.log"