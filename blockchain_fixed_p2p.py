#!/usr/bin/env python3
"""
ZION 2.7.5 Production Blockchain Node with Fixed P2P
Fixed seed nodes issue - real IPs instead of fake domains
"""
import sys
sys.path.append('.')
from new_zion_blockchain import NewZionBlockchain
import time
import logging
import asyncio

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    logger.info('🌟 Starting ZION 2.7.5 Production Node with Fixed P2P')
    
    try:
        # Create blockchain with FIXED P2P (real seed nodes)
        blockchain = NewZionBlockchain(
            db_file='data/zion_blockchain.db',
            enable_p2p=True,   # Enable P2P with FIXED seed nodes
            p2p_port=8333,
            enable_rpc=True,
            rpc_port=8332
        )
        
        logger.info(f'📊 Block height: {len(blockchain.blocks)}')
        logger.info(f'💰 Total supply: {blockchain.get_total_supply():.2f} ZION')
        
        # Start RPC server
        blockchain.start_rpc_server()
        logger.info('✅ RPC Server started on port 8332')
        logger.info('🌐 P2P enabled with fixed seed nodes (real IPs)')
        logger.info('🚀 Production node running...')
        
        # Main loop
        while True:
            time.sleep(60)
            peer_count = len(blockchain.p2p_network.peers) if blockchain.p2p_network else 0
            logger.info(f'⏰ Height: {len(blockchain.blocks)}, Supply: {blockchain.get_total_supply():.2f} ZION, Peers: {peer_count}')
            
    except KeyboardInterrupt:
        logger.info('🛑 Stopping production node...')
        if blockchain:
            blockchain.stop_rpc_server()
            if blockchain.p2p_network:
                # Stop P2P network gracefully
                try:
                    asyncio.run(blockchain.p2p_network.stop())
                except:
                    pass
        logger.info('✅ Node stopped cleanly')
    except Exception as e:
        logger.error(f'❌ Critical error: {e}')
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == '__main__':
    main()