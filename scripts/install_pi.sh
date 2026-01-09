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

# Detect if running in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    USE_VENV=true
    PIP_CMD="pip"
else
    echo "📦 No virtual environment detected"
    echo "   Recommendation: Use virtual environment"
    echo "   Run: python3 -m venv venv && source venv/bin/activate"
    echo ""
    read -p "Install system-wide anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Installation cancelled"
        echo "   Please activate a virtual environment and try again"
        exit 1
    fi
    USE_VENV=false
    PIP_CMD="pip3"
fi
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Installing..."
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv python3-full
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
    python3-full \
    python3-venv \
    python3-opencv \
    python3-rpi.gpio \
    libatlas-base-dev \
    libhdf5-dev \
    libjpeg-dev \
    libportaudio2 \
    portaudio19-dev \
    i2c-tools \
    python3-smbus

echo "✅ System dependencies installed"
echo ""

# Setup GPIO permissions
echo "🔌 Configuring GPIO permissions..."
sudo usermod -a -G gpio $USER || true
sudo usermod -a -G i2c $USER || true
sudo usermod -a -G spi $USER || true
echo "✅ GPIO permissions configured"
echo ""

# Enable camera interface
echo "📷 Checking camera interface..."
if [ -f "/boot/config.txt" ]; then
    if ! grep -q "start_x=1" /boot/config.txt; then
        echo "Enabling camera interface..."
        echo "start_x=1" | sudo tee -a /boot/config.txt > /dev/null
        echo "⚠️  Camera enabled - reboot required!"
        REBOOT_NEEDED=true
    else
        echo "✅ Camera interface already enabled"
    fi
else
    echo "⚠️  /boot/config.txt not found (might be using new boot system)"
    echo "   Check camera with: libcamera-hello"
fi
echo ""

# Install Python packages
echo "📦 Installing Python packages..."
cd pi_server

if [ "$USE_VENV" = true ]; then
    echo "   Using virtual environment pip"
    pip install --upgrade pip
    pip install -r requirements.txt
else
    echo "   Installing system-wide with --break-system-packages"
    pip3 install --upgrade pip --break-system-packages
    pip3 install -r requirements.txt --break-system-packages
fi

echo "✅ Python packages installed"
echo ""

# Create config directory
echo "📁 Setting up configuration..."
mkdir -p config
mkdir -p logs
echo "✅ Directories created"
echo ""

# Test imports
echo "🧪 Testing imports..."
if [ "$USE_VENV" = true ]; then
    python -c "import websockets; import yaml; import RPi.GPIO; print('✅ Core packages OK')" 2>/dev/null || echo "⚠️  Some packages may not import"
else
    python3 -c "import websockets; import yaml; import RPi.GPIO; print('✅ Core packages OK')" 2>/dev/null || echo "⚠️  Some packages may not import"
fi
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
    if [ "$USE_VENV" = true ]; then
        echo "   python server.py"
    else
        echo "   python3 server.py"
    fi
    echo ""
    echo "📖 Need help? Check docs/SETUP_GUIDE.md"
    echo ""
    echo "💡 Tip: For best practice, use a virtual environment:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
fi
