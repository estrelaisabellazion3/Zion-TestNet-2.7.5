#!/bin/bash
# ZION SSH Dashboard Setup and Launch Script

echo "🚀 ZION SSH Dashboard Setup"
echo "=========================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python version: $python_version"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
pip3 install -r requirements-ssh-dashboard.txt

# Create config directory
echo ""
echo "📁 Creating config directory..."
mkdir -p config

# Check if SSH config exists
if [ ! -f "config/ssh_config.json" ]; then
    echo ""
    echo "⚙️ Creating default SSH config..."
    cat > config/ssh_config.json << EOF
{
  "host": "YOUR_SSH_SERVER_IP",
  "port": 22,
  "username": "YOUR_USERNAME",
  "password": null,
  "key_file": null
}
EOF
    echo "⚠️ Please edit config/ssh_config.json with your SSH server details!"
fi

# Optional: Compile Yescrypt C extension for better performance
echo ""
read -p "🔧 Compile Yescrypt C extension for 10x performance? (y/N): " compile_choice
if [[ "$compile_choice" =~ ^[Yy]$ ]]; then
    echo "🔨 Compiling C extension..."
    cd mining
    python3 setup.py build_ext --inplace
    cd ..
    echo "✅ C extension compiled!"
else
    echo "⏭️ Skipping C extension (will use Python fallback)"
fi

# Launch dashboard
echo ""
echo "🚀 Launching ZION SSH Dashboard..."
echo "=========================================="
python3 Dashboard_SSH_Optimized.py
