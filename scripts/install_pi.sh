#!/bin/bash
# Raspberry Pi Setup Script for Qt Robot Controller

set -e

echo "🤖 Qt Robot Controller - Raspberry Pi Setup"
echo "============================================"
echo ""

# Check if running on Raspberry Pi
if [ ! -f "/sys/firmware/devicetree/base/model" ]; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Update system
echo "📦 Updating system packages..."
sudo apt update
echo "✅ System packages updated"
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-opencv \
    python3-pyaudio \
    python3-rpi.gpio \
    libatlas-base-dev \
    libhdf5-dev \
    libjpeg-dev \
    libportaudio2 \
    portaudio19-dev

echo "✅ System dependencies installed"
echo ""

# Setup GPIO permissions
echo "🔌 Configuring GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER
sudo usermod -a -G spi $USER
echo "✅ GPIO permissions configured"
echo ""

# Enable camera interface
echo "📷 Checking camera interface..."
if ! grep -q "start_x=1" /boot/config.txt; then
    echo "Enabling camera interface..."
    echo "start_x=1" | sudo tee -a /boot/config.txt
    echo "⚠️  Camera enabled - reboot required!"
    REBOOT_NEEDED=true
else
    echo "✅ Camera interface already enabled"
fi
echo ""

# Install Python packages
echo "📦 Installing Python packages..."
cd pi_server
pip3 install -r requirements.txt
echo "✅ Python packages installed"
echo ""

# Create config directory
echo "📁 Setting up configuration..."
mkdir -p config
mkdir -p logs
echo "✅ Directories created"
echo ""

echo "✅ Raspberry Pi Setup Complete!"
echo ""

if [ "$REBOOT_NEEDED" = true ]; then
    echo "⚠️  REBOOT REQUIRED to enable camera"
    echo ""
    read -p "Reboot now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo reboot
    fi
else
    echo "🚀 To run the server:"
    echo "   cd pi_server"
    echo "   python3 server.py"
    echo ""
    echo "📖 Need help? Check docs/SETUP_GUIDE.md"
fi
