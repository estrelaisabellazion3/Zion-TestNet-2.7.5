#!/bin/bash

# ZION Miner Ubuntu Release v1.0.0 - Installation Script
# Copyright (c) 2025 ZION Development Team

set -e

PACKAGE_NAME="zion-miner-1.0.0.deb"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🚀 ZION Miner Ubuntu Release v1.0.0"
echo "======================================"
echo ""

# Check if running as root/sudo
if [[ $EUID -ne 0 ]]; then
   echo "❌ This script must be run as root (use sudo)"
   echo "Usage: sudo ./install-zion-miner.sh"
   exit 1
fi

echo "📋 Pre-installation checks..."

# Check Ubuntu version
if ! command -v lsb_release &> /dev/null; then
    echo "⚠️ Cannot detect Ubuntu version (lsb_release not found)"
else
    UBUNTU_VERSION=$(lsb_release -rs)
    echo "✅ Detected Ubuntu $UBUNTU_VERSION"
    
    # Check supported versions
    if [[ $(echo "$UBUNTU_VERSION >= 22.04" | bc -l) -eq 1 ]]; then
        echo "✅ Ubuntu version supported"
    else
        echo "⚠️ Warning: Ubuntu $UBUNTU_VERSION may not be fully supported"
        echo "   Recommended: Ubuntu 22.04 LTS or newer"
    fi
fi

# Check if package file exists
if [ ! -f "$SCRIPT_DIR/$PACKAGE_NAME" ]; then
    echo "❌ Package file not found: $PACKAGE_NAME"
    echo "Make sure the .deb file is in the same directory as this script"
    exit 1
fi

echo "✅ Package file found: $PACKAGE_NAME"

# Check dependencies
echo ""
echo "🔍 Checking dependencies..."

MISSING_DEPS=()

if ! command -v python3 &> /dev/null; then
    MISSING_DEPS+=("python3")
fi

if ! command -v pip3 &> /dev/null; then
    MISSING_DEPS+=("python3-pip")
fi

if ! systemctl --version &> /dev/null; then
    MISSING_DEPS+=("systemd")
fi

if [ ${#MISSING_DEPS[@]} -ne 0 ]; then
    echo "⚠️ Missing dependencies: ${MISSING_DEPS[*]}"
    echo "🔧 Installing missing dependencies..."
    apt-get update
    apt-get install -y "${MISSING_DEPS[@]}"
else
    echo "✅ All dependencies are available"
fi

# Install the package
echo ""
echo "📦 Installing ZION Miner package..."

if dpkg -i "$SCRIPT_DIR/$PACKAGE_NAME"; then
    echo "✅ Package installation completed"
else
    echo "⚠️ Package installation had warnings, fixing dependencies..."
    apt-get install -f -y
fi

# Verify installation
echo ""
echo "🔍 Verifying installation..."

if command -v zion-miner &> /dev/null; then
    echo "✅ ZION Miner executable installed"
    INSTALLED_VERSION=$(zion-miner --version 2>&1 || echo "Version check failed")
    echo "   Version: $INSTALLED_VERSION"
else
    echo "❌ ZION Miner executable not found"
    exit 1
fi

if systemctl list-unit-files | grep -q "zion-miner.service"; then
    echo "✅ Systemd service installed"
else
    echo "❌ Systemd service not found"
    exit 1
fi

if [ -f "/etc/zion-miner/config.json" ]; then
    echo "✅ Configuration file installed"
else
    echo "❌ Configuration file not found"
    exit 1
fi

# Installation summary
echo ""
echo "🎉 ZION Miner Installation Completed Successfully!"
echo "==============================================="
echo ""
echo "📋 Next Steps:"
echo "   1. Configure mining pool and wallet:"
echo "      sudo nano /etc/zion-miner/config.json"
echo ""
echo "   2. Start mining service:"
echo "      sudo systemctl start zion-miner"
echo ""
echo "   3. Enable auto-start on boot:"
echo "      sudo systemctl enable zion-miner"
echo ""
echo "   4. Check mining status:"
echo "      sudo systemctl status zion-miner"
echo ""
echo "   5. View mining logs:"
echo "      sudo journalctl -u zion-miner -f"
echo ""
echo "🔧 Configuration file: /etc/zion-miner/config.json"
echo "📊 Service management: systemctl [start|stop|status] zion-miner"
echo "📁 Data directory: /var/lib/zion-miner/"
echo "📖 Documentation: /usr/share/doc/zion-miner/README.md"
echo ""
echo "🌐 Support: https://github.com/estrelaisabellazion3/Zion-TestNet-2.7.5"
echo ""
echo "Happy Mining! 💎"