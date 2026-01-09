#!/bin/bash
# Quick Raspberry Pi Setup for Qt Robot Controller
# Handles virtual environment and dependencies properly

set -e

echo "🤖 Qt Robot Controller - Pi Quick Setup"
echo "========================================"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo "❌ Don't run this script as root/sudo!"
    echo "   Run as normal user: bash scripts/pi_quick_install.sh"
    exit 1
fi

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Install with: sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Navigate to project root
cd "$(dirname "$0")"/..

# Install system dependencies
echo "📦 Installing system dependencies..."
echo "   This requires sudo and may take a few minutes"
echo ""

sudo apt update
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-opencv \
    python3-rpi.gpio \
    libatlas-base-dev \
    i2c-tools \
    python3-smbus \
    || echo "⚠️  Some packages may have failed (continuing...)"

echo "✅ System dependencies installed"
echo ""

# Create virtual environment
echo "📦 Setting up virtual environment..."
cd pi_server

if [ -d "venv" ]; then
    echo "   Virtual environment already exists"
    read -p "   Recreate? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo "✅ Virtual environment recreated"
    else
        echo "✅ Using existing virtual environment"
    fi
else
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo "✅ Activated"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"
echo ""

# Install Python packages
echo "📦 Installing Python packages..."
echo "   This may take several minutes..."
echo ""

echo "[1/3] Installing core networking packages..."
pip install -q websockets aiohttp python-socketio
echo "✅ Networking packages installed"

echo "[2/3] Installing utilities..."
pip install -q pyyaml numpy colorama Pillow
echo "✅ Utilities installed"

echo "[3/3] Installing hardware packages..."
pip install -q RPi.GPIO opencv-python
echo "✅ Hardware packages installed"
echo ""

# Setup GPIO permissions
echo "🔌 Setting up GPIO permissions..."
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER
echo "✅ GPIO permissions configured"
echo ""

# Create config
echo "📁 Setting up configuration..."
mkdir -p config logs

if [ ! -f "config/hardware_config.yaml" ]; then
    cat > config/hardware_config.yaml << 'EOF'
# Hardware Configuration
server:
  host: "0.0.0.0"
  port: 8888

motor:
  type: "L298N"
  pins:
    left_forward: 33
    left_backward: 38
    right_forward: 35
    right_backward: 40

camera:
  type: "auto"  # auto, csi, usb
  resolution: [640, 480]
  fps: 30

sensors:
  ultrasonic:
    trigger_pin: 11
    echo_pin: 13
EOF
    echo "✅ Created hardware_config.yaml"
else
    echo "✅ hardware_config.yaml already exists"
fi
echo ""

# Test installation
echo "🧪 Testing installation..."
python -c "import websockets; print('✅ websockets')" 2>/dev/null || echo "❌ websockets failed"
python -c "import aiohttp; print('✅ aiohttp')" 2>/dev/null || echo "❌ aiohttp failed"
python -c "import RPi.GPIO; print('✅ RPi.GPIO')" 2>/dev/null || echo "❌ RPi.GPIO failed"
python -c "import cv2; print('✅ opencv')" 2>/dev/null || echo "❌ opencv failed"
echo ""

echo "✨ Installation Complete!"
echo ""
echo "🚀 To run the server:"
echo "   cd pi_server"
echo "   source venv/bin/activate"
echo "   python server.py"
echo ""
echo "💡 Important:"
echo "   - You may need to reboot for GPIO permissions to take effect"
echo "   - Connect from PC using this Pi's IP address"
echo "   - Default port: 8888"
echo ""
echo "📖 Documentation: docs/SETUP_GUIDE.md"
echo ""
