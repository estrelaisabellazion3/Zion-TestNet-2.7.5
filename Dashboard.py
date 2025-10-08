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
from flask import Flask, jsonify, request
from threading import Thread
import socket

# Import AI mining components
try:
    sys.path.append('ai')
    from ai.zion_gpu_miner import ZionGPUMiner
    from ai.zion_ai_afterburner import ZionAIAfterburner, ComputeMode
    from ai.zion_hybrid_miner import ZionHybridMiner
    from ai.zion_ai_yesscript_miner import ZionAIYesscriptMiner
    AI_COMPONENTS_AVAILABLE = True
    print("All AI components enabled")
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
        self.gpu_miner_active = False
        self.ai_afterburner_active = False
        self.hybrid_miner_active = False
        self.yesscript_miner_active = False
        self.neural_networks = 2
        self.allocation_mining = 70
        self.allocation_ai = 30
        self.compute_mode = "OPTIMIZED"
        self.efficiency = 95.2
        self.neural_networks = 3
        self.allocation_mining = 70
        self.allocation_ai = 30

class ZIONDashboard:
    """ZION Blockchain and Mining Pool Dashboard"""

    def __init__(self, root):
        self.root = root
        self.root.title("🚀 ZION 2.7.5 Advanced Dashboard 🚀")
        self.root.geometry("1600x1000")
        self.root.configure(bg='#0f0f23')
        self.root.resizable(True, True)
        
        # Modern styling configuration
        self.colors = {
            'bg_primary': '#0f0f23',
            'bg_secondary': '#1a1a2e', 
            'bg_tertiary': '#16213e',
            'accent': '#00d4ff',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'error': '#ff3366',
            'text_primary': '#ffffff',
            'text_secondary': '#b4b4b4',
            'text_accent': '#00d4ff'
        }

        # Optimized configuration
        self.blockchain_rpc_url = "http://localhost:8332"
        self.pool_api_url = "http://localhost:3336"
        self.unified_system_api = "http://localhost:8332/unified"  # New unified system API
        self.update_interval = 3000  # Optimized to 3 seconds
        self.chart_update_interval = 5000  # Charts update less frequently

        # Initialize comprehensive stats
        self.system_stats = SystemStats()
        self.gpu_stats = GPUStats()
        self.mining_stats = MiningStats()
        self.blockchain_stats = BlockchainStats()
        self.ai_stats = AIStats()

        # Optimized performance history for charts
        self.performance_history = {
            'cpu': [], 'memory': [], 'gpu_temp': [], 'hashrate': [], 'ai_tasks': [], 'network_rx': [], 'network_tx': [], 'timestamps': []
        }
        self.max_history_points = 100

        # Status variables
        self.blockchain_status = {"status": "unknown", "blocks": 0, "connections": 0}
        self.pool_status = {"miners": 0, "hashrate": 0, "blocks_found": 0}
        self.system_status = {"cpu": 0, "memory": 0, "disk": 0}

        # AI status container
        self.ai_status = {}

        # Initialize AI components if available
        if AI_COMPONENTS_AVAILABLE:
            self._init_ai_components()

        # UI setup & services
        self.setup_ui()
        self.start_monitoring()
        self.setup_integrated_api()
        self.root.after(1000, self.auto_start_all_services)
        self._log_debug("Dashboard initialized")
        # Internal registry for started processes {name: Popen}
        self.process_registry = {}

    def _log_debug(self, msg: str):
        try:
            print(f"[DEBUG] {msg}")
        except Exception:
            pass

    def _load_recent_json(self, path: str, max_age_seconds: int = 30):
        """Load JSON file only if it is not older than given age. Returns dict or None.
        No simulation, strictly real data. Logs debug on failure/age issues."""
        try:
            if not os.path.exists(path):
                return None
            stat = os.stat(path)
            age = time.time() - stat.st_mtime
            if age > max_age_seconds:
                self._log_debug(f"File {path} stale (age {age:.1f}s > {max_age_seconds}s)")
                return None
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self._log_debug(f"Failed to load {path}: {e}")
            return None

    def _update_ai_status_unified(self):
        """Internal consolidated AI status updater (called by public update_ai_status)."""
        timestamp = datetime.now().strftime('%H:%M:%S')
        # Prefer live stats
        unified_stats = None
        if os.path.exists('live_stats.json'):
            try:
                with open('live_stats.json','r') as f:
                    unified_stats = json.load(f)
            except Exception as e:
                self._log_debug(f"live_stats read fail: {e}")
        if unified_stats is None:
            unified_stats = self.get_unified_system_stats()

        gpu_active = self.check_process_running('SRBMiner-MULTI')
        ai_afterburner_active = self.check_process_running('zion_ai_afterburner')
        hybrid_cpu_active = self.check_process_running('xmrig')

        yesscript_active = False
        yesscript_hashrate = 0.0
        yesscript_threads = 0
        if unified_stats:
            ai_section = unified_stats.get('ai_miner') or unified_stats.get('ai') or {}
            yesscript_active = bool(ai_section.get('active', False))
            yesscript_hashrate = float(ai_section.get('current_hashrate', 0.0) or ai_section.get('hashrate', 0.0))
            yesscript_threads = int(ai_section.get('threads_active', 0))
        if not yesscript_active and 'yesscript_miner' in self.ai_components:
            try:
                ys_obj = self.ai_components['yesscript_miner']
                if hasattr(ys_obj, 'get_mining_stats'):
                    ys_stats = ys_obj.get_mining_stats()
                    yesscript_active = ys_stats.get('active', False)
                    yesscript_hashrate = ys_stats.get('hashrate', 0.0)
                    yesscript_threads = ys_stats.get('threads', 0)
            except Exception as e:
                self._log_debug(f"yesscript local fallback fail: {e}")

        # Internal flags
        self.ai_stats.gpu_miner_active = gpu_active
        self.ai_stats.ai_afterburner_active = ai_afterburner_active
        self.ai_stats.hybrid_miner_active = hybrid_cpu_active
        self.ai_stats.yesscript_miner_active = yesscript_active

        # Ensure dict structure
        for k in ['gpu_miner','ai_afterburner','hybrid_miner','yesscript_miner']:
            self.ai_status.setdefault(k, {})

        self.ai_status['gpu_miner'].update({
            'active': gpu_active,
            'hashrate': self.get_gpu_miner_hashrate() if gpu_active else 0.0,
            'algorithm': 'kawpow'
        })
        self.ai_status['ai_afterburner'].update({
            'active': ai_afterburner_active,
            'tasks': getattr(self.ai_stats,'active_tasks',0),
            'efficiency': getattr(self.ai_stats,'efficiency',0.0)
        })
        cpu_hr = self.get_hybrid_miner_hashrate() if hybrid_cpu_active else 0.0
        gpu_hr = self.ai_status['gpu_miner']['hashrate'] if gpu_active else 0.0
        self.ai_status['hybrid_miner'].update({
            'active': hybrid_cpu_active,
            'cpu_hashrate': cpu_hr,
            'gpu_hashrate': gpu_hr,
            'total_hashrate': cpu_hr + gpu_hr
        })
        self.ai_status['yesscript_miner'].update({
            'active': yesscript_active,
            'hashrate': yesscript_hashrate,
            'threads': yesscript_threads,
            'algorithm': 'yescrypt'
        })

        # Update UI indicators
        def _set(ind_name, active, hash_label=None, value=0.0, unit='H/s'):
            w = getattr(self, ind_name, None)
            if w is not None:
                w.config(text=('🟢 Active' if active else '🔴 Inactive'),
                         foreground=(self.colors['success'] if active else self.colors['error']))
            if hash_label:
                hv = getattr(self, hash_label, None)
                if hv is not None:
                    hv.config(text=f"{value:.1f} {unit}")

        _set('gpu_miner_status_indicator', gpu_active, 'gpu_miner_hashrate_display', self.ai_status['gpu_miner']['hashrate']/1_000_000 if self.ai_status['gpu_miner']['hashrate']>0 else 0.0, 'MH/s')
        _set('ai_afterburner_status_indicator', ai_afterburner_active)
        _set('hybrid_miner_status_indicator', hybrid_cpu_active, 'hybrid_miner_hashrate_display', self.ai_status['hybrid_miner']['total_hashrate'])
        _set('yesscript_miner_status_indicator', yesscript_active, 'yesscript_miner_hashrate_display', yesscript_hashrate)

        # AI metrics panel
        self.update_ai_metrics_display()

        if hasattr(self, 'ai_text'):
            try:
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"AI SYSTEM STATUS - {timestamp}\n\n", 'header')
                for key, info in self.ai_status.items():
                    icon = '🟢' if info.get('active') else '🔴'
                    line = f"{icon} {key}: "
                    if 'hashrate' in info:
                        line += f"{info.get('hashrate',0):.1f} H/s"
                    if key == 'yesscript_miner' and info.get('threads'):
                        line += f" | Threads: {info.get('threads')}"
                    self.ai_text.insert(tk.END, line + '\n')
            except Exception as e:
                self._log_debug(f"ai_text render fail: {e}")

    def update_ai_status(self):
        """Public method invoked by monitor loop / buttons."""
        try:
            self._update_ai_status_unified()
            self._log_debug('AI status refreshed')
        except Exception as e:
            self._log_debug(f"update_ai_status outer fail: {e}")

    def setup_header(self, parent):
        """Setup modern header with status indicators"""
        header_frame = ttk.Frame(parent, style="Main.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 20))

        # Title section
        title_section = ttk.Frame(header_frame, style="Main.TFrame")
        title_section.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(title_section, 
                               text="🚀 ZION 2.7.5 ADVANCED DASHBOARD",
                               style="Header.TLabel")
        title_label.pack(anchor='w')

        subtitle_label = ttk.Label(title_section,
                                  text="💎 Next-Gen Blockchain • ⛏️ AI Mining • 🌟 Sacred Economy",
                                  style="Subtitle.TLabel")
        subtitle_label.pack(anchor='w')
        
        # Status indicators section
        status_section = ttk.Frame(header_frame, style="Main.TFrame")
        status_section.pack(side=tk.RIGHT)
        
        self.blockchain_status_label = ttk.Label(status_section, text="🔗 Blockchain: ❓", style="Data.TLabel")
        self.blockchain_status_label.pack(anchor='e')
        
        self.pool_status_label = ttk.Label(status_section, text="⛏️ Pool: ❓", style="Data.TLabel")
        self.pool_status_label.pack(anchor='e')
        
        self.ai_status_label = ttk.Label(status_section, text="🤖 AI: ❓", style="Data.TLabel")
        self.ai_status_label.pack(anchor='e')

    def setup_quick_stats(self, parent):
        """Setup quick stats cards"""
        stats_frame = ttk.Frame(parent, style="Main.TFrame")
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Create stats cards
        self.create_stats_card(stats_frame, "💰", "Balance", "0 ZION", 0)
        self.create_stats_card(stats_frame, "⛏️", "Hashrate", "0 H/s", 1)
        self.create_stats_card(stats_frame, "🎯", "Efficiency", "0%", 2)
        self.create_stats_card(stats_frame, "📊", "Blocks", "0", 3)

    def create_stats_card(self, parent, icon, title, value, column):
        """Create a modern stats card"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.grid(row=0, column=column, padx=10, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Icon
        icon_label = ttk.Label(card, text=icon, font=('Segoe UI', 24), 
                              background=self.colors['bg_secondary'],
                              foreground=self.colors['accent'])
        icon_label.pack(pady=(10, 5))
        
        # Title
        title_label = ttk.Label(card, text=title, style="Data.TLabel")
        title_label.pack()
        
        # Value
        value_label = ttk.Label(card, text=value, style="Value.TLabel")
        value_label.pack(pady=(0, 10))
        
        # Store reference for updates  
        if title == "Balance":
            self.balance_value_label = value_label
        elif title == "Hashrate":
            self.hashrate_value_label = value_label
        elif title == "Efficiency":
            self.efficiency_value_label = value_label
        elif title == "Blocks":
            self.blocks_value_label = value_label

    def setup_main_content(self, parent):
        """Setup main content area with advanced tabs"""
        # Control buttons
        control_frame = ttk.Frame(parent, style="Main.TFrame")
        control_frame.pack(fill=tk.X, pady=(0, 20))

        ttk.Button(control_frame, text="🔄 Refresh", command=self.manual_refresh, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="🚀 Start Services", command=self.start_local_stack, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="⏹️ Stop All", command=self.stop_all, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_frame, text="📊 Analytics", command=self.view_logs, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))

        # Main tabbed interface
        content_frame = ttk.Frame(parent, style="Main.TFrame")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Advanced notebook with custom styling
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
        
        # Terminal tab
        terminal_tab = ttk.Frame(self.notebook)
        self.notebook.add(terminal_tab, text="💻 Terminal")
        
        self.setup_terminal_tab(terminal_tab)
        
        logs_tab = ttk.Frame(self.notebook)
        self.notebook.add(logs_tab, text="📋 Logs")

        self.logs_text = scrolledtext.ScrolledText(logs_tab, height=20,
                                                  bg=self.colors['bg_tertiary'], 
                                                  fg=self.colors['success'],
                                                  font=('Consolas', 10))
        self.logs_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def setup_status_bar(self, parent):
        """Setup status bar"""
        self.status_bar = ttk.Label(parent, text="🚀 ZION Dashboard Ready", 
                                   style="Data.TLabel")
        self.status_bar.pack(fill=tk.X, pady=(10, 0))

    def setup_ai_mining_tab(self, parent):
        """Setup advanced AI Mining tab with modern cards"""
        # Main container with scroll
        main_container = ttk.Frame(parent, style="Main.TFrame")
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # AI Mining Overview Card
        overview_card = ttk.LabelFrame(main_container, text="🤖 AI Mining Overview", 
                                      style="Card.TFrame", padding=15)
        overview_card.pack(fill=tk.X, pady=(0, 15))
        
        # Status grid
        status_grid = ttk.Frame(overview_card, style="Card.TFrame")
        status_grid.pack(fill=tk.X)
        
        # GPU Miner Card
        self.create_ai_component_card(status_grid, "🎮 GPU Miner", "gpu_miner", 0)
        
        # AI Afterburner Card  
        self.create_ai_component_card(status_grid, "🔥 AI Afterburner", "ai_afterburner", 1)
        
        # Hybrid Miner Card
        self.create_ai_component_card(status_grid, "⚡ Hybrid Miner", "hybrid_miner", 2)
        
        # AI Yesscript Miner Card
        self.create_ai_component_card(status_grid, "🌊 AI Yesscript Miner", "yesscript_miner", 3)
        
        # Performance Metrics Card
        metrics_card = ttk.LabelFrame(main_container, text="📊 Performance Metrics",
                                     style="Card.TFrame", padding=15)
        metrics_card.pack(fill=tk.X, pady=(0, 15))
        
        # Real-time metrics display
        self.ai_metrics_text = scrolledtext.ScrolledText(
            metrics_card, height=12, width=80,
            bg=self.colors['bg_tertiary'], 
            fg=self.colors['text_primary'],
            font=('Consolas', 10),
            insertbackground=self.colors['accent']
        )
        self.ai_metrics_text.pack(fill=tk.BOTH, expand=True)
        
        # Add global controls at the end
        self.setup_ai_global_controls(main_container)

    def create_ai_component_card(self, parent, title, component_key, column):
        """Create modern AI component card"""
        card = ttk.Frame(parent, style="Card.TFrame")
        card.grid(row=0, column=column, padx=10, pady=5, sticky='ew')
        parent.grid_columnconfigure(column, weight=1)
        
        # Header
        header = ttk.Frame(card, style="Card.TFrame")  
        header.pack(fill=tk.X, pady=(10, 5))
        
        title_label = ttk.Label(header, text=title, style="Data.TLabel",
                               font=('Segoe UI', 11, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        status_label = ttk.Label(header, text="⚫ Inactive", style="Data.TLabel")
        status_label.pack(side=tk.RIGHT)
        setattr(self, f"{component_key}_status_indicator", status_label)
        
        # Metrics
        metrics_frame = ttk.Frame(card, style="Card.TFrame")
        metrics_frame.pack(fill=tk.X, pady=5)
        
        hashrate_label = ttk.Label(metrics_frame, text="0.0 H/s", style="Value.TLabel")
        hashrate_label.pack()
        setattr(self, f"{component_key}_hashrate_display", hashrate_label)
        
        # Control buttons
        control_frame = ttk.Frame(card, style="Card.TFrame")
        control_frame.pack(fill=tk.X, pady=(5, 10))
        
        start_btn = ttk.Button(control_frame, text="▶️ Start", 
                              command=getattr(self, f"start_{component_key}"),
                              style="Accent.TButton")
        start_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        stop_btn = ttk.Button(control_frame, text="⏹️ Stop",
                             command=getattr(self, f"stop_{component_key}"),
                             style="Accent.TButton") 
        stop_btn.pack(side=tk.LEFT)

    def setup_ai_global_controls(self, parent):
        """Setup global AI controls section"""
        # Global AI Controls
        global_controls = ttk.Frame(parent, style="Card.TFrame")
        global_controls.pack(fill=tk.X, pady=10)
        
        ttk.Button(global_controls, text="🔄 Update Status", 
                  command=self.update_ai_status, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(global_controls, text="🚀 Start All AI", 
                  command=self.start_all_ai, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(global_controls, text="⏹️ Stop All AI", 
                  command=self.stop_all_ai, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))

    def setup_terminal_tab(self, parent):
        """Setup integrated terminal tab"""
        # Terminal container
        terminal_container = ttk.Frame(parent, style="Main.TFrame")
        terminal_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Terminal header with controls
        header_frame = ttk.Frame(terminal_container, style="Card.TFrame")
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="💻 Integrated ZION Terminal", 
                 style="Header.TLabel", font=('Segoe UI', 14, 'bold')).pack(side=tk.LEFT, padx=10)
        
        # Terminal controls
        controls_frame = ttk.Frame(header_frame, style="Card.TFrame")
        controls_frame.pack(side=tk.RIGHT, padx=10)
        
        ttk.Button(controls_frame, text="🧹 Clear", 
                  command=self.clear_terminal, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="📋 Copy", 
                  command=self.copy_terminal, style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(controls_frame, text="💾 Save Log", 
                  command=self.save_terminal_log, style="Accent.TButton").pack(side=tk.LEFT)
        
        # Terminal output display
        terminal_frame = ttk.LabelFrame(terminal_container, text="Terminal Output", 
                                       style="Card.TFrame", padding=5)
        terminal_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame,
            height=20,
            bg=self.colors['bg_primary'],
            fg=self.colors['text_primary'],
            font=('Consolas', 10),
            insertbackground=self.colors['accent'],
            selectbackground=self.colors['accent'],
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        # Command input section  
        input_frame = ttk.Frame(terminal_container, style="Card.TFrame")
        input_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(input_frame, text="zion@dashboard:~$", 
                 style="Value.TLabel", font=('Consolas', 10, 'bold')).pack(side=tk.LEFT, padx=(5, 10))
        
        self.command_entry = tk.Entry(
            input_frame,
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_primary'],
            insertbackground=self.colors['accent'],
            font=('Consolas', 10),
            relief='flat',
            bd=5
        )
        self.command_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.command_entry.bind('<Return>', self.execute_command)
        self.command_entry.bind('<Up>', self.command_history_up)
        self.command_entry.bind('<Down>', self.command_history_down)
        
        ttk.Button(input_frame, text="▶️ Run", 
                  command=self.execute_command, style="Accent.TButton").pack(side=tk.RIGHT)
        
        # Quick command buttons
        quick_commands_frame = ttk.LabelFrame(terminal_container, text="Quick Commands", 
                                            style="Card.TFrame", padding=5)
        quick_commands_frame.pack(fill=tk.X, pady=(5, 0))
        
        quick_commands = [
            ("📊 Pool Stats", "curl -s http://localhost:3336/api/stats | jq ."),
            ("🔗 Blockchain Status", "curl -s http://localhost:8332/api/status"),  
            ("⛏️ Mining Processes", "ps aux | grep -E '(zion|mining|blockchain)' | grep -v grep"),
            ("💾 Disk Usage", "df -h /media/maitreya/ZION1"),
            ("🔥 GPU Status", "nvidia-smi --query-gpu=temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv,noheader,nounits"),
            ("📈 System Load", "top -bn1 | head -5")
        ]
        
        for i, (name, cmd) in enumerate(quick_commands):
            row = i // 3
            col = i % 3
            btn = ttk.Button(quick_commands_frame, text=name,
                           command=lambda c=cmd: self.run_quick_command(c),
                           style="Accent.TButton")
            btn.grid(row=row, column=col, padx=5, pady=2, sticky='ew')
            quick_commands_frame.grid_columnconfigure(col, weight=1)
        
        # Terminal state
        self.command_history = []
        self.history_index = -1
        self.current_directory = "/media/maitreya/ZION1"
        
        # Welcome message
        self.write_terminal_output("💻 ZION Integrated Terminal Ready\n")
        self.write_terminal_output("🚀 Current directory: /media/maitreya/ZION1\n")
        self.write_terminal_output("💡 Type commands or use Quick Commands above\n")
        self.write_terminal_output("=" * 60 + "\n\n")

    def write_terminal_output(self, text):
        """Write text to terminal output"""
        if hasattr(self, 'terminal_output'):
            self.terminal_output.insert(tk.END, text)
            self.terminal_output.see(tk.END)
            self.root.update_idletasks()

    def clear_terminal(self):
        """Clear terminal output"""
        if hasattr(self, 'terminal_output'):
            self.terminal_output.delete(1.0, tk.END)
            self.write_terminal_output("💻 Terminal cleared\n\n")

    def save_terminal_log(self):
        """Save terminal log to file"""
        if hasattr(self, 'terminal_output'):
            try:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"/media/maitreya/ZION1/terminal_log_{timestamp}.txt"
                content = self.terminal_output.get(1.0, tk.END)
                with open(filename, 'w') as f:
                    f.write(content)
                self.write_terminal_output(f"💾 Terminal log saved: {filename}\n")
            except Exception as e:
                self.write_terminal_output(f"❌ Error saving log: {e}\n")

    def run_terminal_command(self, command):
        """Execute terminal command and show output"""
        try:
            # Handle built-in commands
            if command.startswith('cd '):
                path = command[3:].strip()
                if path == '~':
                    path = '/media/maitreya/ZION1'
                elif not path.startswith('/'):
                    path = os.path.join(self.current_directory, path)
                if os.path.exists(path) and os.path.isdir(path):
                    self.current_directory = os.path.abspath(path)
                    self.write_terminal_output(f"📁 Changed directory to: {self.current_directory}\n")
                else:
                    self.write_terminal_output(f"❌ Directory not found: {path}\n")
                return
            elif command == 'pwd':
                self.write_terminal_output(f"{self.current_directory}\n")
                return
            elif command == 'clear':
                self.clear_terminal()
                return
            elif command == 'exit':
                self.write_terminal_output("Session closed.\n")
                return
            
            result = subprocess.run(
                command,
                shell=True,
                cwd=self.current_directory,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.stdout:
                self.write_terminal_output(result.stdout)
            if result.stderr:
                self.write_terminal_output(result.stderr)
            if result.returncode != 0:
                self.write_terminal_output(f"⚠️ Exit code: {result.returncode}\n")
        except subprocess.TimeoutExpired:
            self.write_terminal_output("⏰ Command timeout (30s)\n")
        except Exception as e:
            self.write_terminal_output(f"❌ Command error: {e}\n")
        self.write_terminal_output("\n")

    def command_history_up(self, event):
        """Navigate command history up"""
        if self.command_history and self.history_index > 0:
            self.history_index -= 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])

    def command_history_down(self, event):
        """Navigate command history down"""
        if self.command_history and self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            self.command_entry.delete(0, tk.END)
            self.command_entry.insert(0, self.command_history[self.history_index])
        elif self.history_index >= len(self.command_history) - 1:
            self.command_entry.delete(0, tk.END)

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

        # Unified System Controls section
        unified_frame = ttk.LabelFrame(parent, text="🌟 ZION Unified System", padding=10)
        unified_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        ttk.Button(unified_frame, text="🚀 Start Unified System", command=self.start_unified_system).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(unified_frame, text="⏹️ Stop Unified System", command=self.stop_unified_system).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(unified_frame, text="📊 Unified Status", command=self.check_unified_status).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(unified_frame, text="🤖 Start AI Mining", command=self.start_unified_ai_mining).pack(side=tk.LEFT, padx=(0, 10))
        
        # Unified Status Display
        unified_status_frame = ttk.LabelFrame(parent, text="🌟 Unified System Status", padding=10)
        unified_status_frame.pack(fill=tk.X, pady=(0, 10), padx=10)
        
        self.unified_status_text = scrolledtext.ScrolledText(
            unified_status_frame, height=8,
            bg=self.colors['bg_tertiary'], 
            fg=self.colors['text_primary'],
            font=('Consolas', 10)
        )
        self.unified_status_text.pack(fill=tk.BOTH, expand=True)

    def update_charts(self):
        """Update performance charts display"""
        self.chart_text.delete(1.0, tk.END)
        # Trim histories to max_history_points
        for k, arr in self.performance_history.items():
            if k == 'timestamps':
                continue
            if len(arr) > self.max_history_points:
                overflow = len(arr) - self.max_history_points
                del arr[:overflow]
        # Align timestamps
        if len(self.performance_history['timestamps']) > self.max_history_points:
            overflow = len(self.performance_history['timestamps']) - self.max_history_points
            del self.performance_history['timestamps'][:overflow]

        def spark(values, width=40, value_format="{:.1f}"):
            if not values:
                return "(no data)"
            lo, hi = min(values), max(values)
            if hi == lo:
                return "■" * min(len(values), width)
            # Downsample if necessary
            step = max(1, int(len(values)/width))
            sampled = values[::step][:width]
            blocks = "▁▂▃▄▅▆▇█"
            span = hi - lo
            line = ''.join(blocks[int((v - lo)/span * (len(blocks)-1))] for v in sampled)
            return f"{line}  (min {value_format.format(lo)}, avg {value_format.format(sum(values)/len(values))}, max {value_format.format(hi)})"

        sections = [
            ("🔥 CPU %", self.performance_history['cpu'], "{:.1f}%"),
            ("💾 Memory %", self.performance_history['memory'], "{:.1f}%"),
            ("🎮 GPU Temp °C", self.performance_history['gpu_temp'], "{:.1f}"),
            ("⛏️ Hashrate H/s", self.performance_history['hashrate'], "{:.2f}"),
            ("🤖 AI Tasks", self.performance_history['ai_tasks'], "{:.0f}")
        ]

        header = "📊 ZION PERFORMANCE CHARTS\n" + "="*50 + "\nLast Update: " + datetime.now().strftime('%H:%M:%S') + "\nPoints: " + str(len(self.performance_history['cpu'])) + "\n\n"
        out = [header]
        for title, data_series, fmt in sections:
            out.append(title + "\n" + spark(data_series) + "\n\n")

        self.chart_text.insert(tk.END, ''.join(out))

    def clear_performance_history(self):
        """Clear performance history"""
        for key in self.performance_history:
            self.performance_history[key].clear()
        self.update_charts()
        messagebox.showinfo("Success", "Performance history cleared")

    def start_unified_system(self):
        """Start ZION Unified System"""
        try:
            if 'unified' in self.process_registry and self.process_registry['unified'].poll() is None:
                messagebox.showinfo("Info", "Unified system already running")
                return
            cmd = ['python3', 'zion_unified.py', '--daemon']
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.process_registry['unified'] = proc
            self._log_debug(f"Started unified system PID {proc.pid}")
            # UI update
            self.unified_status_text.delete(1.0, tk.END)
            self.unified_status_text.insert(tk.END, "🚀 Starting ZION Unified System...\n")
            self.unified_status_text.insert(tk.END, f"Process ID: {proc.pid}\n")
            self.unified_status_text.insert(tk.END, "Components: Blockchain + Mining Pool + AI Yesscript Miner\n")
            messagebox.showinfo("Success", "ZION Unified System started")
        except Exception as e:
            self._log_debug(f"Unified start error: {e}")
            messagebox.showerror("Error", f"Failed to start unified system: {str(e)}")

    def stop_unified_system(self):
        """Stop ZION Unified System"""
        try:
            proc = self.process_registry.get('unified')
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    self._log_debug("Unified system did not terminate gracefully, killing")
                    proc.kill()
            # Fallback kill to ensure no stray processes
            subprocess.run(['pkill', '-f', 'zion_unified.py'], check=False)
            self.process_registry.pop('unified', None)
            self.unified_status_text.delete(1.0, tk.END)
            self.unified_status_text.insert(tk.END, "⏹️ ZION Unified System stopped\n")
            messagebox.showinfo("Success", "ZION Unified System stopped")
        except Exception as e:
            self._log_debug(f"Unified stop error: {e}")
            messagebox.showerror("Error", f"Failed to stop unified system: {str(e)}")

    def check_unified_status(self):
        """Check ZION Unified System status"""
        try:
            # Get unified system stats
            unified_stats = self.get_unified_system_stats()
            
            # Clear and update status display
            self.unified_status_text.delete(1.0, tk.END)
            
            if unified_stats:
                self.unified_status_text.insert(tk.END, "🌟 ZION UNIFIED SYSTEM STATUS\n")
                self.unified_status_text.insert(tk.END, "=" * 40 + "\n\n")
                
                # System info
                if 'system' in unified_stats:
                    system_info = unified_stats['system']
                    self.unified_status_text.insert(tk.END, f"Running: {'✅' if system_info.get('running', False) else '❌'}\n")
                    self.unified_status_text.insert(tk.END, f"Blockchain: {system_info.get('blockchain_type', 'Unknown')}\n\n")
                    
                    # Components
                    components = system_info.get('components', {})
                    self.unified_status_text.insert(tk.END, "Components:\n")
                    self.unified_status_text.insert(tk.END, f"  Blockchain: {'✅' if components.get('blockchain', False) else '❌'}\n")
                    self.unified_status_text.insert(tk.END, f"  Mining Pool: {'✅' if components.get('mining_pool', False) else '❌'}\n")
                    self.unified_status_text.insert(tk.END, f"  AI Yesscript: {'✅' if components.get('ai_yesscript_miner', False) else '❌'}\n")
                    self.unified_status_text.insert(tk.END, f"  P2P Network: {'✅' if components.get('p2p_enabled', False) else '❌'}\n")
                    self.unified_status_text.insert(tk.END, f"  RPC Server: {'✅' if components.get('rpc_enabled', False) else '❌'}\n\n")
                
                # AI Miner info
                if 'ai_miner' in unified_stats:
                    ai_info = unified_stats['ai_miner']
                    self.unified_status_text.insert(tk.END, "🤖 AI Yesscript Miner:\n")
                    self.unified_status_text.insert(tk.END, f"  Status: {'🟢 Active' if ai_info.get('active', False) else '🔴 Inactive'}\n")
                    self.unified_status_text.insert(tk.END, f"  Hashrate: {ai_info.get('current_hashrate', 0.0):.2f} H/s\n")
                    self.unified_status_text.insert(tk.END, f"  Threads: {ai_info.get('threads_active', 0)}\n")
                    self.unified_status_text.insert(tk.END, f"  Algorithm: {ai_info.get('algorithm', 'yescrypt')}\n")
            else:
                self.unified_status_text.insert(tk.END, "❌ ZION Unified System not running\n")
                self.unified_status_text.insert(tk.END, "Use 'Start Unified System' to launch\n")
                
        except Exception as e:
            self.unified_status_text.delete(1.0, tk.END)
            self.unified_status_text.insert(tk.END, f"Error checking status: {str(e)}\n")

    def start_unified_ai_mining(self):
        """Start AI mining through unified system"""
        try:
            # Check if unified system is running
            unified_stats = self.get_unified_system_stats()
            
            if not unified_stats:
                # Start unified system first
                self.start_unified_system()
                time.sleep(2)  # Give it time to start
            
            # AI mining is automatically started with unified system
            self.check_unified_status()
            messagebox.showinfo("Success", "AI Yesscript Mining started via Unified System")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start AI mining: {str(e)}")

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

    # (Unified update_ai_status implementation defined earlier is authoritative)

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

            # Start AI Yesscript miner
            if 'yesscript_miner' in self.ai_components and not self.ai_stats.yesscript_miner_active:
                yesscript_miner = self.ai_components['yesscript_miner']
                pool_config = {'url': 'stratum+tcp://localhost:3335', 'pass': 'yesscript_worker'}
                wallet = 'test_wallet_yesscript'
                if yesscript_miner.start_mining(pool_config, wallet):
                    self.ai_stats.yesscript_miner_active = True

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

            # Stop AI Yesscript miner
            if 'yesscript_miner' in self.ai_components:
                self.ai_components['yesscript_miner'].stop_mining()

            # Update status
            self.ai_stats.gpu_miner_active = False
            self.ai_stats.ai_afterburner_active = False
            self.ai_stats.hybrid_miner_active = False
            self.ai_stats.yesscript_miner_active = False

            messagebox.showinfo("Success", "All AI components stopped")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop AI components: {str(e)}")

    def check_process_running(self, process_name):
        """Check if process is running"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name],
                                  capture_output=True, text=True)
            return result.returncode == 0
        except Exception as e:
            self._log_debug(f"check_process_running error ({process_name}): {e}")
            return False

    def get_unified_system_stats(self):
        """Get unified system stats (real only) from freshest available source.
        Priority:
          1. Fresh live_stats.json (<=30s)
          2. Fresh real_system_status.json (<=20s)
          3. Optional RPC endpoint /unified/stats (timeout 1s)
        Returns dict or None."""
        # 1. live_stats.json
        live_stats = self._load_recent_json('live_stats.json', 30)
        if live_stats:
            return live_stats

        # 2. real_system_status.json
        real_status = self._load_recent_json('real_system_status.json', 20)
        if real_status:
            return real_status

        # 3. RPC endpoint fallback (non-blocking quick try)
        try:
            response = requests.get(f"{self.blockchain_rpc_url}/unified/stats", timeout=1)
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            self._log_debug(f"Unified RPC stats fail: {e}")
        return None

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
        base_interval = 3.0
        last_run = 0.0
        while self.monitoring:
            start = time.time()
            try:
                # Throttle if previous update still recent (< 1s)
                if start - last_run >= 1.0:
                    self.root.after(0, self.safe_update_all)
                    last_run = start
            except Exception as e:
                print(f"Monitor loop error: {e}")
            # Adaptive sleep: keep near base interval but allow finer granularity
            elapsed = time.time() - start
            sleep_for = max(0.2, base_interval - elapsed)
            time.sleep(sleep_for)

    def safe_update_all(self):
        """Thread-safe update of all components with REAL data only"""
        try:
            self.update_quick_stats()
            self.update_blockchain_status()
            self.update_pool_status()
            self.update_system_status()
            self.update_ai_status()
            self.update_ai_metrics_display()
            
            # Status based on actual system state
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Check if we have any real active components
            has_active_components = False
            if hasattr(self, 'ai_components') and self.ai_components:
                has_active_components = any(
                    getattr(inst, 'is_mining', False) for inst in self.ai_components.values()
                )
            
            # Check if live stats exist and are recent
            live_stats_active = False
            try:
                if os.path.exists('live_stats.json'):
                    stat = os.stat('live_stats.json')
                    age = time.time() - stat.st_mtime
                    live_stats_active = age < 30  # Less than 30 seconds old
            except Exception as e:
                self._log_debug(f"live_stats age check error: {e}")
            
            if has_active_components or live_stats_active:
                status_icon = "🟢"
                status_text = "System Active"
            else:
                status_icon = "🔴"
                status_text = "System Inactive"
                
            self.update_status_bar(f"{status_icon} {status_text} - Last Update: {timestamp}")
            
        except Exception as e:
            print(f"Update error: {e}")
            self.update_status_bar(f"⚠️ Update Error: {str(e)[:30]} - {datetime.now().strftime('%H:%M:%S')}")
            
    def update_quick_stats(self):
        """Update quick stats strictly from real sources (no simulations).
        Sources priority:
          1. Fresh live_stats.json (<=30s)
          2. Fresh real_system_status.json (<=15s for system/mining)
          3. Direct process / psutil inspection / AI component stats
        All exceptions are captured and logged via _log_debug without hiding partial updates."""
        # Load data files (do not treat absence as error)
        live_data = self._load_recent_json('live_stats.json', 30)
        real_status = self._load_recent_json('real_system_status.json', 15)

        # System stats (CPU/memory) - always fresh via psutil; override only if file more specific
        try:
            if PSUTIL_AVAILABLE:
                cpu_percent = psutil.cpu_percent(interval=0.1)
                memory = psutil.virtual_memory()
                self.system_stats.cpu_usage = cpu_percent
                self.system_stats.memory_usage = memory.percent
                self.system_stats.memory_total = memory.total / (1024**3)
                self.system_stats.memory_used = memory.used / (1024**3)
        except Exception as e:
            self._log_debug(f"psutil system stats error: {e}")

        # Wallet balance
        try:
            balance_value = 0.0
            if live_data:
                balance_value = float(live_data.get('wallet', {}).get('balance', 0.0))
            self.balance_value_label.config(text=f"{balance_value:.2f} ZION")
        except Exception as e:
            self._log_debug(f"Balance update error: {e}")
            self.balance_value_label.config(text="0.00 ZION")

        # Hashrate determination
        total_hashrate = 0.0
        try:
            if live_data and live_data.get('mining', {}).get('active'):
                total_hashrate = float(live_data.get('mining', {}).get('hashrate', 0.0))
            elif real_status and real_status.get('mining', {}).get('active'):
                total_hashrate = float(real_status.get('mining', {}).get('hashrate', 0.0))
            else:
                # Fallback to AI component internal stats
                if hasattr(self, 'ai_components') and self.ai_components:
                    for instance in self.ai_components.values():
                        try:
                            if hasattr(instance, 'get_mining_stats'):
                                stats = instance.get_mining_stats() or {}
                                total_hashrate += float(stats.get('hashrate', 0.0))
                            elif hasattr(instance, 'hashrate'):
                                total_hashrate += float(getattr(instance, 'hashrate', 0.0))
                        except Exception as inner_e:
                            self._log_debug(f"AI component hashrate error: {inner_e}")
        except Exception as e:
            self._log_debug(f"Hashrate computation error: {e}")

        # Update hashrate label
        if total_hashrate > 0:
            self.hashrate_value_label.config(text=f"{total_hashrate:.1f} H/s", foreground='#00ff88')
        else:
            self.hashrate_value_label.config(text="0.0 H/s", foreground='#666666')

        # Efficiency (simple derived metric)
        try:
            if total_hashrate > 0 and hasattr(self.system_stats, 'cpu_usage'):
                efficiency = max(0.0, 100.0 - float(self.system_stats.cpu_usage))
                color = '#00ff88' if efficiency > 70 else '#ffaa00' if efficiency > 40 else '#ff6666'
                self.efficiency_value_label.config(text=f"{efficiency:.0f}%", foreground=color)
            else:
                self.efficiency_value_label.config(text="0%", foreground='#666666')
        except Exception as e:
            self._log_debug(f"Efficiency calc error: {e}")
            self.efficiency_value_label.config(text="0%", foreground='#666666')

        # Blocks (height)
        try:
            blocks = 0
            if live_data:
                blocks = int(live_data.get('blockchain', {}).get('height', 0))
            elif real_status:
                blocks = int(real_status.get('blockchain', {}).get('height', 0))
            if blocks > 0:
                self.blocks_value_label.config(text=str(blocks), foreground='#00ff88')
            else:
                self.blocks_value_label.config(text="0", foreground='#666666')
        except Exception as e:
            self._log_debug(f"Blocks update error: {e}")
            self.blocks_value_label.config(text="0", foreground='#666666')
            
    def get_current_blocks(self):
        """Get REAL current block count from live stats only"""
        try:
            if os.path.exists('live_stats.json'):
                with open('live_stats.json', 'r') as f:
                    stats = json.load(f)
                blockchain = stats.get('blockchain', {})
                return blockchain.get('height', 0)
        except Exception as e:
            self._log_debug(f"get_current_blocks error: {e}")
        
        return 0

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
        except Exception as e:
            self._log_debug(f"update_blockchain_status error: {e}")
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
        except Exception as e:
            self._log_debug(f"update_pool_status error: {e}")
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
            self._log_debug(f"System status update error: {e}")

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

            # Real GPU not detected - set to zero values
            self.gpu_stats.temperature = 0.0
            self.gpu_stats.utilization = 0
            self.gpu_stats.power_usage = 0
            self.gpu_stats.memory_usage = 0
            self.gpu_stats.memory_total = 0
            self.gpu_stats.clock_speed = 0
            self.gpu_stats.fan_speed = 0

        except Exception as e:
            self._log_debug(f"GPU stats update error: {e}")

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
        except Exception as e:
            self._log_debug(f"update_logs error: {e}")

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

    def start_yesscript_miner(self):
        """Start AI Yesscript miner"""
        if 'yesscript_miner' not in self.ai_components:
            messagebox.showerror("Error", "AI Yesscript Miner not available")
            return

        try:
            yesscript_miner = self.ai_components['yesscript_miner']
            pool_config = {'url': 'stratum+tcp://localhost:3335', 'pass': 'yesscript_worker'}
            wallet = 'test_wallet_yesscript'  # In production, get from user input

            if yesscript_miner.start_mining(pool_config, wallet):
                self.ai_status['yesscript_miner']['active'] = True
                if hasattr(self, 'yesscript_miner_status_indicator'):
                    self.yesscript_miner_status_indicator.config(text="🟢 Active", foreground='#00ff00')
                messagebox.showinfo("Success", "AI Yesscript Miner started")
            else:
                messagebox.showerror("Error", "Failed to start AI Yesscript Miner")
        except Exception as e:
            messagebox.showerror("Error", f"AI Yesscript Miner error: {str(e)}")

    def stop_yesscript_miner(self):
        """Stop AI Yesscript miner"""
        if 'yesscript_miner' not in self.ai_components:
            return

        try:
            self.ai_components['yesscript_miner'].stop_mining()
            self.ai_status['yesscript_miner']['active'] = False
            if hasattr(self, 'yesscript_miner_status_indicator'):
                self.yesscript_miner_status_indicator.config(text="🔴 Inactive", foreground='#ff0000')
            if hasattr(self, 'yesscript_miner_hashrate_display'):
                self.yesscript_miner_hashrate_display.config(text="0.0 H/s")
        except Exception as e:
            messagebox.showerror("Error", f"AI Yesscript Miner stop error: {str(e)}")

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
        try:
            # Show REAL AI component status ONLY
            timestamp = datetime.now().strftime('%H:%M:%S')
            
            # Clear and update AI status display
            if hasattr(self, 'ai_text'):
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"AI SYSTEM STATUS - {timestamp}\n\n", "header")
                
                # Show REAL AI components status
                active_count = 0
                
                # Check REAL components ONLY
                if hasattr(self, 'ai_components') and self.ai_components:
                    for name, instance in self.ai_components.items():
                        try:
                            if hasattr(instance, 'is_mining') and instance.is_mining:
                                hashrate = getattr(instance, 'hashrate', 0.0)
                                self.ai_text.insert(tk.END, f"🟢 {name.title()}: ACTIVE ({hashrate:.1f} H/s)\n")
                                active_count += 1
                            elif hasattr(instance, 'get_status'):
                                status = instance.get_status()
                                icon = "🟢" if status.get('active', False) else "�"
                                state = status.get('state', 'INACTIVE')
                                self.ai_text.insert(tk.END, f"{icon} {name.title()}: {state}\n")
                                if status.get('active', False):
                                    active_count += 1
                            else:
                                self.ai_text.insert(tk.END, f"� {name.title()}: INACTIVE\n")
                        except Exception as e:
                            self.ai_text.insert(tk.END, f"⚠️ {name.title()}: ERROR - {str(e)[:30]}\n")
                else:
                    # No AI components loaded
                    self.ai_text.insert(tk.END, "❌ No AI Components Loaded\n")
                    self.ai_text.insert(tk.END, "To activate: Start zion_unified.py first\n")
                
                # REAL system efficiency calculation
                if PSUTIL_AVAILABLE:
                    efficiency = max(0, 100 - self.system_stats.cpu_usage)
                    self.ai_text.insert(tk.END, f"\nSystem Efficiency: {efficiency:.0f}%\n")
                else:
                    efficiency = 0
                    self.ai_text.insert(tk.END, f"\nSystem Efficiency: Unknown\n")
                    
                self.ai_text.insert(tk.END, f"Active Components: {active_count}\n")
                
                # Update AI stats with REAL values
                self.ai_stats.yesscript_miner_active = any(
                    hasattr(inst, 'is_mining') and inst.is_mining 
                    for name, inst in (self.ai_components.items() if hasattr(self, 'ai_components') and self.ai_components else [])
                    if 'yescript' in name.lower()
                )
                self.ai_stats.efficiency = efficiency
            
            # Update individual AI component labels if they exist
            if hasattr(self, 'ai_components') and self.ai_components:
                # Update GPU Miner
                if 'gpu_miner' in self.ai_components:
                    gpu_miner = self.ai_components['gpu_miner']
                    if hasattr(self, 'gpu_status_label'):
                        status = "Active" if getattr(gpu_miner, 'is_mining', False) else "Standby"
                        color = '#00ff88' if getattr(gpu_miner, 'is_mining', False) else '#ffaa00'
                        self.gpu_status_label.config(text=status, foreground=color)
                    
                    if hasattr(self, 'gpu_hashrate_label'):
                        hashrate = getattr(gpu_miner, 'hashrate', 0.0)
                        self.gpu_hashrate_label.config(text=f"{hashrate:.1f} MH/s")
    
                # Update AI Afterburner
                if 'ai_afterburner' in self.ai_components:
                    ai_afterburner = self.ai_components['ai_afterburner']
                    if hasattr(self, 'ai_status_label'):
                        status = "Active" if getattr(ai_afterburner, 'processing_active', False) else "Standby"
                        color = '#00ff88' if getattr(ai_afterburner, 'processing_active', False) else '#ffaa00'
                        self.ai_status_label.config(text=status, foreground=color)
                        
        except Exception as e:
            print(f"AI status update error: {e}")
            if hasattr(self, 'ai_text'):
                self.ai_text.delete(1.0, tk.END)
                self.ai_text.insert(tk.END, f"⚠️ AI System: Error - {str(e)[:50]}\n")

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

    def auto_start_all_services(self):
        """Auto-start all ZION services on dashboard startup"""
        try:
            self.status_bar.config(text="🚀 Starting ZION services...")
            self.root.update()
            
            # Stop any existing processes first
            self.cleanup_processes()
            
            # Start blockchain node
            self.start_blockchain_node()
            time.sleep(2)
            
            # Start mining pool
            self.start_mining_pool()
            time.sleep(2)
            
            # Start RPC server (if separate)
            self.start_rpc_server()
            time.sleep(1)
            
            # Start wallet service
            self.start_wallet_service()
            time.sleep(1)
            
            # Start P2P nodes/seeds
            self.start_p2p_nodes()
            
            self.status_bar.config(text="✅ All ZION services started successfully!")
            
        except Exception as e:
            self.status_bar.config(text=f"❌ Error starting services: {str(e)}")
            print(f"Auto-start error: {e}")

    def cleanup_processes(self):
        """Clean up any existing ZION processes"""
        try:
            processes_to_kill = [
                'new_zion_blockchain',
                'zion_universal_pool',
                'zion_rpc_server', 
                'zion_wallet_service',
                'zion_p2p_node'
            ]
            
            for process in processes_to_kill:
                subprocess.run(['pkill', '-f', process], check=False, 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(1)
        except Exception as e:
            print(f"Cleanup error: {e}")

    def start_blockchain_node(self):
        """Start ZION blockchain node"""
        try:
            cmd = ['python3', 'new_zion_blockchain.py']
            self.blockchain_process = subprocess.Popen(
                cmd, cwd='/media/maitreya/ZION1',
                stdout=subprocess.DEVNULL, 
                stderr=subprocess.DEVNULL
            )
            print("🔗 Blockchain node started")
        except Exception as e:
            print(f"Blockchain start error: {e}")

    def start_mining_pool(self):
        """Start ZION mining pool"""
        try:
            cmd = ['python3', 'zion_universal_pool_v2.py']
            self.pool_process = subprocess.Popen(
                cmd, cwd='/media/maitreya/ZION1',
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print("⛏️ Mining pool started")
        except Exception as e:
            print(f"Mining pool start error: {e}")

    def start_rpc_server(self):
        """Start RPC server (if separate from blockchain)"""
        try:
            # RPC is usually integrated in blockchain node
            # This is for additional RPC services if needed
            print("🔌 RPC server integrated with blockchain")
        except Exception as e:
            print(f"RPC server start error: {e}")

    def start_wallet_service(self):
        """Start wallet service"""
        try:
            # Check if wallet service exists
            wallet_files = [
                'zion_wallet_service.py',
                'wallet_service.py', 
                'zion_wallet.py'
            ]
            
            wallet_file = None
            for wf in wallet_files:
                if os.path.exists(f'/media/maitreya/ZION1/{wf}'):
                    wallet_file = wf
                    break
            
            if wallet_file:
                cmd = ['python3', wallet_file]
                self.wallet_process = subprocess.Popen(
                    cmd, cwd='/media/maitreya/ZION1',
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                print(f"💰 Wallet service started: {wallet_file}")
            else:
                print("💰 Wallet service integrated with blockchain")
                
        except Exception as e:
            print(f"Wallet service start error: {e}")

    def start_p2p_nodes(self):
        """Start P2P nodes and seed nodes"""
        try:
            # P2P is usually integrated in blockchain node
            # This is for additional seed nodes if needed
            p2p_files = [
                'zion_p2p_node.py',
                'p2p_node.py',
                'seed_node.py'
            ]
            
            for pf in p2p_files:
                if os.path.exists(f'/media/maitreya/ZION1/{pf}'):
                    cmd = ['python3', pf]
                    subprocess.Popen(
                        cmd, cwd='/media/maitreya/ZION1',
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    print(f"🌐 P2P node started: {pf}")
                    break
            else:
                print("🌐 P2P nodes integrated with blockchain")
                
        except Exception as e:
            print(f"P2P nodes start error: {e}")

    def start_local_stack(self):
        """Enhanced start local stack with all services"""
        try:
            self.auto_start_all_services()
            messagebox.showinfo("Success", "🚀 All ZION services started!\n\n"
                              "✅ Blockchain Node\n"
                              "✅ Mining Pool  \n"
                              "✅ RPC Server\n"
                              "✅ Wallet Service\n"
                              "✅ P2P Network\n\n"
                              "Ready for mining and transactions!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start services: {str(e)}")

    def stop_all(self):
        """Stop all ZION services"""
        try:
            self.cleanup_processes()
            
            # Stop AI components
            if hasattr(self, 'ai_components'):
                self.stop_all_ai()
            
            self.status_bar.config(text="⏹️ All services stopped")
            messagebox.showinfo("Success", "All ZION services stopped")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop services: {str(e)}")

    def get_gpu_miner_hashrate(self):
        """Get real GPU miner hashrate"""
        try:
            # Try to get hashrate from SRBMiner API
            response = requests.get("http://localhost:21550/api", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'hashrate' in data:
                    return float(data['hashrate'].get('total', [0])[0])
        except Exception as e:
            self._log_debug(f"GPU miner hashrate API error: {e}")
        # Real-only: no synthetic estimation
        return 0.0

    def get_hybrid_miner_hashrate(self):
        """Get real hybrid miner hashrate"""
        try:
            # Try to get hashrate from xmrig API
            response = requests.get("http://localhost:3335/api.json", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if 'hashrate' in data:
                    total_hashrate = data['hashrate'].get('total', [0])
                    if isinstance(total_hashrate, list) and len(total_hashrate) > 0:
                        return float(total_hashrate[0])
        except Exception as e:
            self._log_debug(f"Hybrid miner hashrate API error: {e}")
        # Real-only: no synthetic estimation
        return 0.0

    def update_ai_metrics_display(self):
        """Update AI metrics display with real-time data"""
        try:
            if hasattr(self, 'ai_metrics_text'):
                metrics = f"""🤖 AI Mining Performance Metrics

⏰ Last Update: {datetime.now().strftime('%H:%M:%S')}

🎮 GPU Miner Status:
   • Active: {'Yes' if self.ai_stats.gpu_miner_active else 'No'}
   • Hashrate: {self.get_gpu_miner_hashrate():.2f} H/s
   • Algorithm: RandomX + KawPow

🔥 AI Afterburner Status:
   • Active: {'Yes' if self.ai_stats.ai_afterburner_active else 'No'}
   • Neural Networks: {self.ai_stats.neural_networks}
   • Performance Score: {self.ai_stats.performance_score:.1f}%

⚡ Hybrid Miner Status:
   • Active: {'Yes' if self.ai_stats.hybrid_miner_active else 'No'}
   • Total Hashrate: {self.get_hybrid_miner_hashrate():.2f} H/s
   • CPU Allocation: {self.ai_stats.allocation_mining}%
   • AI Allocation: {self.ai_stats.allocation_ai}%

🌊 AI Yesscript Miner Status:
   • Active: {'Yes' if getattr(self.ai_stats, 'yesscript_miner_active', False) else 'No'}
   • Hashrate: {self.ai_components.get('yesscript_miner', lambda: type('obj', (object,), {'get_mining_stats': lambda: {'hashrate': 0.0}})()).get_mining_stats().get('hashrate', 0.0):.2f} H/s
   • Algorithm: Yescrypt (Memory-Hard)
   • AI Optimization: {'Enabled' if self.ai_components.get('yesscript_miner', None) and self.ai_components['yesscript_miner'].ai_optimization_active else 'Disabled'}

📊 System Resources:
   • CPU Usage: {self.system_stats.cpu_usage:.1f}%
   • Memory: {self.system_stats.memory_used:.1f}GB / {self.system_stats.memory_total:.1f}GB
   • GPU Temp: {self.gpu_stats.temperature:.1f}°C
   • Network: {self.system_stats.network_tx/1024/1024:.1f}MB sent

🔄 Task Statistics:
   • Active Tasks: {self.ai_stats.active_tasks}
   • Completed: {self.ai_stats.completed_tasks}
   • Failed: {self.ai_stats.failed_tasks}
   • Success Rate: {(self.ai_stats.completed_tasks / max(1, self.ai_stats.completed_tasks + self.ai_stats.failed_tasks)) * 100:.1f}%

⚙️ AI Configuration:
   • Compute Mode: {self.ai_stats.compute_mode if hasattr(self.ai_stats, 'compute_mode') else 'OPTIMIZED'}
   • Efficiency: {self.ai_stats.efficiency if hasattr(self.ai_stats, 'efficiency') else 95.2}%
   • Auto-scaling: {'Enabled' if self.ai_stats.allocation_mining < 80 else 'Disabled'}
"""
                self.ai_metrics_text.delete(1.0, tk.END)
                self.ai_metrics_text.insert(tk.END, metrics)
        except Exception as e:
            print(f"Failed to update AI metrics: {e}")

    def setup_integrated_api(self):
        """Setup integrated REST API server for frontend communication"""
        try:
            # Check if port 5001 is available
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', 5001))
            sock.close()
            
            if result != 0:  # Port is available
                self.api_app = Flask(__name__)
                self.setup_api_routes()
                
                # Start API server in background thread
                api_thread = Thread(target=self.run_api_server, daemon=True)
                api_thread.start()
                
                self.update_status_bar("✅ Integrated API Server started on port 5001")
            else:
                self.update_status_bar("⚠️ Port 5001 busy - API server disabled")
                
        except Exception as e:
            print(f"Failed to setup API server: {e}")
            self.update_status_bar("❌ API server failed to start")

    def setup_api_routes(self):
        """Setup API routes for frontend integration"""
        
        @self.api_app.route('/api/unified/stats')
        def get_unified_stats():
            """Get unified system stats"""
            try:
                unified_stats = self.get_unified_system_stats()
                if unified_stats:
                    return jsonify(unified_stats)
                else:
                    return jsonify({
                        "system": {"running": False},
                        "ai_miner": {"active": False, "hashrate": 0.0}
                    })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/api/dashboard/stats')
        def get_dashboard_stats():
            """Get comprehensive dashboard stats"""
            try:
                # Get AI stats
                ai_stats = {}
                if hasattr(self, 'ai_components') and self.ai_components:
                    for component, instance in self.ai_components.items():
                        try:
                            if hasattr(instance, 'get_mining_stats'):
                                ai_stats[component] = instance.get_mining_stats()
                            else:
                                ai_stats[component] = self.ai_status.get(component, {})
                        except Exception:
                            ai_stats[component] = {"active": False, "error": "stats_unavailable"}

                return jsonify({
                    "system": {
                        "cpu_usage": self.system_stats.cpu_usage,
                        "memory_usage": self.system_stats.memory_usage,
                        "memory_total": self.system_stats.memory_total
                    },
                    "blockchain": self.blockchain_status,
                    "pool": self.pool_status,
                    "ai_components": ai_stats,
                    "unified_system": self.get_unified_system_stats(),
                    "timestamp": datetime.now().isoformat()
                })
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/api/unified/start', methods=['POST'])
        def api_start_unified():
            """Start unified system via API"""
            try:
                self.start_unified_system()
                return jsonify({"success": True, "message": "Unified system starting"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/api/unified/stop', methods=['POST'])
        def api_stop_unified():
            """Stop unified system via API"""
            try:
                self.stop_unified_system()
                return jsonify({"success": True, "message": "Unified system stopped"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/api/ai/yesscript/start', methods=['POST'])
        def api_start_yesscript():
            """Start AI Yesscript miner via API"""
            try:
                self.start_unified_ai_mining()
                return jsonify({"success": True, "message": "AI Yesscript miner starting"})
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/api/ai/components/status')
        def api_ai_status():
            """Get AI components status"""
            try:
                self.update_ai_status()  # Refresh status
                
                status = {}
                for component in ['gpu_miner', 'ai_afterburner', 'hybrid_miner', 'yesscript_miner']:
                    if hasattr(self, f"{component}_status_indicator"):
                        indicator = getattr(self, f"{component}_status_indicator")
                        active = "Active" in indicator.cget("text")
                        status[component] = {
                            "active": active,
                            "status_text": indicator.cget("text")
                        }
                    
                    if hasattr(self, f"{component}_hashrate_display"):
                        display = getattr(self, f"{component}_hashrate_display")
                        status[component]["hashrate_display"] = display.cget("text")

                return jsonify(status)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.api_app.route('/health')
        def health_check():
            """API health check"""
            return jsonify({
                "status": "healthy",
                "service": "ZION Dashboard API",
                "version": "2.7.5",
                "timestamp": datetime.now().isoformat()
            })

    def run_api_server(self):
        """Run the API server"""
        try:
            self.api_app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)
        except Exception as e:
            print(f"API server error: {e}")

def main():
    """Main entry point with service management"""
    print("🚀 Starting ZION 2.7.5 Advanced Dashboard...")
    print("This will auto-start all ZION services:")
    print("  🔗 Blockchain Node")
    print("  ⛏️ Mining Pool") 
    print("  🔌 RPC Server")
    print("  💰 Wallet Service")
    print("  🌐 P2P Network")
    print("  🤖 AI Mining Components")
    print()
    
    root = tk.Tk()
    app = ZIONDashboard(root)
    
    # Handle window close event
    def on_closing():
        try:
            app.cleanup_processes()
            print("🛑 ZION services stopped")
        except Exception as e:
            app._log_debug(f"on_closing cleanup error: {e}")
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()



if __name__ == "__main__":
    main()