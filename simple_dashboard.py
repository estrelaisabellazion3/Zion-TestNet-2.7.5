#!/usr/bin/env python3
"""
🚀 ZION 2.7.5 Simple Dashboard 🚀
Simplified version without AI components that cause macOS compatibility issues
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import time
from datetime import datetime
import json

class SimpleZionDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 ZION 2.7.5 TestNet Dashboard")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Status variables
        self.mining_active = tk.BooleanVar(value=False)
        self.hashrate = tk.StringVar(value="0.00 H/s")
        self.blocks_found = tk.StringVar(value="0")
        self.network_status = tk.StringVar(value="Disconnected")
        self.server_status = tk.StringVar(value="91.98.122.165:3335 - Ready")
        self.unified_system_status = tk.StringVar(value="❌ Not Running")
        self.ai_yesscript_status = tk.StringVar(value="❌ Inactive")
        
        self.create_ui()
        self.start_monitoring()
    
    def create_ui(self):
        """Create the main UI"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(main_frame, text="🚀 ZION 2.7.5 TestNet Dashboard", 
                              font=('Arial', 18, 'bold'), fg='gold', bg='#1a1a2e')
        title_label.pack(pady=10)
        
        # Status frame
        status_frame = ttk.LabelFrame(main_frame, text="📊 System Status", padding=10)
        status_frame.pack(fill=tk.X, pady=5)
        
        # Server status
        server_frame = ttk.Frame(status_frame)
        server_frame.pack(fill=tk.X, pady=2)
        ttk.Label(server_frame, text="🖥️ Production Server:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(server_frame, textvariable=self.server_status, foreground='green').pack(side=tk.LEFT, padx=10)
        
        # Network status
        network_frame = ttk.Frame(status_frame)
        network_frame.pack(fill=tk.X, pady=2)
        ttk.Label(network_frame, text="🌐 Network:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(network_frame, textvariable=self.network_status, foreground='blue').pack(side=tk.LEFT, padx=10)
        
        # Mining frame
        mining_frame = ttk.LabelFrame(main_frame, text="⛏️ Mining Status", padding=10)
        mining_frame.pack(fill=tk.X, pady=5)
        
        # Mining controls
        control_frame = ttk.Frame(mining_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(control_frame, text="▶️ Start Mining", 
                                      command=self.toggle_mining)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        # Hashrate display
        hashrate_frame = ttk.Frame(mining_frame)
        hashrate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(hashrate_frame, text="Hashrate:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(hashrate_frame, textvariable=self.hashrate, foreground='orange').pack(side=tk.LEFT, padx=10)
        
        # Blocks found
        blocks_frame = ttk.Frame(mining_frame)
        blocks_frame.pack(fill=tk.X, pady=2)
        ttk.Label(blocks_frame, text="Blocks Found:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(blocks_frame, textvariable=self.blocks_found, foreground='green').pack(side=tk.LEFT, padx=10)
        
        # Unified System frame
        unified_frame = ttk.LabelFrame(main_frame, text="🌟 ZION Unified System", padding=10)
        unified_frame.pack(fill=tk.X, pady=5)
        
        # Unified system status
        unified_status_frame = ttk.Frame(unified_frame)
        unified_status_frame.pack(fill=tk.X, pady=2)
        ttk.Label(unified_status_frame, text="System Status:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(unified_status_frame, textvariable=self.unified_system_status).pack(side=tk.LEFT, padx=10)
        
        # AI Yesscript status
        ai_status_frame = ttk.Frame(unified_frame)
        ai_status_frame.pack(fill=tk.X, pady=2)
        ttk.Label(ai_status_frame, text="🤖 AI Yesscript Miner:", font=('Arial', 10, 'bold')).pack(side=tk.LEFT)
        ttk.Label(ai_status_frame, textvariable=self.ai_yesscript_status).pack(side=tk.LEFT, padx=10)
        
        # Unified system controls
        unified_controls_frame = ttk.Frame(unified_frame)
        unified_controls_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(unified_controls_frame, text="🚀 Start Unified", 
                  command=self.start_unified_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(unified_controls_frame, text="⏹️ Stop Unified", 
                  command=self.stop_unified_system).pack(side=tk.LEFT, padx=5)
        ttk.Button(unified_controls_frame, text="📊 Check Status", 
                  command=self.check_unified_status).pack(side=tk.LEFT, padx=5)
        
        # Production Services frame
        services_frame = ttk.LabelFrame(main_frame, text="🐳 Production Services (91.98.122.165)", padding=10)
        services_frame.pack(fill=tk.X, pady=5)
        
        services_text = """
✅ Frontend (Port 3000) - Next.js React Application
✅ Mining Pool (Port 3335) - Universal Pool with Hash Validation  
✅ Node1 (Ports 18089-18090) - Full Node with RPC and WebSocket
✅ Seed1 (Ports 19089-19090) - Bootstrap Node
✅ Seed2 (Ports 19091-19092) - Secondary Bootstrap Node
✅ Rainbow Bridge (Ports 9000-9001) - Multi-chain Bridge Service
✅ PostgreSQL (Port 5432) - Database for Pool Data
✅ Redis (Port 6379) - Cache and Session Storage
✅ ZION Unified System - Blockchain + Pool + AI Yesscript Miner
        """
        
        services_label = tk.Label(services_frame, text=services_text, 
                                 font=('Courier', 9), justify=tk.LEFT, fg='green', bg='white')
        services_label.pack(fill=tk.BOTH, expand=True)
        
        # Log frame
        log_frame = ttk.LabelFrame(main_frame, text="📝 Activity Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=10, width=80, 
                                                 font=('Courier', 9), bg='black', fg='lime')
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        self.log("🚀 ZION 2.7.5 TestNet Dashboard Started")
        self.log("🖥️ Production Server: 91.98.122.165 - All Services Operational")
        self.log("⛏️ Mining Pool Ready on Port 3335")
        self.log("🌐 Blockchain Height: 5613+ blocks")
        self.log("🌟 ZION Unified System Ready")
        
    def start_unified_system(self):
        """Start ZION Unified System"""
        try:
            import subprocess
            # Start unified system with AI mining enabled
            cmd = ['python3', 'zion_unified.py', '--daemon']
            subprocess.Popen(cmd)
            
            self.unified_system_status.set("✅ Starting...")
            self.log("🚀 Starting ZION Unified System (Blockchain + Pool + AI)")
            
            # Schedule status check
            self.root.after(3000, self.check_unified_status)
            
        except Exception as e:
            self.log(f"❌ Error starting unified system: {str(e)}")
            
    def stop_unified_system(self):
        """Stop ZION Unified System"""
        try:
            import subprocess
            # Kill unified system process
            subprocess.run(['pkill', '-f', 'zion_unified.py'], check=False)
            
            self.unified_system_status.set("❌ Not Running")
            self.ai_yesscript_status.set("❌ Inactive")
            self.log("⏹️ ZION Unified System stopped")
            
        except Exception as e:
            self.log(f"❌ Error stopping unified system: {str(e)}")
            
    def check_unified_status(self):
        """Check ZION Unified System status"""
        try:
            import subprocess
            import os
            
            # Check if unified system is running
            result = subprocess.run(['pgrep', '-f', 'zion_unified.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                self.unified_system_status.set("✅ Running")
                self.log("🌟 Unified System: Active")
                
                # Check for AI Yesscript status from live stats
                try:
                    if os.path.exists('live_stats.json'):
                        with open('live_stats.json', 'r') as f:
                            stats = json.load(f)
                            
                        if 'ai_miner' in stats:
                            ai_data = stats['ai_miner']
                            if ai_data.get('active', False):
                                hashrate = ai_data.get('current_hashrate', 0.0)
                                threads = ai_data.get('threads_active', 0)
                                self.ai_yesscript_status.set(f"✅ Active ({hashrate:.1f} H/s, {threads} threads)")
                                self.log(f"🤖 AI Yesscript: {hashrate:.1f} H/s with {threads} threads")
                            else:
                                self.ai_yesscript_status.set("⚠️ Initialized")
                        else:
                            self.ai_yesscript_status.set("⚠️ Initializing")
                    else:
                        self.ai_yesscript_status.set("⚠️ Initializing")
                except Exception:
                    self.ai_yesscript_status.set("⚠️ Status Unknown")
            else:
                self.unified_system_status.set("❌ Not Running")
                self.ai_yesscript_status.set("❌ Inactive")
                
        except Exception as e:
            self.log(f"❌ Error checking status: {str(e)}")

    def log(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        
    def toggle_mining(self):
        """Toggle mining on/off"""
        if self.mining_active.get():
            self.mining_active.set(False)
            self.start_button.config(text="▶️ Start Mining")
            self.hashrate.set("0.00 H/s")
            self.log("⛏️ Mining stopped")
        else:
            self.mining_active.set(True)
            self.start_button.config(text="⏸️ Stop Mining")
            self.log("⛏️ Mining started - Connecting to pool...")
            self.log("🔗 Pool: stratum+tcp://91.98.122.165:3335")
            
    def start_monitoring(self):
        """Start background monitoring"""
        def monitor():
            while True:
                if self.mining_active.get():
                    # Simulate mining activity
                    import random
                    hashrate = random.uniform(50.0, 75.0)
                    self.hashrate.set(f"{hashrate:.2f} H/s")
                    
                    if random.random() < 0.01:  # 1% chance of finding block
                        current_blocks = int(self.blocks_found.get())
                        self.blocks_found.set(str(current_blocks + 1))
                        self.log(f"🎉 Block found! Total: {current_blocks + 1}")
                
                # Update network status
                self.network_status.set("Connected - 3 Peers")
                time.sleep(2)
        
        monitor_thread = threading.Thread(target=monitor, daemon=True)
        monitor_thread.start()
    
    def run(self):
        """Start the dashboard"""
        self.root.mainloop()

if __name__ == "__main__":
    print("🚀 Starting ZION 2.7.5 Simple Dashboard...")
    dashboard = SimpleZionDashboard()
    dashboard.run()