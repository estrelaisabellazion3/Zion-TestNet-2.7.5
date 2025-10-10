#!/usr/bin/env python3
"""
ZION SSH Dashboard - Quick Test Script
Verifies all dependencies and components are working
"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("🧪 Testing Python imports...")
    
    tests = {
        'tkinter': 'GUI framework',
        'paramiko': 'SSH connection',
        'psutil': 'System monitoring',
        'json': 'JSON handling',
        'threading': 'Multi-threading',
        'datetime': 'Time functions'
    }
    
    passed = 0
    failed = 0
    
    for module, description in tests.items():
        try:
            __import__(module)
            print(f"  ✅ {module:15} - {description}")
            passed += 1
        except ImportError as e:
            print(f"  ❌ {module:15} - {description} - ERROR: {e}")
            failed += 1
    
    print(f"\n📊 Import test: {passed} passed, {failed} failed")
    return failed == 0

def test_miner():
    """Test Yescrypt miner availability"""
    print("\n⛏️ Testing Yescrypt miner...")
    
    # Add mining to path
    sys.path.append('mining')
    
    try:
        from mining.zion_yescrypt_hybrid import HybridYescryptMiner
        print("  ✅ Yescrypt Hybrid miner loaded")
        
        # Try to import C extension
        try:
            import yescrypt_fast
            print("  ✅ C extension available (10x performance!)")
            has_c_ext = True
        except ImportError:
            print("  ⚠️ C extension not available (using Python fallback)")
            has_c_ext = False
        
        return True, has_c_ext
        
    except Exception as e:
        print(f"  ❌ Miner error: {e}")
        return False, False

def test_ssh_config():
    """Test SSH configuration"""
    print("\n🔐 Testing SSH configuration...")
    
    config_path = 'config/ssh_config.json'
    
    if os.path.exists(config_path):
        try:
            import json
            with open(config_path) as f:
                config = json.load(f)
            
            print(f"  ✅ Config file found")
            print(f"  📡 Host: {config.get('host', 'Not set')}")
            print(f"  🔢 Port: {config.get('port', 'Not set')}")
            print(f"  👤 User: {config.get('username', 'Not set')}")
            
            if config.get('host') == 'YOUR_SSH_SERVER_IP':
                print("  ⚠️ WARNING: Please configure SSH server IP in config/ssh_config.json")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ❌ Config error: {e}")
            return False
    else:
        print(f"  ❌ Config file not found: {config_path}")
        print(f"  💡 Run ./start_ssh_dashboard.sh to create default config")
        return False

def test_file_structure():
    """Test required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = {
        'Dashboard_SSH_Optimized.py': 'Main dashboard',
        'requirements-ssh-dashboard.txt': 'Dependencies',
        'ZION_SSH_DASHBOARD_GUIDE.md': 'Documentation',
        'mining/zion_yescrypt_hybrid.py': 'Yescrypt miner'
    }
    
    passed = 0
    failed = 0
    
    for file, description in required_files.items():
        if os.path.exists(file):
            print(f"  ✅ {file:40} - {description}")
            passed += 1
        else:
            print(f"  ❌ {file:40} - {description}")
            failed += 1
    
    print(f"\n📊 File test: {passed} passed, {failed} failed")
    return failed == 0

def test_system_resources():
    """Test system resources"""
    print("\n💻 Testing system resources...")
    
    try:
        import psutil
        
        cpu_count = os.cpu_count() or 4
        memory = psutil.virtual_memory()
        
        print(f"  ✅ CPU Cores: {cpu_count}")
        print(f"  ✅ RAM Total: {memory.total / (1024**3):.1f} GB")
        print(f"  ✅ RAM Available: {memory.available / (1024**3):.1f} GB")
        
        # Recommendations
        print("\n💡 Mining recommendations:")
        print(f"  - Recommended threads: {max(1, cpu_count - 1)}")
        print(f"  - Expected hashrate: ~{cpu_count * 100}-{cpu_count * 150} H/s (with C ext)")
        print(f"  - Power consumption: ~80W")
        
        return True
        
    except Exception as e:
        print(f"  ❌ System test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 ZION SSH Dashboard - Component Test")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    miner_ok, has_c_ext = test_miner()
    results.append(("Miner", miner_ok))
    results.append(("SSH Config", test_ssh_config()))
    results.append(("File Structure", test_file_structure()))
    results.append(("System Resources", test_system_resources()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! Dashboard is ready to use.")
        print("\n📝 Next steps:")
        print("  1. Configure SSH settings in config/ssh_config.json")
        print("  2. Run: python3 Dashboard_SSH_Optimized.py")
        
        if not has_c_ext:
            print("\n⚡ Performance tip:")
            print("  - Compile C extension for 10x faster mining:")
            print("    cd mining && python3 setup.py build_ext --inplace")
    else:
        print("\n⚠️ Some tests failed. Please fix the issues above.")
        print("\n💡 Quick fixes:")
        print("  - Install dependencies: pip3 install -r requirements-ssh-dashboard.txt")
        print("  - Create config: ./start_ssh_dashboard.sh")
        print("  - Check file paths are correct")
    
    print()
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
