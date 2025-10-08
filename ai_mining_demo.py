#!/usr/bin/env python3
"""
🚀 ZION AI Mining Demo Script 🚀
Demonstrates AI mining components integration
"""

import sys
import os
import time

# Add paths
sys.path.append('.')
sys.path.append('./ai')

def demo_ai_mining():
    """Demonstrate AI mining components"""
    print("🚀 ZION 2.7.5 AI MINING DEMO")
    print("=" * 50)

    try:
        # Import AI components
        from ai.zion_gpu_miner import ZionGPUMiner
        from ai.zion_ai_afterburner import ZionAIAfterburner, ComputeMode
        from ai.zion_hybrid_miner import ZionHybridMiner

        print("🤖 Initializing AI Mining Components...")

        # Initialize components
        gpu_miner = ZionGPUMiner()
        ai_afterburner = ZionAIAfterburner()
        hybrid_miner = ZionHybridMiner()

        print("✅ AI Components initialized successfully")
        print()

        # Demo GPU Miner
        print("🎮 GPU MINER DEMO:")
        print(f"  GPU Available: {gpu_miner.gpu_available}")
        print(f"  Benchmark Hashrate: {gpu_miner.benchmark_hashrate:.1f} MH/s")
        print(f"  SRBMiner Found: {gpu_miner.srbminer_path is not None}")
        print(f"  Current Algorithm: {gpu_miner.current_algorithm}")
        print()

        # Demo AI Afterburner
        print("🔥 AI AFTERBURNER DEMO:")
        print(f"  Compute Mode: {ai_afterburner.compute_mode.value}")
        print(f"  Total Compute Power: {ai_afterburner.total_compute_power} MH/s")
        print(f"  Sacred Enhancement: {ai_afterburner.sacred_enhancement_active}")
        print(f"  Available Compute: {ai_afterburner.available_compute} MH/s")
        print()

        # Demo Hybrid Miner
        print("⚡ HYBRID MINER DEMO:")
        print(f"  Hybrid Mode: {hybrid_miner.hybrid_mode}")
        print(f"  AI Optimization: {hybrid_miner.ai_optimization_active}")
        print(f"  CPU Algorithm: {hybrid_miner.current_cpu_algorithm}")
        print(f"  Xmrig Found: {hybrid_miner.xmrig_path is not None}")
        print(f"  GPU Miner Available: {hybrid_miner.gpu_miner.gpu_available}")
        print()

        # Performance metrics
        print("📊 PERFORMANCE METRICS:")
        print(f"  GPU Benchmark: {gpu_miner.benchmark_hashrate:.1f} MH/s")
        print(f"  AI Efficiency: {ai_afterburner.performance_metrics['compute_efficiency']:.2f}%")
        print(f"  Total Mining Power: {gpu_miner.benchmark_hashrate + ai_afterburner.total_compute_power:.1f} MH/s")
        print()

        print("🎯 AI MINING CAPABILITIES:")
        print("  ✅ GPU Mining (KawPow, Octopus, Ethash)")
        print("  ✅ AI Afterburner Processing")
        print("  ✅ Hybrid CPU + GPU Mining")
        print("  ✅ Real-time Performance Monitoring")
        print("  ✅ Sacred Geometry Optimization")
        print("  ✅ Quantum-enhanced Computing")
        print()

        print("🚀 Ready for AI-enhanced ZION mining!")
        print("💡 Use Dashboard.py for full control interface")

    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure AI components are properly installed")
    except Exception as e:
        print(f"❌ Demo Error: {e}")

if __name__ == "__main__":
    demo_ai_mining()