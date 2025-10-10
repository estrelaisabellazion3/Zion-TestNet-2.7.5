#!/usr/bin/env python3
"""
🚀 ZION 2.7.5 SSH Dashboard - Optimized Edition 🚀
Remote blockchain monitoring and Yescrypt mining dashboard
Connects to SSH server with running blockchain node
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import threading
import time
from datetime import datetime
import subprocess
import os
import sys
import platform
import psutil
from typing import Dict, Any, Optional
import paramiko
from pathlib import Path

# Mining imports
try:
    sys.path.append('mining')
    from mining.zion_yescrypt_hybrid import HybridYescryptMiner
    MINER_AVAILABLE = True
    print("✅ Yescrypt Hybrid Miner loaded")
except ImportError as e:
    print(f"⚠️ Miner not available: {e}")
    MINER_AVAILABLE = False

# SSH Configuration
SSH_CONFIG = {
    'host': 'your_ssh_server_ip',  # Nastavte IP vašeho SSH serveru
    'port': 22,
    'username': 'your_username',
    'password': None,  # Nebo použijte SSH klíč
    'key_file': None,  # Path to SSH private key
}

class SSHConnectionManager:
    """Manages SSH connection to remote blockchain server"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.client = None
        self.connected = False
        self.last_error = None
        
    def connect(self) -> bool:
        """Establish SSH connection"""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.config.get('key_file'):
                # SSH key authentication
                key = paramiko.RSAKey.from_private_key_file(self.config['key_file'])
                self.client.connect(
                    hostname=self.config['host'],
                    port=self.config['port'],
                    username=self.config['username'],
                    pkey=key,
                    timeout=10
                )
            else:
                # Password authentication
                self.client.connect(
                    hostname=self.config['host'],
                    port=self.config['port'],
                    username=self.config['username'],
                    password=self.config.get('password'),
                    timeout=10
                )
            
            self.connected = True
            self.last_error = None
            return True
            
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            print(f"❌ SSH connection failed: {e}")
            return False
    
    def execute_command(self, command: str) -> tuple:
        """Execute remote command via SSH"""
        if not self.connected:
            if not self.connect():
                return (None, None, "Not connected")
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            return (stdout.read().decode(), stderr.read().decode(), None)
        except Exception as e:
            self.connected = False
            return (None, None, str(e))
    
    def get_blockchain_stats(self) -> Dict[str, Any]:
        """Get blockchain statistics from remote server"""
        command = "curl -s http://localhost:8332/api/stats"
        stdout, stderr, error = self.execute_command(command)
        
        if error or stderr:
            return {}
        
        try:
            return json.loads(stdout) if stdout else {}
        except json.JSONDecodeError:
            return {}
    
    def get_pool_stats(self) -> Dict[str, Any]:
        """Get mining pool statistics"""
        command = "curl -s http://localhost:3333/stats"
        stdout, stderr, error = self.execute_command(command)
        
        if error or stderr:
            return {}
        
        try:
            return json.loads(stdout) if stdout else {}
        except json.JSONDecodeError:
            return {}
    
    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            self.connected = False

