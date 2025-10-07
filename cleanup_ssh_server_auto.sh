#!/bin/bash

# ZION SSH Server Complete Cleanup Script - AUTO MODE
# This script completely removes all old ZION processes and data from SSH server
# AUTOMATIC VERSION - NO CONFIRMATION REQUIRED

set -e

SERVER="91.98.122.165"
SERVER_USER="root"

echo "🧹 ZION SSH Server Complete Cleanup - AUTO MODE"
echo "=============================================="
echo "Server: $SERVER"
echo "⚠️  Automatically cleaning ALL ZION data on server..."
echo ""

echo "🔍 Stopping all ZION processes..."

# Stop all possible ZION processes
ssh $SERVER_USER@$SERVER "
    echo '=== Stopping all Python ZION processes ==='
    pkill -f 'python.*zion' || true
    pkill -f 'python.*pool' || true
    pkill -f 'python.*blockchain' || true
    pkill -f 'python.*rpc' || true
    pkill -f 'stratum' || true
    sleep 2
    
    echo '=== Stopping Docker containers ==='
    docker stop \$(docker ps -q) 2>/dev/null || true
    docker rm \$(docker ps -aq) 2>/dev/null || true
    docker system prune -af 2>/dev/null || true
    
    echo '=== Force kill any remaining processes ==='
    pkill -9 -f 'zion' || true
    pkill -9 -f 'pool' || true
    pkill -9 -f 'blockchain' || true
    
    echo '✅ All processes stopped'
"

echo ""
echo "🗑️  Removing all ZION directories..."

# Remove all ZION related directories
ssh $SERVER_USER@$SERVER "
    echo '=== Removing ZION directories ==='
    rm -rf /root/zion* || true
    rm -rf /root/ZION* || true
    rm -rf /root/*zion* || true
    rm -rf /root/pool* || true
    rm -rf /root/blockchain* || true
    rm -rf /opt/zion* || true
    rm -rf /var/lib/zion* || true
    rm -rf /tmp/zion* || true
    
    echo '=== Removing database files ==='
    find /root -name '*.db' -type f -delete 2>/dev/null || true
    find /root -name '*.db-*' -type f -delete 2>/dev/null || true
    find /root -name 'zion*.log' -type f -delete 2>/dev/null || true
    find /root -name 'pool*.log' -type f -delete 2>/dev/null || true
    find /root -name 'mining*.log' -type f -delete 2>/dev/null || true
    
    echo '✅ All ZION files removed'
"

echo ""
echo "🔥 Cleaning system state..."

# Clean system state
ssh $SERVER_USER@$SERVER "
    echo '=== Cleaning network state ==='
    # Reset iptables if needed
    # iptables -F || true
    
    echo '=== Cleaning logs ==='
    truncate -s 0 /var/log/syslog 2>/dev/null || true
    journalctl --vacuum-time=1d 2>/dev/null || true
    
    echo '=== Cleaning temp files ==='
    rm -rf /tmp/* 2>/dev/null || true
    rm -rf /var/tmp/* 2>/dev/null || true
    
    echo '=== Updating package list ==='
    apt update -qq 2>/dev/null || true
    
    echo '✅ System cleaned'
"

echo ""
echo "📊 Checking cleanup results..."

# Verify cleanup
ssh $SERVER_USER@$SERVER "
    echo '=== Verification ==='
    echo 'Python processes:'
    ps aux | grep -i python | grep -v grep || echo 'No Python processes'
    echo ''
    echo 'Docker containers:'
    docker ps -a || echo 'No Docker containers'
    echo ''
    echo 'ZION files:'
    find /root -name '*zion*' -o -name '*pool*' -o -name '*.db' 2>/dev/null | head -10 || echo 'No ZION files found'
    echo ''
    echo 'Disk space:'
    df -h /
    echo ''
    echo 'Memory:'
    free -h
"

echo ""
echo "✅ SSH Server Cleanup Complete!"
echo "The server is now ready for fresh ZION deployment"
echo ""