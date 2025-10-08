#!/usr/bin/env python3
"""
ZION System Health Check
Tests all critical imports and basic functionality
"""

import sys
import os

def test_dependencies():
    """Test that all required dependencies are installed"""
    print("🔍 Testing Dependencies...")
    print("=" * 60)
    
    dependencies = {
        'numpy': 'Numerical computing',
        'pandas': 'Data analysis',
        'sklearn': 'Machine learning',
        'psutil': 'System monitoring',
        'GPUtil': 'GPU monitoring',
        'ecdsa': 'Cryptography',
        'requests': 'HTTP client',
        'aiohttp': 'Async HTTP',
        'argon2': 'ASIC-resistant hashing',
        'cryptography': 'Advanced crypto',
        'fastapi': 'Web framework',
    }
    
    passed = 0
    failed = 0
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {module:<20} - {description}")
            passed += 1
        except ImportError as e:
            print(f"❌ {module:<20} - {description} (MISSING)")
            failed += 1
    
    print(f"\nDependencies: {passed}/{passed+failed} passed")
    return failed == 0

def test_core_modules():
    """Test that core blockchain modules work"""
    print("\n🔧 Testing Core Modules...")
    print("=" * 60)
    
    modules = [
        ('new_zion_blockchain', 'Main blockchain'),
        ('zion_rpc_server', 'RPC server'),
        ('zion_p2p_network', 'P2P network'),
        ('crypto_utils', 'Cryptography utils'),
        ('seednodes', 'Network configuration'),
    ]
    
    passed = 0
    failed = 0
    
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {module:<25} - {description}")
            passed += 1
        except Exception as e:
            print(f"❌ {module:<25} - {description} ({type(e).__name__})")
            failed += 1
    
    print(f"\nCore Modules: {passed}/{passed+failed} passed")
    return failed == 0

def test_ai_modules():
    """Test that AI modules work"""
    print("\n🧠 Testing AI Modules...")
    print("=" * 60)
    
    modules = [
        ('ai.zion_predictive_maintenance', 'Predictive maintenance'),
        ('ai.zion_blockchain_analytics', 'Blockchain analytics'),
        ('ai.zion_security_monitor', 'Security monitor'),
        ('ai.zion_gpu_miner', 'GPU miner'),
        ('ai.zion_ai_master_orchestrator', 'AI orchestrator'),
    ]
    
    passed = 0
    failed = 0
    
    for module, description in modules:
        try:
            __import__(module)
            print(f"✅ {module:<40} - {description}")
            passed += 1
        except Exception as e:
            print(f"❌ {module:<40} - {description} ({type(e).__name__})")
            failed += 1
    
    print(f"\nAI Modules: {passed}/{passed+failed} passed")
    return failed == 0

def test_blockchain_initialization():
    """Test that blockchain can be initialized"""
    print("\n⛓️  Testing Blockchain Initialization...")
    print("=" * 60)
    
    try:
        from new_zion_blockchain import NewZionBlockchain
        
        # Create blockchain without P2P/RPC to avoid port conflicts
        blockchain = NewZionBlockchain(enable_p2p=False, enable_rpc=False)
        
        print(f"✅ Blockchain initialized")
        print(f"   Database: {blockchain.db_file}")
        print(f"   Blocks: {len(blockchain.blocks)}")
        print(f"   Difficulty: {blockchain.mining_difficulty}")
        print(f"   Block reward: {blockchain.block_reward}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to initialize blockchain: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all health checks"""
    print("\n" + "=" * 60)
    print("🚀 ZION 2.7.5 System Health Check")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Dependencies", test_dependencies()))
    results.append(("Core Modules", test_core_modules()))
    results.append(("AI Modules", test_ai_modules()))
    results.append(("Blockchain Init", test_blockchain_initialization()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:<20} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 All health checks PASSED!")
        print("✅ System is ready to use")
        return 0
    else:
        print("⚠️  Some health checks FAILED")
        print("❌ Please review the errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())
