#!/usr/bin/env python3
"""
ZION Real System Status Check - Shows ONLY actual data
No simulations or fake data!
"""

import os
import json
import time
import psutil
from datetime import datetime

def check_live_stats():
    """Check if live_stats.json exists and is current"""
    try:
        if not os.path.exists('live_stats.json'):
            return False, "live_stats.json not found"
        
        # Check file age
        stat = os.stat('live_stats.json')
        age = time.time() - stat.st_mtime
        
        if age > 60:  # More than 1 minute old
            return False, f"live_stats.json is {age:.1f} seconds old"
        
        # Try to read and parse
        with open('live_stats.json', 'r') as f:
            stats = json.load(f)
        
        return True, stats
        
    except Exception as e:
        return False, f"Error reading live_stats.json: {e}"

def check_zion_processes():
    """Check for running ZION processes"""
    processes = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if any(keyword in cmdline.lower() for keyword in ['zion', 'mining', 'dashboard']):
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'cmd': cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
    except Exception as e:
        return False, f"Error checking processes: {e}"
    
    return True, processes

def main():
    print("=" * 60)
    print("ZION REAL SYSTEM STATUS CHECK")
    print("=" * 60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check live stats
    print("1. Live Stats Check:")
    live_ok, live_result = check_live_stats()
    if live_ok:
        print("   ✅ live_stats.json is current and valid")
        stats = live_result
        
        # Show blockchain info
        blockchain = stats.get('blockchain', {})
        print(f"   📦 Blockchain Height: {blockchain.get('height', 0)}")
        print(f"   ⛏️  Mining Active: {blockchain.get('mining_active', False)}")
        
        # Show wallet info
        wallet = stats.get('wallet', {})
        print(f"   💰 Balance: {wallet.get('balance', 0.0)} ZION")
        
        # Show mining info
        mining = stats.get('mining', {})
        print(f"   🔥 Hashrate: {mining.get('hashrate', 0.0)} H/s")
        print(f"   ⚡ Efficiency: {mining.get('efficiency', 0.0)}%")
        
    else:
        print(f"   ❌ {live_result}")
    
    print()
    
    # Check processes
    print("2. Process Check:")
    proc_ok, processes = check_zion_processes()
    if proc_ok and processes:
        print(f"   ✅ Found {len(processes)} ZION-related processes:")
        for proc in processes:
            cmd_short = proc['cmd'][:50] + "..." if len(proc['cmd']) > 50 else proc['cmd']
            print(f"   🔄 PID {proc['pid']}: {cmd_short}")
    elif proc_ok:
        print("   ❌ No ZION processes found")
    else:
        print(f"   ❌ {processes}")
    
    print()
    
    # System resources
    print("3. System Resources:")
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        print(f"   🖥️  CPU Usage: {cpu:.1f}%")
        print(f"   🧠 Memory: {memory.percent:.1f}% ({memory.used/1024**3:.1f}GB / {memory.total/1024**3:.1f}GB)")
        
        # Load average (Linux only)
        try:
            load = os.getloadavg()
            print(f"   📊 Load Average: {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
        except:
            pass
            
    except Exception as e:
        print(f"   ❌ Error getting system info: {e}")
    
    print()
    print("=" * 60)
    
    # Overall status
    if live_ok and proc_ok and processes:
        print("🟢 ZION SYSTEM STATUS: ACTIVE")
    elif proc_ok and processes:
        print("🟡 ZION SYSTEM STATUS: PARTIAL (processes running, no live stats)")
    else:
        print("🔴 ZION SYSTEM STATUS: INACTIVE")
    
    print("=" * 60)

if __name__ == "__main__":
    main()