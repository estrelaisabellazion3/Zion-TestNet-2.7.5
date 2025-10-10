#!/usr/bin/env python3
"""
Quick SSH connection test for ZION Dashboard
"""
import json
import paramiko
from pathlib import Path

def load_ssh_config():
    config_path = Path('config/ssh_config.json')
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {
        'host': '91.98.122.165',
        'port': 22,
        'username': 'root',
        'password': None,
        'key_file': None
    }

def test_ssh_connection():
    config = load_ssh_config()
    print(f"🔗 Testing SSH connection to {config['host']}:{config['port']}")
    print(f"👤 User: {config['username']}")
    print("=" * 60)
    
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        print("⏳ Connecting...")
        client.connect(
            hostname=config['host'],
            port=config['port'],
            username=config['username'],
            timeout=10
        )
        print("✅ SSH Connected!")
        
        # Test blockchain stats
        print("\n📊 Testing blockchain stats...")
        cmd = 'cd /root/zion && python3 -c "from zion_unified import ZionUnifiedSystem; z=ZionUnifiedSystem(); print(z.get_blockchain_height())" 2>&1 | tail -1'
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        print(f"   Block height: {output}")
        
        # Test pool stats
        print("\n⛏️  Testing pool stats...")
        cmd = 'cd /root/zion && tail -20 unified_production_diff1500.log | grep -i "block\|share" | tail -5'
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        if output:
            print("   Recent activity:")
            for line in output.split('\n')[:5]:
                print(f"   {line}")
        
        # Test process
        print("\n🔄 Testing ZION process...")
        cmd = 'ps aux | grep zion_unified | grep -v grep'
        stdin, stdout, stderr = client.exec_command(cmd)
        output = stdout.read().decode().strip()
        if output:
            print("   ✅ zion_unified.py is running")
        else:
            print("   ⚠️  zion_unified.py not running")
        
        client.close()
        print("\n" + "=" * 60)
        print("✅ SSH connection test PASSED!")
        print("Dashboard should be able to connect successfully.")
        return True
        
    except Exception as e:
        print(f"\n❌ SSH connection FAILED: {e}")
        print("\n💡 Tips:")
        print("   1. Check SSH server is running")
        print("   2. Verify firewall allows port 22")
        print("   3. Check username/password or SSH key")
        print("   4. Try: ssh root@91.98.122.165")
        return False

if __name__ == "__main__":
    test_ssh_connection()