class ZIONSSHDashboard:
    """ZION Dashboard with SSH remote monitoring and local mining"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ZION 2.7.5 SSH Dashboard - Optimized")
        self.root.geometry("1400x900")
        self.root.configure(bg='#001100')
        
        # SSH connection
        self.ssh = SSHConnectionManager(SSH_CONFIG)
        
        # Mining
        self.miner = None
        self.mining_active = False
        self.mining_thread = None
        
        # Statistics
        self.blockchain_stats = {}
        self.pool_stats = {}
        self.mining_stats = {
            'hashrate': 0.0,
            'shares': 0,
            'eco_shares': 0,
            'power': 80.0
        }
        
        # UI state
        self.monitoring_active = False
        self.update_interval = 5000  # 5 seconds
        
        # Performance history
        self.hashrate_history = []
        self.max_history = 100
        
        # Setup UI
        self.setup_ui()
        
        # Start monitoring
        self.start_monitoring()
    
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main container
        main_frame = tk.Frame(self.root, bg='#001100')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.setup_header(main_frame)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self.create_overview_tab()
        self.create_mining_tab()
        self.create_blockchain_tab()
        self.create_settings_tab()
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_header(self, parent):
        """Setup header with connection status"""
        header = tk.Frame(parent, bg='#001100')
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title = tk.Label(
            header,
            text="🚀 ZION 2.7.5 SSH DASHBOARD",
            font=('Courier', 24, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        title.pack(side=tk.LEFT)
        
        # SSH Status
        self.ssh_status_label = tk.Label(
            header,
            text="⚠️ Not Connected",
            font=('Courier', 12),
            fg='#ff4444',
            bg='#001100'
        )
        self.ssh_status_label.pack(side=tk.RIGHT, padx=20)
        
        # Connect button
        self.connect_btn = tk.Button(
            header,
            text="🔗 Connect SSH",
            command=self.connect_ssh,
            font=('Courier', 10),
            bg='#003300',
            fg='#00ff41',
            activebackground='#004400'
        )
        self.connect_btn.pack(side=tk.RIGHT, padx=5)
    
    def create_overview_tab(self):
        """Overview tab with key metrics"""
        tab = tk.Frame(self.notebook, bg='#001100')
        self.notebook.add(tab, text="📊 Overview")
        
        # Metrics grid
        metrics_frame = tk.Frame(tab, bg='#001100')
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Blockchain metrics
        blockchain_frame = tk.LabelFrame(
            metrics_frame,
            text="🔗 Blockchain Status (Remote)",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        blockchain_frame.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
        
        self.block_height_label = self.create_metric_label(blockchain_frame, "Block Height:", "0")
        self.difficulty_label = self.create_metric_label(blockchain_frame, "Difficulty:", "0")
        self.connections_label = self.create_metric_label(blockchain_frame, "Connections:", "0")
        
        # Mining metrics
        mining_frame = tk.LabelFrame(
            metrics_frame,
            text="⛏️ Mining Status (Local)",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        mining_frame.grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
        
        self.hashrate_label = self.create_metric_label(mining_frame, "Hashrate:", "0 H/s")
        self.shares_label = self.create_metric_label(mining_frame, "Shares:", "0")
        self.eco_shares_label = self.create_metric_label(mining_frame, "Eco Shares:", "0")
        
        # Pool metrics
        pool_frame = tk.LabelFrame(
            metrics_frame,
            text="🌊 Pool Status (Remote)",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        pool_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')
        
        self.pool_hashrate_label = self.create_metric_label(pool_frame, "Pool Hashrate:", "0 H/s")
        self.pool_miners_label = self.create_metric_label(pool_frame, "Active Miners:", "0")
        self.pool_blocks_label = self.create_metric_label(pool_frame, "Blocks Found:", "0")
        
        metrics_frame.grid_columnconfigure(0, weight=1)
        metrics_frame.grid_columnconfigure(1, weight=1)
    
    def create_mining_tab(self):
        """Mining control tab"""
        tab = tk.Frame(self.notebook, bg='#001100')
        self.notebook.add(tab, text="⛏️ Mining")
        
        # Control panel
        control_frame = tk.LabelFrame(
            tab,
            text="⚙️ Mining Control",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        control_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Mining algorithm info
        algo_label = tk.Label(
            control_frame,
            text="Algorithm: Yescrypt (CPU) | Power: ~80W | Eco Bonus: +15%",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100'
        )
        algo_label.pack(pady=10)
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg='#001100')
        button_frame.pack(pady=10)
        
        self.start_mining_btn = tk.Button(
            button_frame,
            text="▶️ Start Mining",
            command=self.start_mining,
            font=('Courier', 12, 'bold'),
            bg='#003300',
            fg='#00ff41',
            width=15,
            activebackground='#004400'
        )
        self.start_mining_btn.pack(side=tk.LEFT, padx=5)
        
        self.stop_mining_btn = tk.Button(
            button_frame,
            text="⏹️ Stop Mining",
            command=self.stop_mining,
            font=('Courier', 12, 'bold'),
            bg='#330000',
            fg='#ff4444',
            width=15,
            state=tk.DISABLED,
            activebackground='#440000'
        )
        self.stop_mining_btn.pack(side=tk.LEFT, padx=5)
        
        # Mining settings
        settings_frame = tk.LabelFrame(
            tab,
            text="⚙️ Settings",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        settings_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Threads
        threads_frame = tk.Frame(settings_frame, bg='#001100')
        threads_frame.pack(pady=5)
        
        tk.Label(
            threads_frame,
            text="CPU Threads:",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100'
        ).pack(side=tk.LEFT, padx=5)
        
        self.threads_var = tk.StringVar(value=str(max(1, os.cpu_count() - 1) if os.cpu_count() else 4))
        threads_spin = tk.Spinbox(
            threads_frame,
            from_=1,
            to=16,
            textvariable=self.threads_var,
            font=('Courier', 10),
            width=5
        )
        threads_spin.pack(side=tk.LEFT, padx=5)
        
        # Eco mode
        self.eco_mode_var = tk.BooleanVar(value=True)
        eco_check = tk.Checkbutton(
            settings_frame,
            text="🌱 Eco Mode (+15% bonus)",
            variable=self.eco_mode_var,
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100',
            selectcolor='#003300'
        )
        eco_check.pack(pady=5)
        
        # Mining log
        log_frame = tk.LabelFrame(
            tab,
            text="📋 Mining Log",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.mining_log = scrolledtext.ScrolledText(
            log_frame,
            font=('Courier', 9),
            bg='#000000',
            fg='#00ff41',
            height=15
        )
        self.mining_log.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_blockchain_tab(self):
        """Blockchain details tab"""
        tab = tk.Frame(self.notebook, bg='#001100')
        self.notebook.add(tab, text="🔗 Blockchain")
        
        # Blockchain info
        info_frame = tk.LabelFrame(
            tab,
            text="📊 Blockchain Information",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        self.blockchain_text = scrolledtext.ScrolledText(
            info_frame,
            font=('Courier', 10),
            bg='#000000',
            fg='#00ff41',
            height=25
        )
        self.blockchain_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def create_settings_tab(self):
        """Settings tab"""
        tab = tk.Frame(self.notebook, bg='#001100')
        self.notebook.add(tab, text="⚙️ Settings")
        
        # SSH Settings
        ssh_frame = tk.LabelFrame(
            tab,
            text="🔐 SSH Connection Settings",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        ssh_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Host
        host_frame = tk.Frame(ssh_frame, bg='#001100')
        host_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(
            host_frame,
            text="Host:",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.ssh_host_var = tk.StringVar(value=SSH_CONFIG.get('host', ''))
        tk.Entry(
            host_frame,
            textvariable=self.ssh_host_var,
            font=('Courier', 10),
            width=40
        ).pack(side=tk.LEFT, padx=5)
        
        # Port
        port_frame = tk.Frame(ssh_frame, bg='#001100')
        port_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(
            port_frame,
            text="Port:",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.ssh_port_var = tk.StringVar(value=str(SSH_CONFIG.get('port', 22)))
        tk.Entry(
            port_frame,
            textvariable=self.ssh_port_var,
            font=('Courier', 10),
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        # Username
        user_frame = tk.Frame(ssh_frame, bg='#001100')
        user_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(
            user_frame,
            text="Username:",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.ssh_user_var = tk.StringVar(value=SSH_CONFIG.get('username', ''))
        tk.Entry(
            user_frame,
            textvariable=self.ssh_user_var,
            font=('Courier', 10),
            width=40
        ).pack(side=tk.LEFT, padx=5)
        
        # Save button
        tk.Button(
            ssh_frame,
            text="💾 Save Settings",
            command=self.save_ssh_settings,
            font=('Courier', 10),
            bg='#003300',
            fg='#00ff41'
        ).pack(pady=10)
        
        # Mining Pool Settings
        pool_frame = tk.LabelFrame(
            tab,
            text="🌊 Mining Pool Settings",
            font=('Courier', 12, 'bold'),
            fg='#00ff41',
            bg='#001100'
        )
        pool_frame.pack(fill=tk.X, padx=20, pady=20)
        
        # Pool address (will use SSH server)
        pool_label = tk.Label(
            pool_frame,
            text=f"Pool: {SSH_CONFIG.get('host', 'Not set')}:3333",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100'
        )
        pool_label.pack(pady=10)
        
        # Wallet
        wallet_frame = tk.Frame(pool_frame, bg='#001100')
        wallet_frame.pack(pady=5, fill=tk.X, padx=10)
        
        tk.Label(
            wallet_frame,
            text="Wallet:",
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100',
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)
        
        self.wallet_var = tk.StringVar(value="Z3NDN97SeT1Apeb4t3z1TFhBb7qr58pTQTjm9PWKFmhQWNWfeFKdEhVj6x2QDATBsuxYzUTKnS4Y42kXArkzJU5X2Vj1NMBc6Y")
        tk.Entry(
            wallet_frame,
            textvariable=self.wallet_var,
            font=('Courier', 8),
            width=60
        ).pack(side=tk.LEFT, padx=5)
    
    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_bar = tk.Label(
            parent,
            text="Ready",
            font=('Courier', 9),
            fg='#00ff41',
            bg='#001100',
            anchor='w'
        )
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
    
    def create_metric_label(self, parent, label_text, value_text):
        """Create metric display label"""
        frame = tk.Frame(parent, bg='#001100')
        frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            frame,
            text=label_text,
            font=('Courier', 10),
            fg='#00ff41',
            bg='#001100'
        ).pack(side=tk.LEFT)
        
        value_label = tk.Label(
            frame,
            text=value_text,
            font=('Courier', 10, 'bold'),
            fg='#00ff00',
            bg='#001100'
        )
        value_label.pack(side=tk.RIGHT)
        
        return value_label
    
    def connect_ssh(self):
        """Connect to SSH server"""
        self.update_status("Connecting to SSH server...")
        
        # Update config from UI
        SSH_CONFIG['host'] = self.ssh_host_var.get()
        SSH_CONFIG['port'] = int(self.ssh_port_var.get())
        SSH_CONFIG['username'] = self.ssh_user_var.get()
        
        # Connect in thread
        def connect_thread():
            if self.ssh.connect():
                self.root.after(0, lambda: self.ssh_status_label.config(
                    text=f"✅ Connected: {SSH_CONFIG['host']}",
                    fg='#00ff41'
                ))
                self.root.after(0, lambda: self.update_status("SSH connected successfully"))
            else:
                self.root.after(0, lambda: self.ssh_status_label.config(
                    text=f"❌ Connection Failed",
                    fg='#ff4444'
                ))
                self.root.after(0, lambda: self.update_status(f"SSH connection error: {self.ssh.last_error}"))
        
        threading.Thread(target=connect_thread, daemon=True).start()
    
    def save_ssh_settings(self):
        """Save SSH settings"""
        SSH_CONFIG['host'] = self.ssh_host_var.get()
        SSH_CONFIG['port'] = int(self.ssh_port_var.get())
        SSH_CONFIG['username'] = self.ssh_user_var.get()
        
        # Save to config file
        try:
            config_path = Path('config/ssh_config.json')
            config_path.parent.mkdir(exist_ok=True)
            
            with open(config_path, 'w') as f:
                json.dump(SSH_CONFIG, f, indent=2)
            
            messagebox.showinfo("Success", "SSH settings saved successfully!")
            self.update_status("SSH settings saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def start_mining(self):
        """Start Yescrypt mining"""
        if not MINER_AVAILABLE:
            messagebox.showerror("Error", "Yescrypt miner not available!")
            return
        
        if self.mining_active:
            messagebox.showwarning("Warning", "Mining already active!")
            return
        
        # Get settings
        threads = int(self.threads_var.get())
        eco_mode = self.eco_mode_var.get()
        wallet = self.wallet_var.get()
        pool_host = SSH_CONFIG.get('host', 'localhost')
        
        if not wallet or len(wallet) < 30:
            messagebox.showerror("Error", "Please enter a valid wallet address!")
            return
        
        # Create miner config
        config = {
            'pool_host': pool_host,
            'pool_port': 3333,
            'wallet_address': wallet,
            'threads': threads,
            'eco_mode': eco_mode
        }
        
        # Start mining in thread
        def mining_thread():
            try:
                self.miner = HybridYescryptMiner(config)
                self.mining_active = True
                
                self.root.after(0, lambda: self.start_mining_btn.config(state=tk.DISABLED))
                self.root.after(0, lambda: self.stop_mining_btn.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.log_mining("🚀 Mining started!"))
                
                # Start miner (this blocks)
                self.miner.start_mining()
                
            except Exception as e:
                self.root.after(0, lambda: self.log_mining(f"❌ Mining error: {e}"))
                self.mining_active = False
        
        self.mining_thread = threading.Thread(target=mining_thread, daemon=True)
        self.mining_thread.start()
        
        self.update_status("Mining started")
    
    def stop_mining(self):
        """Stop mining"""
        if self.miner:
            self.miner.stop_mining.set()
            self.mining_active = False
            
            self.start_mining_btn.config(state=tk.NORMAL)
            self.stop_mining_btn.config(state=tk.DISABLED)
            
            self.log_mining("⏹️ Mining stopped")
            self.update_status("Mining stopped")
    
    def log_mining(self, message):
        """Add message to mining log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.mining_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.mining_log.see(tk.END)
    
    def start_monitoring(self):
        """Start monitoring loop"""
        self.monitoring_active = True
        self.update_all_stats()
    
    def update_all_stats(self):
        """Update all statistics"""
        if not self.monitoring_active:
            return
        
        # Update in thread to avoid blocking
        def update_thread():
            # Get blockchain stats
            blockchain_data = self.ssh.get_blockchain_stats()
            if blockchain_data:
                self.blockchain_stats = blockchain_data
            
            # Get pool stats
            pool_data = self.ssh.get_pool_stats()
            if pool_data:
                self.pool_stats = pool_data
            
            # Update mining stats if active
            if self.miner and self.mining_active:
                try:
                    stats = self.miner.get_mining_stats()
                    if stats:
                        self.mining_stats = stats
                except:
                    pass
            
            # Update UI
            self.root.after(0, self.update_ui)
        
        threading.Thread(target=update_thread, daemon=True).start()
        
        # Schedule next update
        self.root.after(self.update_interval, self.update_all_stats)
    
    def update_ui(self):
        """Update UI with latest stats"""
        # Blockchain stats
        if self.blockchain_stats:
            self.block_height_label.config(text=str(self.blockchain_stats.get('height', 0)))
            self.difficulty_label.config(text=f"{self.blockchain_stats.get('difficulty', 0):.2f}")
            self.connections_label.config(text=str(self.blockchain_stats.get('connections', 0)))
            
            # Update blockchain tab
            self.blockchain_text.delete('1.0', tk.END)
            self.blockchain_text.insert('1.0', json.dumps(self.blockchain_stats, indent=2))
        
        # Mining stats
        self.hashrate_label.config(text=f"{self.mining_stats.get('hashrate', 0):.2f} H/s")
        self.shares_label.config(text=str(self.mining_stats.get('shares', 0)))
        self.eco_shares_label.config(text=str(self.mining_stats.get('eco_shares', 0)))
        
        # Pool stats
        if self.pool_stats:
            self.pool_hashrate_label.config(text=f"{self.pool_stats.get('pool_hashrate', 0):.2f} H/s")
            self.pool_miners_label.config(text=str(self.pool_stats.get('miners', 0)))
            self.pool_blocks_label.config(text=str(self.pool_stats.get('blocks_found', 0)))
    
    def update_status(self, message):
        """Update status bar"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_bar.config(text=f"[{timestamp}] {message}")
    
    def on_closing(self):
        """Handle window closing"""
        if self.mining_active:
            if messagebox.askokcancel("Quit", "Mining is active. Stop mining and quit?"):
                self.stop_mining()
                self.ssh.disconnect()
                self.root.destroy()
        else:
            self.ssh.disconnect()
            self.root.destroy()

def main():
    """Main entry point"""
    print("🚀 ZION 2.7.5 SSH Dashboard - Starting...")
    print("=" * 60)
    
    # Load SSH config if exists
    config_path = Path('config/ssh_config.json')
    if config_path.exists():
        try:
            with open(config_path) as f:
                saved_config = json.load(f)
                SSH_CONFIG.update(saved_config)
            print(f"✅ Loaded SSH config: {SSH_CONFIG.get('host')}")
        except Exception as e:
            print(f"⚠️ Could not load SSH config: {e}")
    
    # Create dashboard
    root = tk.Tk()
    dashboard = ZIONSSHDashboard(root)
    
    # Handle window closing
    root.protocol("WM_DELETE_WINDOW", dashboard.on_closing)
    
    print("✅ Dashboard ready!")
    print("=" * 60)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()
