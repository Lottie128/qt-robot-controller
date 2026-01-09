#!/bin/bash
# PC Setup Script for Qt Robot Controller

set -e

echo "🖥️  Qt Robot Controller - PC Setup"
echo "====================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python $PYTHON_VERSION found. Python 3.9+ required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
cd pc_app
python3 -m venv venv
echo "✅ Virtual environment created"
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi
echo "✅ Virtual environment activated"
echo ""
# Upgrade pip
echo "⬆️  Upgrading pip..."
python3 -m pip install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Installing system dependencies (Linux)..."
    sudo apt update
    sudo apt install -y portaudio19-dev python3-pyaudio python3-pyqt6
    echo "✅ System dependencies installed"
    echo ""
fi

# Install Python packages
echo "📦 Installing Python packages..."
pip install -r requirements.txt
echo "✅ Python packages installed"
echo ""

# Create config directory
echo "📁 Setting up configuration..."
mkdir -p config
mkdir -p logs

if [ ! -f "config/.env" ]; then
    echo "📝 Creating .env file..."
    cat > config/.env << EOF
# Google Gemini API Key (optional - for AI features)
GEMINI_API_KEY=your_api_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF
    echo "✅ .env file created (edit config/.env to add API keys)"
else
    echo "✅ .env file already exists"
fi
echo ""

echo "✅ PC Setup Complete!"
echo ""
echo "🚀 To run the application:"
echo "   cd pc_app"
echo "   source venv/bin/activate  # Windows: venv\\Scripts\\activate"
echo "   python3 main.py"
echo ""
echo "📖 Need help? Check docs/SETUP_GUIDE.md"
