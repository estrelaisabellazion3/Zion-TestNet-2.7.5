#!/usr/bin/env python3
"""
ZION 2.7.5 Unified System Integrator
Propojuje všechny komponenty do jediného funkčního celku
"""

import os
import sys
import time
import threading
import logging
from typing import Optional, Dict, Any

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import existing ZION 2.7.5 components
try:
    from new_zion_blockchain import NewZionBlockchain
    from zion_universal_pool_v2 import ZionUniversalPool
    from seednodes import ZionNetworkConfig, get_premine_addresses
    MAIN_BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Main blockchain components not available: {e}")
    MAIN_BLOCKCHAIN_AVAILABLE = False
    # Fallback for config
    class FallbackConfig:
        POOL_CONFIG = {'stratum_port': 3335}
        PORTS = {'rpc_mainnet': 8332, 'p2p_mainnet': 8333}
    ZionNetworkConfig = FallbackConfig()

# Import 2.7.1 real blockchain if available
try:
    from core.real_blockchain import ZionRealBlockchain
    REAL_BLOCKCHAIN_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Real blockchain from 2.7.1 not available: {e}")
    REAL_BLOCKCHAIN_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZionUnifiedSystem:
    """Unified ZION system integrating all components"""
    
    def __init__(self, use_real_blockchain=True, enable_p2p=True, enable_rpc=True, enable_mining_pool=True):
        self.use_real_blockchain = use_real_blockchain and REAL_BLOCKCHAIN_AVAILABLE
        self.enable_p2p = enable_p2p
        self.enable_rpc = enable_rpc
        self.enable_mining_pool = enable_mining_pool
        
        # Component instances
        self.blockchain = None
        self.mining_pool = None
        self.running = False
        
        # Configuration from centralized seednodes
        self.config = ZionNetworkConfig
        
        logger.info("🚀 ZION 2.7.5 Unified System Initializing...")
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        
        # 1. Initialize Blockchain (choose best available implementation)
        if self.use_real_blockchain and REAL_BLOCKCHAIN_AVAILABLE:
            logger.info("🌟 Using Real Blockchain implementation from 2.7.1")
            db_path = os.path.join(os.path.dirname(__file__), 'zion_unified_blockchain.db')
            self.blockchain = ZionRealBlockchain(db_file=db_path)
            self.blockchain_type = "real_2.7.1"
        elif MAIN_BLOCKCHAIN_AVAILABLE:
            logger.info("🔗 Using Main Blockchain implementation from 2.7.5")
            self.blockchain = NewZionBlockchain(
                db_file='data/zion_unified_blockchain.db',
                enable_p2p=self.enable_p2p,
                enable_rpc=self.enable_rpc
            )
            self.blockchain_type = "main_2.7.5"
        else:
            raise Exception("❌ No blockchain implementation available!")
        
        # 2. Initialize Mining Pool (if enabled)
        if self.enable_mining_pool and MAIN_BLOCKCHAIN_AVAILABLE:
            logger.info("⛏️ Initializing Universal Mining Pool...")
            self.mining_pool = ZionUniversalPool(port=self.config.POOL_CONFIG['stratum_port'])
            # Connect pool to blockchain
            if hasattr(self.mining_pool, 'blockchain'):
                if self.blockchain_type == "main_2.7.5":
                    self.mining_pool.blockchain = self.blockchain
                else:
                    # Create bridge for real blockchain
                    logger.info("🌉 Creating blockchain bridge for mining pool")
                    self.mining_pool.blockchain = self._create_blockchain_bridge()
        
        logger.info("✅ All components initialized successfully")
    
    def _create_blockchain_bridge(self):
        """Create a bridge between real blockchain and mining pool expectations"""
        class BlockchainBridge:
            def __init__(self, real_blockchain):
                self.real_bc = real_blockchain
            
            @property 
            def blocks(self):
                """Convert real blockchain blocks to expected format"""
                if hasattr(self.real_bc, 'get_all_blocks'):
                    return self.real_bc.get_all_blocks()
                return []
            
            def get_total_supply(self):
                if hasattr(self.real_bc, 'get_blockchain_stats'):
                    stats = self.real_bc.get_blockchain_stats()
                    return stats.get('total_supply', 0)
                return 0
            
            def mine_block(self, miner_address, **kwargs):
                if hasattr(self.real_bc, 'mine_block'):
                    return self.real_bc.mine_block(miner_address=miner_address, **kwargs)
                return None
        
        return BlockchainBridge(self.blockchain)
    
    def start_system(self):
        """Start all system components"""
        if self.running:
            logger.warning("⚠️ System already running")
            return
        
        self.running = True
        logger.info("🚀 Starting ZION Unified System...")
        
        # Start blockchain services
        if self.blockchain_type == "main_2.7.5":
            if self.enable_p2p and hasattr(self.blockchain, 'start_p2p_network'):
                try:
                    self.blockchain.start_p2p_network()
                    logger.info("🌐 P2P Network started")
                except Exception as e:
                    logger.warning(f"⚠️ P2P Network failed to start: {e}")
            
            if self.enable_rpc and hasattr(self.blockchain, 'start_rpc_server'):
                try:
                    self.blockchain.start_rpc_server()
                    logger.info("🔌 RPC Server started")
                except Exception as e:
                    logger.warning(f"⚠️ RPC Server failed to start: {e}")
        
        # Start mining pool
        if self.mining_pool and self.enable_mining_pool:
            try:
                # Start mining pool in background thread
                pool_thread = threading.Thread(target=self._start_mining_pool, daemon=True)
                pool_thread.start()
                logger.info("⛏️ Mining Pool started")
            except Exception as e:
                logger.warning(f"⚠️ Mining Pool failed to start: {e}")
        
        logger.info("✅ ZION Unified System fully operational!")
        self._print_system_status()
    
    def _start_mining_pool(self):
        """Start mining pool in async context"""
        import asyncio
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.mining_pool.start_server())
        except Exception as e:
            logger.error(f"❌ Mining pool error: {e}")
    
    def stop_system(self):
        """Stop all system components"""
        if not self.running:
            return
        
        logger.info("🛑 Stopping ZION Unified System...")
        self.running = False
        
        # Stop blockchain services
        if self.blockchain_type == "main_2.7.5":
            if hasattr(self.blockchain, 'stop_p2p_network'):
                self.blockchain.stop_p2p_network()
            if hasattr(self.blockchain, 'stop_rpc_server'):
                self.blockchain.stop_rpc_server()
        
        logger.info("✅ ZION Unified System stopped")
    
    def _print_system_status(self):
        """Print current system status"""
        print("\n" + "="*60)
        print("🌟 ZION 2.7.5 UNIFIED SYSTEM STATUS")
        print("="*60)
        
        # Blockchain status
        if self.blockchain:
            if self.blockchain_type == "real_2.7.1":
                if hasattr(self.blockchain, 'get_block_count'):
                    block_count = self.blockchain.get_block_count()
                    print(f"🔗 Blockchain: Real 2.7.1 Implementation ({block_count} blocks)")
                else:
                    print(f"🔗 Blockchain: Real 2.7.1 Implementation")
            else:
                block_count = len(self.blockchain.blocks) if hasattr(self.blockchain, 'blocks') else 0
                total_supply = self.blockchain.get_total_supply() if hasattr(self.blockchain, 'get_total_supply') else 0
                print(f"🔗 Blockchain: Main 2.7.5 Implementation ({block_count} blocks)")
                print(f"💰 Total Supply: {total_supply:,.0f} ZION")
        
        # Network status
        rpc_port = self.config.PORTS.get('rpc_mainnet', 8332)
        p2p_port = self.config.PORTS.get('p2p_mainnet', 8333)
        pool_port = self.config.POOL_CONFIG.get('stratum_port', 3335)
        
        if self.enable_rpc:
            print(f"🔌 RPC Server: http://localhost:{rpc_port}")
        if self.enable_p2p:
            print(f"🌐 P2P Network: localhost:{p2p_port}")
        if self.enable_mining_pool:
            print(f"⛏️ Mining Pool: stratum://localhost:{pool_port}")
        
        # Component status
        print(f"\n📊 System Components:")
        print(f"   Real Blockchain (2.7.1): {'✅' if REAL_BLOCKCHAIN_AVAILABLE else '❌'}")
        print(f"   Main Blockchain (2.7.5): {'✅' if MAIN_BLOCKCHAIN_AVAILABLE else '❌'}")
        print(f"   Mining Pool: {'✅' if self.mining_pool else '❌'}")
        print(f"   P2P Network: {'✅' if self.enable_p2p else '❌'}")
        print(f"   RPC Server: {'✅' if self.enable_rpc else '❌'}")
        
        print("="*60)
        print("🎯 Use 'python zion_unified.py --help' for CLI options")
        print("🎯 Use 'python zion_simple_cli.py stats' for blockchain stats") 
        print("="*60 + "\n")
    
    def get_system_stats(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        stats = {
            'system': {
                'running': self.running,
                'blockchain_type': self.blockchain_type if self.blockchain else None,
                'components': {
                    'blockchain': bool(self.blockchain),
                    'mining_pool': bool(self.mining_pool),
                    'p2p_enabled': self.enable_p2p,
                    'rpc_enabled': self.enable_rpc
                }
            }
        }
        
        # Add blockchain stats
        if self.blockchain:
            if self.blockchain_type == "real_2.7.1":
                if hasattr(self.blockchain, 'get_blockchain_stats'):
                    stats['blockchain'] = self.blockchain.get_blockchain_stats()
            else:
                stats['blockchain'] = {
                    'height': len(self.blockchain.blocks) if hasattr(self.blockchain, 'blocks') else 0,
                    'total_supply': self.blockchain.get_total_supply() if hasattr(self.blockchain, 'get_total_supply') else 0
                }
        
        return stats

def main():
    """Main entry point for unified system"""
    import argparse
    
    parser = argparse.ArgumentParser(description='ZION 2.7.5 Unified System')
    parser.add_argument('--no-p2p', action='store_true', help='Disable P2P network')
    parser.add_argument('--no-rpc', action='store_true', help='Disable RPC server')
    parser.add_argument('--no-pool', action='store_true', help='Disable mining pool')
    parser.add_argument('--use-main-blockchain', action='store_true', help='Force use main 2.7.5 blockchain')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    # Create unified system
    system = ZionUnifiedSystem(
        use_real_blockchain=not args.use_main_blockchain,
        enable_p2p=not args.no_p2p,
        enable_rpc=not args.no_rpc,
        enable_mining_pool=not args.no_pool
    )
    
    try:
        # Start system
        system.start_system()
        
        if args.daemon:
            logger.info("🔄 Running in daemon mode...")
            while system.running:
                time.sleep(60)
                # Optional: periodic status updates
                stats = system.get_system_stats()
                logger.info(f"📊 System heartbeat: {stats['system']['components']}")
        else:
            # Interactive mode
            print("\n🎯 ZION Unified System is running!")
            print("   Press Ctrl+C to stop...")
            while system.running:
                time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
    except Exception as e:
        logger.error(f"❌ System error: {e}")
    finally:
        system.stop_system()

if __name__ == "__main__":
    main()