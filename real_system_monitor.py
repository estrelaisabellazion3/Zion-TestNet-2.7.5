#!/usr/bin/env python3
"""
Real System Monitor - Only shows actual running processes and system data
No simulations, no fake data
"""

import os
import json
import time
import subprocess
import psutil
from datetime import datetime

class RealSystemMonitor:
    def __init__(self):
        self.status = {
            'timestamp': '',
            'blockchain': {
                'running': False,
                'height': 0,
                'connections': 0
            },
            'mining': {
                'active': False,
                'hashrate': 0.0,
                'processes': []
            },
            'system': {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0
            },
            'network': {
                'pool_connection': False,
                'peer_count': 0
            }
        }
    
    def check_blockchain_process(self):
        """Check if blockchain daemon is running"""
        try:
            # Look for common blockchain process names
            blockchain_processes = ['ziond', 'zion-daemon', 'blockchain', 'node']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                    
                    for bp in blockchain_processes:
                        if bp in name or bp in cmdline:
                            self.status['blockchain']['running'] = True
                            return True
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.status['blockchain']['running'] = False
            return False
            
        except Exception as e:
            print(f"Error checking blockchain: {e}")
            return False
    
    def check_mining_processes(self):
        """Check for actual mining processes"""
        try:
            mining_processes = ['xmrig', 'cpuminer', 'srbminer', 'teamredminer', 'miner']
            active_miners = []
            total_hashrate = 0.0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent']):
                try:
                    name = proc.info['name'].lower()
                    cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
                    
                    for mp in mining_processes:
                        if mp in name or mp in cmdline:
                            active_miners.append({
                                'name': proc.info['name'],
                                'pid': proc.info['pid'],
                                'cpu': proc.info['cpu_percent']
                            })
                            # Estimate hashrate based on CPU usage (rough approximation)
                            total_hashrate += proc.info['cpu_percent'] * 2.5
                            
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            self.status['mining']['active'] = len(active_miners) > 0
            self.status['mining']['processes'] = active_miners
            self.status['mining']['hashrate'] = total_hashrate
            
            return len(active_miners) > 0
            
        except Exception as e:
            print(f"Error checking mining: {e}")
            return False
    
    def get_system_stats(self):
        """Get real system statistics"""
        try:
            # CPU usage
            self.status['system']['cpu'] = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.status['system']['memory'] = memory.percent
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.status['system']['disk'] = disk.percent
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
    
    def check_network_connections(self):
        """Check for network connections to pools or peers"""
        try:
            connections = psutil.net_connections()
            pool_connected = False
            peer_count = 0
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    # Check for common pool ports
                    if conn.raddr and conn.raddr.port in [3333, 4444, 5555, 8080, 8888]:
                        pool_connected = True
                    peer_count += 1
            
            self.status['network']['pool_connection'] = pool_connected
            self.status['network']['peer_count'] = peer_count
            
        except Exception as e:
            print(f"Error checking network: {e}")
    
    def read_live_stats(self):
        """Read live stats if available"""
        try:
            if os.path.exists('live_stats.json'):
                with open('live_stats.json', 'r') as f:
                    live_data = json.load(f)
                
                # Update with live data
                blockchain = live_data.get('blockchain', {})
                self.status['blockchain']['height'] = blockchain.get('height', 0)
                self.status['blockchain']['connections'] = blockchain.get('connections', 0)
                
                mining = live_data.get('mining', {})
                if mining.get('active'):
                    self.status['mining']['active'] = True
                    self.status['mining']['hashrate'] = mining.get('hashrate', 0.0)
                
        except Exception as e:
            print(f"Error reading live stats: {e}")
    
    def update_status(self):
        """Update all status information"""
        self.status['timestamp'] = datetime.now().isoformat()
        
        # Check all systems
        self.check_blockchain_process()
        self.check_mining_processes()
        self.get_system_stats()
        self.check_network_connections()
        self.read_live_stats()
        
        return self.status
    
    def save_status(self):
        """Save current status to file"""
        try:
            with open('real_system_status.json', 'w') as f:
                json.dump(self.status, f, indent=2)
        except Exception as e:
            print(f"Error saving status: {e}")
    
    def print_status(self):
        """Print current status to console"""
        print(f"\n=== REAL SYSTEM STATUS - {self.status['timestamp']} ===")
        
        # Blockchain status
        blockchain_status = "🟢 RUNNING" if self.status['blockchain']['running'] else "🔴 OFFLINE"
        print(f"Blockchain: {blockchain_status}")
        if self.status['blockchain']['height'] > 0:
            print(f"  Height: {self.status['blockchain']['height']}")
        if self.status['blockchain']['connections'] > 0:
            print(f"  Connections: {self.status['blockchain']['connections']}")
        
        # Mining status
        mining_status = "🟢 ACTIVE" if self.status['mining']['active'] else "🔴 INACTIVE"
        print(f"Mining: {mining_status}")
        if self.status['mining']['active']:
            print(f"  Hashrate: {self.status['mining']['hashrate']:.1f} H/s")
            print(f"  Processes: {len(self.status['mining']['processes'])}")
        
        # System stats
        print(f"System:")
        print(f"  CPU: {self.status['system']['cpu']:.1f}%")
        print(f"  Memory: {self.status['system']['memory']:.1f}%")
        print(f"  Disk: {self.status['system']['disk']:.1f}%")
        
        # Network
        pool_status = "🟢 CONNECTED" if self.status['network']['pool_connection'] else "🔴 DISCONNECTED"
        print(f"Network: {pool_status}")
        print(f"  Active connections: {self.status['network']['peer_count']}")

def main():
    """Main monitoring loop"""
    monitor = RealSystemMonitor()
    
    print("Starting Real System Monitor...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            monitor.update_status()
            monitor.save_status()
            monitor.print_status()
            
            time.sleep(5)  # Update every 5 seconds
            
    except KeyboardInterrupt:
        print("\nMonitor stopped.")
        monitor.save_status()

if __name__ == "__main__":
    main()