#!/bin/bash
# ZION Miner Release Verification Script
# Version: 1.0.0

set -e

echo "🔍 ZION Miner Package Verification"
echo "=================================="

PACKAGE_FILE="zion-miner-1.0.0.deb"
EXPECTED_SHA256="3cf52dd26fe622731919be84d747b2d7a7a4bdfc92740d06315fa7594fb75529"

# Check if package file exists
if [ ! -f "$PACKAGE_FILE" ]; then
    echo "❌ Error: Package file $PACKAGE_FILE not found"
    exit 1
fi

echo "📦 Package file found: $PACKAGE_FILE"

# Calculate SHA256 checksum
echo "🔐 Calculating SHA256 checksum..."
ACTUAL_SHA256=$(sha256sum "$PACKAGE_FILE" | cut -d' ' -f1)

echo "Expected: $EXPECTED_SHA256"
echo "Actual  : $ACTUAL_SHA256"

# Verify checksum
if [ "$ACTUAL_SHA256" = "$EXPECTED_SHA256" ]; then
    echo "✅ Package integrity verified!"
else
    echo "❌ Package integrity check FAILED!"
    echo "The package may be corrupted or tampered with."
    exit 1
fi

# Package information
echo ""
echo "📋 Package Information:"
dpkg -I "$PACKAGE_FILE" | head -20

echo ""
echo "📁 Package Contents:"
dpkg -c "$PACKAGE_FILE" | head -10

# File size
PACKAGE_SIZE=$(stat -c%s "$PACKAGE_FILE")
echo ""
echo "📊 Package size: $PACKAGE_SIZE bytes ($(numfmt --to=iec --suffix=B $PACKAGE_SIZE))"

echo ""
echo "🎉 Package verification completed successfully!"
echo "Ready for installation with: sudo dpkg -i $PACKAGE_FILE"