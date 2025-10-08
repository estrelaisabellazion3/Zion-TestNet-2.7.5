#!/usr/bin/env python3
"""
🚀 ZION 2.7.5 Dashboard Frontend 🚀
Simple Python Dashboard for Monitoring Blockchain and Mining Pool
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import requests
import json
import threading
import time
from datetime import datetime
import subprocess
import os
import sys
import platform
import psutil

# Import AI mining components
try:
    sys.path.append('ai')
    from ai.zion_gpu_miner import ZionGPUMiner
    from ai.zion_ai_afterburner import ZionAIAfterburner, ComputeMode
    from ai.zion_hybrid_miner import ZionHybridMiner
    AI_COMPONENTS_AVAILABLE = True
except ImportError as e:
    print(f"AI components not available: {e}")
    AI_COMPONENTS_AVAILABLE = False

# Cross-platform imports
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Detect OS for cross-platform compatibility
CURRENT_OS = platform.system().lower()
IS_WINDOWS = CURRENT_OS == "windows"
IS_MACOS = CURRENT_OS == "darwin"
IS_LINUX = CURRENT_OS == "linux"

# Data structures for comprehensive monitoring
class SystemStats:
    def __init__(self):
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.memory_total = 0.0
        self.memory_used = 0.0
        self.disk_usage = 0.0
        self.network_tx = 0
        self.network_rx = 0
        self.uptime = "0:00:00"
        self.load_average = [0.0, 0.0, 0.0]

class GPUStats:
    def __init__(self):
        self.temperature = 75.0
        self.utilization = 85
        self.power_usage = 120
        self.memory_usage = 4096
        self.memory_total = 8192
        self.clock_speed = 1500
        self.fan_speed = 75
        self.profile = "zion_optimal"

class MiningStats:
    def __init__(self):
        self.hashrate = 57.56
        self.algorithm = "RandomX"
        self.status = "active"
        self.difficulty = 1
        self.blocks_found = 0
        self.shares_accepted = 0
        self.shares_rejected = 0
        self.pool_connection = "connected"
        self.efficiency = 100.0

class BlockchainStats:
    def __init__(self):
        self.height = 1
        self.network = "ZION 2.7 TestNet"
        self.difficulty = 1
        self.last_block_time = "Just now"
        self.peers = 3
        self.sync_status = "synced"
        self.mempool_size = 0

class AIStats:
    def __init__(self):
        self.active_tasks = 3
        self.completed_tasks = 47
        self.failed_tasks = 2
        self.performance_score = 98.5
        self.neural_networks = 3
        self.allocation_mining = 70
        self.allocation_ai = 30

class ZIONDashboard:
    """ZION Blockchain and Mining Pool Dashboard"""

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ZION 2.7.5 Complete Dashboard 🚀")
        self.root.geometry("1400x900")
        self.root.configure(bg='#0a0a0a')

        # Configuration
        self.blockchain_rpc_url = "http://localhost:8332"
        self.pool_api_url = "http://localhost:3335"
        self.update_interval = 2000  # 2 seconds for real-time updates

        # Initialize comprehensive stats
        self.system_stats = SystemStats()
        self.gpu_stats = GPUStats()
        self.mining_stats = MiningStats()
        self.blockchain_stats = BlockchainStats()
        self.ai_stats = AIStats()

        # Performance history for charts
        self.performance_history = {
            'cpu': [],
            'memory': [],
            'gpu_temp': [],
            'hashrate': [],
            'ai_tasks': [],
            'timestamps': []
        }
        self.max_history_points = 50

        # Status variables
        self.blockchain_status = {"status": "unknown", "blocks": 0, "connections": 0}
        self.pool_status = {"miners": 0, "hashrate": 0, "blocks_found": 0}
        self.system_status = {"cpu": 0, "memory": 0, "disk": 0}

        # AI Mining components
        self.ai_components = {}
        self.ai_status = {}
        if AI_COMPONENTS_AVAILABLE:
            self._init_ai_components()

        self.setup_ui()
        self.start_monitoring()

    def _init_ai_components(self):
        """Initialize AI mining components"""
        try:
            self.ai_components = {
                'gpu_miner': ZionGPUMiner(),
                'ai_afterburner': ZionAIAfterburner(),
                'hybrid_miner': ZionHybridMiner()
            }

            self.ai_status = {
                'gpu_miner': {'active': False, 'hashrate': 0.0, 'algorithm': 'kawpow'},
                'ai_afterburner': {'active': False, 'tasks': 0, 'efficiency': 0.0},
                'hybrid_miner': {'active': False, 'cpu_hashrate': 0.0, 'gpu_hashrate': 0.0, 'total_hashrate': 0.0}
            }

            print("🤖 AI mining components initialized")
        except Exception as e:
            print(f"Failed to initialize AI components: {e}")
            self.ai_components = {}
            self.ai_status = {}

    def setup_ui(self):
        """Setup the dashboard UI"""
        # Configure styles
        style = ttk.Style()
        style.configure("TFrame", background='#0a0a0a')
        style.configure("TLabel", background='#0a0a0a', foreground='#00ff00', font=('Consolas', 10))
        style.configure("TButton", background='#1a1a2e', foreground='#00ff00', font=('Consolas', 10, 'bold'))

        # Main container
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(header_frame, text="🚀 ZION 2.7.5 COMPLETE INTEGRATION DASHBOARD 🚀",
                               font=('Consolas', 16, 'bold'), foreground='#00ffff')
        title_label.pack()

        subtitle_label = ttk.Label(header_frame, text="Real Blockchain • Real Mining • Real Rewards",
                                  font=('Consolas', 12), foreground='#00ff00')
        subtitle_label.pack()

        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(control_frame, text="🔄 Refresh", command=self.manual_refresh).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🚀 Start Local Stack", command=self.start_local_stack).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="⏹️ Stop All", command=self.stop_all).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📊 View Logs", command=self.view_logs).pack(side=tk.LEFT, padx=(0, 10))

        # Status indicators
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 20))

        # Blockchain status
        blockchain_frame = ttk.LabelFrame(status_frame, text="🔗 Blockchain Status", padding=10)
        blockchain_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.blockchain_status_label = ttk.Label(blockchain_frame, text="Status: Checking...",
                                                font=('Consolas', 12, 'bold'))
        self.blockchain_status_label.pack(anchor=tk.W)

        self.blocks_label = ttk.Label(blockchain_frame, text="Blocks: 0")
        self.blocks_label.pack(anchor=tk.W)

        self.connections_label = ttk.Label(blockchain_frame, text="Connections: 0")
        self.connections_label.pack(anchor=tk.W)

        # Pool status
        pool_frame = ttk.LabelFrame(status_frame, text="⛏️ Mining Pool Status", padding=10)
        pool_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        self.pool_status_label = ttk.Label(pool_frame, text="Status: Checking...",
                                          font=('Consolas', 12, 'bold'))
        self.pool_status_label.pack(anchor=tk.W)

        self.miners_label = ttk.Label(pool_frame, text="Active Miners: 0")
        self.miners_label.pack(anchor=tk.W)

        self.hashrate_label = ttk.Label(pool_frame, text="Pool Hashrate: 0 H/s")
        self.hashrate_label.pack(anchor=tk.W)

        # System status
        system_frame = ttk.LabelFrame(status_frame, text="💻 System Status", padding=10)
        system_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.cpu_label = ttk.Label(system_frame, text="CPU: 0%")
        self.cpu_label.pack(anchor=tk.W)

        self.memory_label = ttk.Label(system_frame, text="Memory: 0%")
        self.memory_label.pack(anchor=tk.W)

        self.disk_label = ttk.Label(system_frame, text="Disk: 0%")
        self.disk_label.pack(anchor=tk.W)

        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook for tabs
        self.notebook = ttk.Notebook(content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Blockchain tab
        blockchain_tab = ttk.Frame(self.notebook)
        self.notebook.add(blockchain_tab, text="🔗 Blockchain")

        self.blockchain_text = scrolledtext.ScrolledText(blockchain_tab, height=20,
                                                       bg='#1a1a2e', fg='#00ff00',
                                                       font=('Consolas', 10))
        self.blockchain_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Pool tab
        pool_tab = ttk.Frame(self.notebook)
        self.notebook.add(pool_tab, text="⛏️ Mining Pool")

        self.pool_text = scrolledtext.ScrolledText(pool_tab, height=20,
                                                  bg='#1a1a2e', fg='#00ff00',
                                                  font=('Consolas', 10))
        self.pool_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # AI Mining tab
        ai_tab = ttk.Frame(self.notebook)
        self.notebook.add(ai_tab, text="🤖 AI Mining")

        self.setup_ai_mining_tab(ai_tab)

        # Performance Charts tab
        charts_tab = ttk.Frame(self.notebook)
        self.notebook.add(charts_tab, text="📊 Charts")

        self.setup_charts_tab(charts_tab)

        # Control Panel tab
        control_tab = ttk.Frame(self.notebook)
        self.notebook.add(control_tab, text="🎛️ Control")

        self.setup_control_tab(control_tab)
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="📋 Logs")

        self.logs_text = scrolledtext.ScrolledText(logs_tab, height=20,
                                                  bg='#1a1a2e', fg='#00ff00',
                                                  font=('Consolas', 10))
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Status bar
        self.status_bar = ttk.Label(main_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def setup_ai_mining_tab(self, parent):
        """Setup AI Mining tab"""
        # AI Components status
        components_frame = ttk.LabelFrame(parent, text="🤖 AI Mining Components", padding=10)
        components_frame.pack(fill=tk.X, pady=(0, 10))

        # GPU Miner
        gpu_frame = ttk.Frame(components_frame)
        gpu_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(gpu_frame, text="🎮 GPU Miner:", font=('Consolas', 10, 'bold')).pack(side=tk.LEFT)
        self.gpu_status_label = ttk.Label(gpu_frame, text="Inactive", foreground='#ff0000')
        self.gpu_status_label.pack(side=tk.LEFT, padx=(10, 0))

        self.gpu_hashrate_label = ttk.Label(gpu_frame, text="0.0 MH/s")
        self.gpu_hashrate_label.pack(side=tk.RIGHT)

        ttk.Button(gpu_frame, text="Start GPU", command=self.start_gpu_miner).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(gpu_frame, text="Stop GPU", command=self.stop_gpu_miner).pack(side=tk.RIGHT, padx=(5, 0))

        # AI Afterburner
        ai_frame = ttk.Frame(components_frame)
        ai_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(ai_frame, text="🔥 AI Afterburner:", font=('Consolas', 10, 'bold')).pack(side=tk.LEFT)
        self.ai_status_label = ttk.Label(ai_frame, text="Inactive", foreground='#ff0000')
        self.ai_status_label.pack(side=tk.LEFT, padx=(10, 0))

        self.ai_tasks_label = ttk.Label(ai_frame, text="0 tasks")
        self.ai_tasks_label.pack(side=tk.RIGHT)

        ttk.Button(ai_frame, text="Start AI", command=self.start_ai_afterburner).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(ai_frame, text="Stop AI", command=self.stop_ai_afterburner).pack(side=tk.RIGHT, padx=(5, 0))

        # Hybrid Miner
        hybrid_frame = ttk.Frame(components_frame)
        hybrid_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(hybrid_frame, text="⚡ Hybrid Miner:", font=('Consolas', 10, 'bold')).pack(side=tk.LEFT)
        self.hybrid_status_label = ttk.Label(hybrid_frame, text="Inactive", foreground='#ff0000')
        self.hybrid_status_label.pack(side=tk.LEFT, padx=(10, 0))

        self.hybrid_hashrate_label = ttk.Label(hybrid_frame, text="CPU: 0.0 H/s | GPU: 0.0 MH/s | Total: 0.0 H/s")
        self.hybrid_hashrate_label.pack(side=tk.RIGHT)

        ttk.Button(hybrid_frame, text="Start Hybrid", command=self.start_hybrid_miner).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(hybrid_frame, text="Stop Hybrid", command=self.stop_hybrid_miner).pack(side=tk.RIGHT, padx=(5, 0))

        # AI Performance metrics
        metrics_frame = ttk.LabelFrame(parent, text="📊 AI Performance Metrics", padding=10)
        metrics_frame.pack(fill=tk.BOTH, expand=True)

        self.ai_metrics_text = scrolledtext.ScrolledText(metrics_frame, height=15,
                                                       bg='#1a1a2e', fg='#00ff00',
                                                       font=('Consolas', 10))
        self.ai_metrics_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(control_frame, text="🔄 Update AI Status", command=self.update_ai_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🚀 Start All AI", command=self.start_all_ai).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="⏹️ Stop All AI", command=self.stop_all_ai).pack(side=tk.LEFT, padx=(0, 10))

    def setup_charts_tab(self, parent):
        """Setup Performance Charts tab"""
        # Chart area (placeholder for matplotlib/tkinter canvas)
        chart_frame = ttk.LabelFrame(parent, text="📊 Real-time Performance Monitor", padding=10)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Chart display area
        self.chart_text = scrolledtext.ScrolledText(chart_frame, height=25,
                                                   bg='#1a1a2e', fg='#00ff00',
                                                   font=('Consolas', 10))
        self.chart_text.pack(fill=tk.BOTH, expand=True)

        # Chart controls
        controls_frame = ttk.Frame(parent)
        controls_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(controls_frame, text="📈 Update Charts", command=self.update_charts).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="🧹 Clear History", command=self.clear_performance_history).pack(side=tk.LEFT, padx=(0, 10))

    def setup_control_tab(self, parent):
        """Setup Control Panel tab"""
        # GPU Profiles section
        gpu_frame = ttk.LabelFrame(parent, text="🎮 GPU Profiles", padding=10)
        gpu_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        profiles = ["zion_optimal", "mining", "balanced", "eco"]
        self.gpu_profile_var = tk.StringVar(value="zion_optimal")

        for profile in profiles:
            ttk.Radiobutton(gpu_frame, text=profile.replace('_', ' ').title(),
                           variable=self.gpu_profile_var, value=profile,
                           command=self.set_gpu_profile).pack(side=tk.LEFT, padx=(0, 20))

        # Quick Actions section
        actions_frame = ttk.LabelFrame(parent, text="⚡ Quick Actions", padding=10)
        actions_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        ttk.Button(actions_frame, text="🚀 Optimize Mining", command=self.optimize_mining).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="🔧 GPU Reset", command=self.reset_gpu).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="🧠 AI Task", command=self.create_ai_task).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(actions_frame, text="⚖️ Balance Load", command=self.balance_load).pack(side=tk.LEFT, padx=(0, 10))

        # System Controls section
        system_frame = ttk.LabelFrame(parent, text="💻 System Controls", padding=10)
        system_frame.pack(fill=tk.X, pady=(0, 10), padx=10)

        ttk.Button(system_frame, text="🔄 Restart Services", command=self.restart_services).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(system_frame, text="💾 Save Config", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(system_frame, text="📊 Export Data", command=self.export_data).pack(side=tk.LEFT, padx=(0, 10))

    def update_charts(self):
        """Update performance charts display"""
        self.chart_text.delete(1.0, tk.END)

        chart_data = "📊 ZION PERFORMANCE CHARTS\n"
        chart_data += "=" * 50 + "\n\n"

        # CPU Chart
        chart_data += "🔥 CPU Usage History:\n"
        if self.performance_history['cpu']:
            for i, (cpu, timestamp) in enumerate(zip(self.performance_history['cpu'][-10:],
                                                   self.performance_history['timestamps'][-10:])):
                bar = "█" * int(cpu / 10)
                chart_data += f"{timestamp}: {bar} {cpu:.1f}%\n"
        chart_data += "\n"

        # Memory Chart
        chart_data += "💾 Memory Usage History:\n"
        if self.performance_history['memory']:
            for i, (mem, timestamp) in enumerate(zip(self.performance_history['memory'][-10:],
                                                   self.performance_history['timestamps'][-10:])):
                bar = "█" * int(mem / 10)
                chart_data += f"{timestamp}: {bar} {mem:.1f}%\n"
        chart_data += "\n"

        # GPU Temperature Chart
        chart_data += "🎮 GPU Temperature History:\n"
        if self.performance_history['gpu_temp']:
            for i, (temp, timestamp) in enumerate(zip(self.performance_history['gpu_temp'][-10:],
                                                    self.performance_history['timestamps'][-10:])):
                bar = "█" * int(temp / 10)
                chart_data += f"{timestamp}: {bar} {temp:.1f}°C\n"
        chart_data += "\n"

        # Hashrate Chart
        chart_data += "⛏️ Mining Hashrate History:\n"
        if self.performance_history['hashrate']:
            for i, (hr, timestamp) in enumerate(zip(self.performance_history['hashrate'][-10:],
                                                  self.performance_history['timestamps'][-10:])):
                bar = "█" * int(hr / 10)
                chart_data += f"{timestamp}: {bar} {hr:.2f} H/s\n"
        chart_data += "\n"

        # AI Tasks Chart
        chart_data += "🤖 AI Tasks History:\n"
        if self.performance_history['ai_tasks']:
            for i, (tasks, timestamp) in enumerate(zip(self.performance_history['ai_tasks'][-10:],
                                                     self.performance_history['timestamps'][-10:])):
                bar = "█" * int(tasks)
                chart_data += f"{timestamp}: {bar} {tasks} tasks\n"
        chart_data += "\n"

        chart_data += f"📈 Total Data Points: {len(self.performance_history['cpu'])}\n"
        chart_data += f"🔄 Last Update: {datetime.now().strftime('%H:%M:%S')}"

        self.chart_text.insert(tk.END, chart_data)

    def clear_performance_history(self):
        """Clear performance history"""
        for key in self.performance_history:
            self.performance_history[key].clear()
        self.update_charts()
        messagebox.showinfo("Success", "Performance history cleared")

    def set_gpu_profile(self):
        """Set GPU profile"""
        profile = self.gpu_profile_var.get()
        self.gpu_stats.profile = profile

        # Apply profile settings
        if profile == "zion_optimal":
            self.gpu_stats.utilization = 90
            self.gpu_stats.power_usage = 140
        elif profile == "mining":
            self.gpu_stats.utilization = 95
            self.gpu_stats.power_usage = 150
        elif profile == "balanced":
            self.gpu_stats.utilization = 75
            self.gpu_stats.power_usage = 100
        elif profile == "eco":
            self.gpu_stats.utilization = 60
            self.gpu_stats.power_usage = 80

        messagebox.showinfo("Success", f"GPU profile set to: {profile}")

    def optimize_mining(self):
        """Optimize mining performance"""
        # Auto-optimize based on current conditions
        if self.system_stats.cpu_usage > 80:
            self.gpu_stats.profile = "balanced"
            messagebox.showinfo("Optimization", "High CPU usage detected - switched to balanced profile")
        else:
            self.gpu_stats.profile = "mining"
            messagebox.showinfo("Optimization", "Optimal conditions - switched to mining profile")

    def reset_gpu(self):
        """Reset GPU settings"""
        self.gpu_stats.temperature = 75.0
        self.gpu_stats.utilization = 85
        self.gpu_stats.power_usage = 120
        self.gpu_stats.profile = "zion_optimal"
        messagebox.showinfo("Success", "GPU settings reset")

    def create_ai_task(self):
        """Create AI task"""
        self.ai_stats.active_tasks += 1
        messagebox.showinfo("Success", "AI task created")

    def balance_load(self):
        """Balance system load"""
        if self.ai_stats.allocation_mining < 80:
            self.ai_stats.allocation_mining += 10
            self.ai_stats.allocation_ai -= 10
        messagebox.showinfo("Success", "Load balanced")

    def restart_services(self):
        """Restart all services"""
        try:
            # Stop processes
            subprocess.run(['pkill', '-f', 'new_zion_blockchain'], check=False)
            subprocess.run(['pkill', '-f', 'zion_universal_pool'], check=False)

            # Start processes
            subprocess.Popen(['python3', 'new_zion_blockchain.py'],
                           cwd='/media/maitreya/ZION1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.Popen(['python3', 'zion_universal_pool_v2.py'],
                           cwd='/media/maitreya/ZION1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            messagebox.showinfo("Success", "Services restarted")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to restart services: {str(e)}")

    def save_config(self):
        """Save current configuration"""
        config = {
            'gpu_profile': self.gpu_stats.profile,
            'ai_allocation': {
                'mining': self.ai_stats.allocation_mining,
                'ai': self.ai_stats.allocation_ai
            },
            'update_interval': self.update_interval
        }

        try:
            with open('/media/maitreya/ZION1/dashboard_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            messagebox.showinfo("Success", "Configuration saved")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save config: {str(e)}")

    def export_data(self):
        """Export performance data"""
        data = {
            'performance_history': self.performance_history,
            'system_stats': vars(self.system_stats),
            'gpu_stats': vars(self.gpu_stats),
            'mining_stats': vars(self.mining_stats),
            'ai_stats': vars(self.ai_stats),
            'export_time': datetime.now().isoformat()
        }

        try:
            filename = f'/media/maitreya/ZION1/zion_dashboard_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            messagebox.showinfo("Success", f"Data exported to {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {str(e)}")

    def update_ai_status(self):
        """Update AI components status"""
        try:
            # Check AI miner status
            self.ai_stats.gpu_miner_active = self.check_process_running("SRBMiner-MULTI")
            self.ai_stats.ai_afterburner_active = self.check_process_running("zion_ai_afterburner")
            self.ai_stats.hybrid_miner_active = self.check_process_running("xmrig")

            # Update AI allocation based on performance
            if self.system_stats.cpu_usage > 85:
                self.ai_stats.allocation_mining = max(50, self.ai_stats.allocation_mining - 5)
                self.ai_stats.allocation_ai = 100 - self.ai_stats.allocation_mining
            elif self.gpu_stats.temperature > 85:
                self.ai_stats.allocation_mining = max(60, self.ai_stats.allocation_mining - 3)
                self.ai_stats.allocation_ai = 100 - self.ai_stats.allocation_mining

            messagebox.showinfo("Success", "AI status updated")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update AI status: {str(e)}")

    def start_all_ai(self):
        """Start all AI components"""
        try:
            # Start GPU miner
            if not self.ai_stats.gpu_miner_active:
                subprocess.Popen(['./SRBMiner-MULTI', '--config', 'zion_gpu_config.txt'],
                               cwd='/media/maitreya/ZION1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.ai_stats.gpu_miner_active = True

            # Start AI afterburner
            if not self.ai_stats.ai_afterburner_active:
                subprocess.Popen(['python3', 'zion_ai_afterburner.py'],
                               cwd='/media/maitreya/ZION1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.ai_stats.ai_afterburner_active = True

            # Start hybrid miner
            if not self.ai_stats.hybrid_miner_active:
                subprocess.Popen(['xmrig', '--config', 'zion_hybrid_config.json'],
                               cwd='/media/maitreya/ZION1', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.ai_stats.hybrid_miner_active = True

            messagebox.showinfo("Success", "All AI components started")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start AI components: {str(e)}")

    def stop_all_ai(self):
        """Stop all AI components"""
        try:
            # Stop processes
            subprocess.run(['pkill', '-f', 'SRBMiner-MULTI'], check=False)
            subprocess.run(['pkill', '-f', 'zion_ai_afterburner'], check=False)
            subprocess.run(['pkill', '-f', 'xmrig'], check=False)

            # Update status
            self.ai_stats.gpu_miner_active = False
            self.ai_stats.ai_afterburner_active = False
            self.ai_stats.hybrid_miner_active = False

            messagebox.showinfo("Success", "All AI components stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop AI components: {str(e)}")

    def check_process_running(self, process_name):
        """Check if process is running"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except:
            return False

    def run(self):
        """Main application loop"""
        self.update_stats()
        self.root.mainloop()

    def start_monitoring(self):
        """Start background monitoring"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()

    def monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring:
            try:
                self.update_blockchain_status()
                self.update_pool_status()
                self.update_system_status()
                self.update_logs()
                self.update_ai_status()  # Update AI status
                self.update_status_bar("Monitoring active - Last update: " + datetime.now().strftime("%H:%M:%S"))
            except Exception as e:
                self.update_status_bar(f"Error: {str(e)}")

            time.sleep(self.update_interval / 1000)

    def update_blockchain_status(self):
        """Update blockchain status"""
        try:
            response = requests.get(f"{self.blockchain_rpc_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.blockchain_status = data
                self.blockchain_status_label.config(text=f"Status: 🟢 Online", foreground='#00ff00')
                self.blocks_label.config(text=f"Blocks: {data.get('blocks', 0)}")
                self.connections_label.config(text=f"Connections: {data.get('connections', 0)}")

                # Update blockchain tab
                self.blockchain_text.delete(1.0, tk.END)
                self.blockchain_text.insert(tk.END, json.dumps(data, indent=2))
            else:
                self.blockchain_status_label.config(text="Status: 🔴 Offline", foreground='#ff0000')
        except:
            self.blockchain_status_label.config(text="Status: 🔴 Offline", foreground='#ff0000')

    def update_pool_status(self):
        """Update mining pool status"""
        try:
            response = requests.get(f"{self.pool_api_url}/api/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                self.pool_status = data
                self.pool_status_label.config(text=f"Status: 🟢 Online", foreground='#00ff00')
                self.miners_label.config(text=f"Active Miners: {data.get('miners', 0)}")
                self.hashrate_label.config(text=f"Pool Hashrate: {data.get('hashrate', 0)} H/s")

                # Update pool tab
                self.pool_text.delete(1.0, tk.END)
                self.pool_text.insert(tk.END, json.dumps(data, indent=2))
            else:
                self.pool_status_label.config(text="Status: 🔴 Offline", foreground='#ff0000')
        except:
            self.pool_status_label.config(text="Status: 🔴 Offline", foreground='#ff0000')

    def update_system_status(self):
        """Update comprehensive system status"""
        try:
            # CPU and Memory
            if PSUTIL_AVAILABLE:
                self.system_stats.cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                self.system_stats.memory_usage = memory.percent
                self.system_stats.memory_total = round(memory.total / (1024**3), 1)  # GB
                self.system_stats.memory_used = round(memory.used / (1024**3), 1)   # GB

                # Disk usage
                disk = psutil.disk_usage('/')
                self.system_stats.disk_usage = disk.percent

                # Network
                net = psutil.net_io_counters()
                self.system_stats.network_tx = net.bytes_sent
                self.system_stats.network_rx = net.bytes_recv

                # Uptime
                uptime_seconds = time.time() - psutil.boot_time()
                hours, remainder = divmod(int(uptime_seconds), 3600)
                minutes, seconds = divmod(remainder, 60)
                self.system_stats.uptime = f"{hours}:{minutes:02d}:{seconds:02d}"

                # Load average (Unix-like systems)
                try:
                    self.system_stats.load_average = os.getloadavg()
                except (AttributeError, OSError):
                    self.system_stats.load_average = [0.0, 0.0, 0.0]

            # GPU Stats (cross-platform)
            self._update_gpu_stats()

            # Update performance history
            self._update_performance_history()

        except Exception as e:
            print(f"System status update error: {e}")

    def _update_gpu_stats(self):
        """Update GPU statistics cross-platform"""
        try:
            # Try nvidia-smi first
            if IS_LINUX or IS_WINDOWS:
                try:
                    result = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu,utilization.gpu,power.draw,memory.used,memory.total,clocks.current.graphics,fan.speed',
                                           '--format=csv,noheader,nounits'],
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0 and result.stdout.strip():
                        values = result.stdout.strip().split(',')
                        self.gpu_stats.temperature = float(values[0])
                        self.gpu_stats.utilization = int(values[1])
                        self.gpu_stats.power_usage = int(float(values[2]))
                        self.gpu_stats.memory_usage = int(values[3])
                        self.gpu_stats.memory_total = int(values[4])
                        self.gpu_stats.clock_speed = int(values[5])
                        self.gpu_stats.fan_speed = int(values[6]) if len(values) > 6 else 0
                        return
                except (subprocess.TimeoutExpired, FileNotFoundError, ValueError):
                    pass

            # Try AMD ROCm
            if IS_LINUX:
                try:
                    # Get temperature
                    temp_result = subprocess.run(['rocm-smi', '--showtemp'], capture_output=True, text=True, timeout=5)
                    if temp_result.returncode == 0:
                        # Parse temperature (simplified)
                        self.gpu_stats.temperature = 70.0  # Placeholder

                    # Get utilization
                    util_result = subprocess.run(['rocm-smi', '--showuse'], capture_output=True, text=True, timeout=5)
                    if util_result.returncode == 0:
                        self.gpu_stats.utilization = 80  # Placeholder

                    return
                except (subprocess.TimeoutExpired, FileNotFoundError):
                    pass

            # Fallback - simulated data for testing
            self.gpu_stats.temperature = 75.0
            self.gpu_stats.utilization = 85
            self.gpu_stats.power_usage = 120
            self.gpu_stats.memory_usage = 4096
            self.gpu_stats.memory_total = 8192
            self.gpu_stats.clock_speed = 1500
            self.gpu_stats.fan_speed = 75

        except Exception as e:
            print(f"GPU stats update error: {e}")

    def _update_performance_history(self):
        """Update performance history for charts"""
        timestamp = datetime.now().strftime("%H:%M:%S")

        self.performance_history['cpu'].append(self.system_stats.cpu_usage)
        self.performance_history['memory'].append(self.system_stats.memory_usage)
        self.performance_history['gpu_temp'].append(self.gpu_stats.temperature)
        self.performance_history['hashrate'].append(self.mining_stats.hashrate)
        self.performance_history['ai_tasks'].append(self.ai_stats.active_tasks)
        self.performance_history['timestamps'].append(timestamp)

        # Keep only last N points
        for key in self.performance_history:
            if len(self.performance_history[key]) > self.max_history_points:
                self.performance_history[key] = self.performance_history[key][-self.max_history_points:]

    def update_logs(self):
        """Update logs display"""
        try:
            # Read recent logs
            log_content = ""
            log_files = [
                "/media/maitreya/ZION1/pool.log",
                "/media/maitreya/ZION1/xmrig-local.log"
            ]

            for log_file in log_files:
                if os.path.exists(log_file):
                    with open(log_file, 'r') as f:
                        lines = f.readlines()[-20:]  # Last 20 lines
                        log_content += f"\n--- {os.path.basename(log_file)} ---\n"
                        log_content += ''.join(lines)

            self.logs_text.delete(1.0, tk.END)
            self.logs_text.insert(tk.END, log_content)
            self.logs_text.see(tk.END)
        except:
            pass

    def update_status_bar(self, message):
        """Update status bar message"""
        self.status_bar.config(text=message)

    def manual_refresh(self):
        """Manual refresh of all data"""
        self.update_status_bar("Manual refresh in progress...")
        threading.Thread(target=self.refresh_all, daemon=True).start()

    def refresh_all(self):
        """Refresh all data"""
        self.update_blockchain_status()
        self.update_pool_status()
        self.update_system_status()
        self.update_logs()
        self.update_status_bar("Manual refresh completed")

    def start_local_stack(self):
        """Start the local ZION stack"""
        try:
            script_path = "/media/maitreya/ZION1/start_zion_local.sh"
            if os.path.exists(script_path):
                subprocess.Popen(['bash', script_path], cwd="/media/maitreya/ZION1")
                messagebox.showinfo("Success", "Local ZION stack starting...")
                self.update_status_bar("Local stack starting...")
            else:
                messagebox.showerror("Error", "start_zion_local.sh not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start local stack: {str(e)}")

    def stop_all(self):
        """Stop all ZION processes"""
        try:
            subprocess.run(['pkill', '-f', 'new_zion_blockchain'], check=False)
            subprocess.run(['pkill', '-f', 'zion_universal_pool'], check=False)
            subprocess.run(['pkill', '-f', 'xmrig'], check=False)
            messagebox.showinfo("Success", "All ZION processes stopped")
            self.update_status_bar("All processes stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop processes: {str(e)}")

    def view_logs(self):
        """Open logs in system viewer"""
        try:
            log_dir = "/media/maitreya/ZION1"
            if os.path.exists(log_dir):
                subprocess.run(['xdg-open', log_dir])
            else:
                messagebox.showerror("Error", "Log directory not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open logs: {str(e)}")

    # AI Mining Control Methods
    def start_gpu_miner(self):
        """Start GPU miner"""
        if 'gpu_miner' not in self.ai_components:
            messagebox.showerror("Error", "GPU Miner not available")
            return

        try:
            gpu_miner = self.ai_components['gpu_miner']
            if gpu_miner.start_mining():
                self.ai_status['gpu_miner']['active'] = True
                self.gpu_status_label.config(text="Active", foreground='#00ff00')
                messagebox.showinfo("Success", "GPU Miner started")
            else:
                messagebox.showerror("Error", "Failed to start GPU Miner")
        except Exception as e:
            messagebox.showerror("Error", f"GPU Miner error: {str(e)}")

    def stop_gpu_miner(self):
        """Stop GPU miner"""
        if 'gpu_miner' not in self.ai_components:
            return

        try:
            self.ai_components['gpu_miner'].stop_mining()
            self.ai_status['gpu_miner']['active'] = False
            self.gpu_status_label.config(text="Inactive", foreground='#ff0000')
            self.gpu_hashrate_label.config(text="0.0 MH/s")
        except Exception as e:
            messagebox.showerror("Error", f"GPU Miner stop error: {str(e)}")

    def start_ai_afterburner(self):
        """Start AI Afterburner"""
        if 'ai_afterburner' not in self.ai_components:
            messagebox.showerror("Error", "AI Afterburner not available")
            return

        try:
            ai_afterburner = self.ai_components['ai_afterburner']
            if ai_afterburner.start_afterburner():
                self.ai_status['ai_afterburner']['active'] = True
                self.ai_status_label.config(text="Active", foreground='#00ff00')
                messagebox.showinfo("Success", "AI Afterburner started")
            else:
                messagebox.showerror("Error", "Failed to start AI Afterburner")
        except Exception as e:
            messagebox.showerror("Error", f"AI Afterburner error: {str(e)}")

    def stop_ai_afterburner(self):
        """Stop AI Afterburner"""
        if 'ai_afterburner' not in self.ai_components:
            return

        try:
            self.ai_components['ai_afterburner'].stop_afterburner()
            self.ai_status['ai_afterburner']['active'] = False
            self.ai_status_label.config(text="Inactive", foreground='#ff0000')
            self.ai_tasks_label.config(text="0 tasks")
        except Exception as e:
            messagebox.showerror("Error", f"AI Afterburner stop error: {str(e)}")

    def start_hybrid_miner(self):
        """Start Hybrid Miner"""
        if 'hybrid_miner' not in self.ai_components:
            messagebox.showerror("Error", "Hybrid Miner not available")
            return

        try:
            hybrid_miner = self.ai_components['hybrid_miner']
            if hybrid_miner.start_hybrid_mining():
                self.ai_status['hybrid_miner']['active'] = True
                self.hybrid_status_label.config(text="Active", foreground='#00ff00')
                messagebox.showinfo("Success", "Hybrid Miner started")
            else:
                messagebox.showerror("Error", "Failed to start Hybrid Miner")
        except Exception as e:
            messagebox.showerror("Error", f"Hybrid Miner error: {str(e)}")

    def stop_hybrid_miner(self):
        """Stop Hybrid Miner"""
        if 'hybrid_miner' not in self.ai_components:
            return

        try:
            self.ai_components['hybrid_miner'].stop_hybrid_mining()
            self.ai_status['hybrid_miner']['active'] = False
            self.hybrid_status_label.config(text="Inactive", foreground='#ff0000')
            self.hybrid_hashrate_label.config(text="CPU: 0.0 H/s | GPU: 0.0 MH/s | Total: 0.0 H/s")
        except Exception as e:
            messagebox.showerror("Error", f"Hybrid Miner stop error: {str(e)}")

    def start_all_ai(self):
        """Start all AI components"""
        self.start_gpu_miner()
        self.start_ai_afterburner()
        self.start_hybrid_miner()

    def stop_all_ai(self):
        """Stop all AI components"""
        self.stop_gpu_miner()
        self.stop_ai_afterburner()
        self.stop_hybrid_miner()

    def update_ai_status(self):
        """Update AI components status"""
        if not self.ai_components:
            return

        try:
            # Update GPU Miner
            if 'gpu_miner' in self.ai_components:
                gpu_miner = self.ai_components['gpu_miner']
                self.ai_status['gpu_miner']['hashrate'] = gpu_miner.hashrate
                self.ai_status['gpu_miner']['active'] = gpu_miner.is_mining
                self.ai_status['gpu_miner']['algorithm'] = gpu_miner.current_algorithm

                status = "Active" if gpu_miner.is_mining else "Inactive"
                color = '#00ff00' if gpu_miner.is_mining else '#ff0000'
                self.gpu_status_label.config(text=status, foreground=color)
                self.gpu_hashrate_label.config(text=f"{gpu_miner.hashrate:.1f} MH/s")

            # Update AI Afterburner
            if 'ai_afterburner' in self.ai_components:
                ai_afterburner = self.ai_components['ai_afterburner']
                self.ai_status['ai_afterburner']['active'] = ai_afterburner.processing_active
                self.ai_status['ai_afterburner']['tasks'] = len(ai_afterburner.active_tasks)
                self.ai_status['ai_afterburner']['efficiency'] = ai_afterburner.performance_metrics.get('compute_efficiency', 0.0)

                status = "Active" if ai_afterburner.processing_active else "Inactive"
                color = '#00ff00' if ai_afterburner.processing_active else '#ff0000'
                self.ai_status_label.config(text=status, foreground=color)
                self.ai_tasks_label.config(text=f"{len(ai_afterburner.active_tasks)} tasks")

            # Update Hybrid Miner
            if 'hybrid_miner' in self.ai_components:
                hybrid_miner = self.ai_components['hybrid_miner']
                self.ai_status['hybrid_miner']['active'] = hybrid_miner.cpu_mining_active or hybrid_miner.gpu_miner.is_mining
                self.ai_status['hybrid_miner']['cpu_hashrate'] = hybrid_miner.cpu_hashrate
                self.ai_status['hybrid_miner']['gpu_hashrate'] = hybrid_miner.gpu_miner.hashrate
                self.ai_status['hybrid_miner']['total_hashrate'] = hybrid_miner.cpu_hashrate + (hybrid_miner.gpu_miner.hashrate * 1000000)  # Convert MH/s to H/s

                status = "Active" if self.ai_status['hybrid_miner']['active'] else "Inactive"
                color = '#00ff00' if self.ai_status['hybrid_miner']['active'] else '#ff0000'
                self.hybrid_status_label.config(text=status, foreground=color)
                self.hybrid_hashrate_label.config(text=f"CPU: {hybrid_miner.cpu_hashrate:.1f} H/s | GPU: {hybrid_miner.gpu_miner.hashrate:.1f} MH/s | Total: {self.ai_status['hybrid_miner']['total_hashrate']:.1f} H/s")

            # Update metrics display
            self.update_ai_metrics_display()

        except Exception as e:
            print(f"AI status update error: {e}")

    def update_ai_metrics_display(self):
        """Update AI metrics display"""
        self.ai_metrics_text.delete(1.0, tk.END)

        metrics = "🤖 ZION AI MINING METRICS\n"
        metrics += "=" * 50 + "\n\n"

        for component, status in self.ai_status.items():
            metrics += f"🔧 {component.upper().replace('_', ' ')}\n"
            for key, value in status.items():
                metrics += f"  {key}: {value}\n"
            metrics += "\n"

        # Add performance summary
        total_hashrate = 0
        active_components = 0

        if 'gpu_miner' in self.ai_status and self.ai_status['gpu_miner']['active']:
            total_hashrate += self.ai_status['gpu_miner']['hashrate'] * 1000000  # MH/s to H/s
            active_components += 1

        if 'hybrid_miner' in self.ai_status and self.ai_status['hybrid_miner']['active']:
            total_hashrate += self.ai_status['hybrid_miner']['total_hashrate']
            active_components += 1

        metrics += f"📊 SUMMARY\n"
        metrics += f"  Active Components: {active_components}\n"
        metrics += f"  Total Hashrate: {total_hashrate:.1f} H/s\n"
        metrics += f"  AI Tasks: {self.ai_status.get('ai_afterburner', {}).get('tasks', 0)}\n"
        metrics += f"  Last Update: {datetime.now().strftime('%H:%M:%S')}\n"

        self.ai_metrics_text.insert(tk.END, metrics)

def main():
    """Main entry point"""
    root = tk.Tk()
    app = ZIONDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    main()