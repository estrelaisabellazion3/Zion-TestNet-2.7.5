#!/bin/bash
# ZION AI Afterburner Ubuntu Installation Script
# Version: 1.0.0

set -e

echo "🔥 ZION AI Afterburner Installer v1.0.0"
echo "======================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run as root (use sudo)"
    exit 1
fi

# Detect Ubuntu version
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$NAME
    VERSION=$VERSION_ID
else
    echo "❌ Cannot detect OS version"
    exit 1
fi

echo "🖥️ Detected: $OS $VERSION"

# Check Ubuntu compatibility
case $VERSION in
    "22.04"|"24.04"|"20.04")
        echo "✅ Ubuntu version supported"
        ;;
    *)
        echo "⚠️ Warning: Ubuntu $VERSION not officially tested"
        echo "Supported versions: 20.04, 22.04, 24.04"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        ;;
esac

# Check system requirements
echo ""
echo "🔍 Checking system requirements..."

# Check CPU cores
CPU_CORES=$(nproc)
echo "  CPU Cores: $CPU_CORES"
if [ "$CPU_CORES" -lt 2 ]; then
    echo "⚠️ Warning: Recommended 4+ CPU cores for optimal performance"
fi

# Check memory
MEMORY_GB=$(free -g | awk 'NR==2{printf "%.1f", $2}')
echo "  Memory: ${MEMORY_GB}GB"
if (( $(echo "$MEMORY_GB < 2" | bc -l) )); then
    echo "⚠️ Warning: Recommended 4GB+ RAM for optimal performance"
fi

# Check Python version
PYTHON_VERSION=$(python3 --version 2>/dev/null | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "  Python: $PYTHON_VERSION"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3,8) else 1)" 2>/dev/null; then
    echo "❌ Python 3.8+ required, found: $PYTHON_VERSION"
    echo "Please update Python or install python3.8+"
    exit 1
fi

# Check GPU (optional)
if command -v nvidia-smi >/dev/null 2>&1; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader 2>/dev/null | head -1)
    echo "  🎮 GPU: $GPU_INFO"
    echo "  ✅ NVIDIA GPU detected - hardware acceleration available"
else
    echo "  🎮 GPU: Not detected (NVIDIA drivers not installed)"
    echo "  ℹ️ AI Afterburner will run in CPU-only mode"
fi

echo ""
echo "📦 Installing dependencies..."

# Update package list
apt-get update -qq

# Install required system packages
PACKAGES="python3 python3-pip systemd python3-psutil python3-numpy curl wget"
apt-get install -y $PACKAGES

# Check if .deb file exists
DEB_FILE="zion-ai-afterburner-1.0.0.deb"
if [ ! -f "$DEB_FILE" ]; then
    echo ""
    echo "📥 Downloading ZION AI Afterburner package..."
    # In production, this would download from GitHub releases
    echo "❌ Package file $DEB_FILE not found in current directory"
    echo "Please ensure you have the .deb package file in the current directory"
    exit 1
fi

echo ""
echo "📋 Package information:"
dpkg -I "$DEB_FILE" | grep -E "(Package|Version|Description)"

echo ""
read -p "🚀 Install ZION AI Afterburner? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "Installation cancelled"
    exit 0
fi

echo ""
echo "🔧 Installing ZION AI Afterburner..."

# Install the package
if dpkg -i "$DEB_FILE"; then
    echo "✅ Package installed successfully"
else
    echo "❌ Package installation failed, trying to fix dependencies..."
    apt-get install -f -y
    if dpkg -i "$DEB_FILE"; then
        echo "✅ Package installed successfully after fixing dependencies"
    else
        echo "❌ Installation failed"
        exit 1
    fi
fi

echo ""
echo "🎉 ZION AI Afterburner installation completed!"
echo ""
echo "📋 Next Steps:"
echo "1. Configure settings:"
echo "   sudo nano /etc/zion-ai/afterburner.json"
echo ""
echo "2. Start the service:"
echo "   sudo systemctl start zion-ai-afterburner"
echo ""
echo "3. Enable auto-start:"
echo "   sudo systemctl enable zion-ai-afterburner"
echo ""
echo "4. Check status:"
echo "   sudo systemctl status zion-ai-afterburner"
echo ""
echo "5. Monitor logs:"
echo "   sudo journalctl -u zion-ai-afterburner -f"
echo ""
echo "📊 Performance monitoring:"
echo "   - Real-time GPU stats: watch -n 1 nvidia-smi"
echo "   - System resources: htop"
echo "   - AI processing logs: tail -f /var/lib/zion-ai/logs/afterburner.log"
echo ""
echo "🔧 Configuration file: /etc/zion-ai/afterburner.json"
echo "📖 Documentation: https://github.com/estrelaisabellazion3/Zion-TestNet-2.7.5"
echo ""

# Offer to start service immediately
echo "🚀 Start AI Afterburner service now?"
read -p "(Y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Nn]$ ]]; then
    echo ""
    echo "🔄 Starting service..."
    systemctl daemon-reload
    systemctl enable zion-ai-afterburner
    systemctl start zion-ai-afterburner
    
    sleep 2
    
    echo ""
    echo "📊 Service Status:"
    systemctl status zion-ai-afterburner --no-pager -l
    
    echo ""
    echo "✅ ZION AI Afterburner is now running!"
    echo "Monitor with: sudo journalctl -u zion-ai-afterburner -f"
else
    echo ""
    echo "ℹ️ Service not started. Start manually with:"
    echo "sudo systemctl start zion-ai-afterburner"
fi

echo ""
echo "🎊 Installation complete - AI Afterburner ready for production!"