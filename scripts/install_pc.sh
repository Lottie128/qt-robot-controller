#!/bin/bash
# PC Setup Script for Qt Robot Controller

set -e

echo "🖥️  Qt Robot Controller - PC Setup"
echo "====================================="
echo ""

# Detect if running in virtual environment
if [ -n "$VIRTUAL_ENV" ]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    USE_VENV=true
    IN_VENV=true
    PIP_CMD="pip"
    PYTHON_CMD="python"
else
    echo "📦 No virtual environment detected"
    USE_VENV=false
    IN_VENV=false
    PIP_CMD="pip3"
    PYTHON_CMD="python3"
fi
echo ""

# Check Python version
echo "📋 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 9 ]); then
    echo "❌ Python $PYTHON_VERSION found. Python 3.9+ required."
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Navigate to pc_app directory
cd pc_app

# Create virtual environment if not already in one
if [ "$IN_VENV" = false ]; then
    echo "📦 Creating virtual environment..."
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
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    PIP_CMD="pip"
    PYTHON_CMD="python"
    echo "✅ Virtual environment activated"
    echo ""
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
$PIP_CMD install --upgrade pip
echo "✅ pip upgraded"
echo ""

# Install system dependencies (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Checking system dependencies (Linux)..."
    
    # Check if packages are available
    if command -v apt &> /dev/null; then
        echo "   Detected apt package manager"
        
        # Optional: Only install if user wants
        read -p "   Install system audio/GUI packages? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            sudo apt update
            sudo apt install -y portaudio19-dev python3-pyaudio || echo "⚠️  Some packages skipped"
            echo "✅ System dependencies installed"
        else
            echo "⏭️  Skipped system packages"
        fi
    else
        echo "   Non-Debian system - skipping apt packages"
    fi
    echo ""
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 macOS detected"
    echo "   Install dependencies with: brew install portaudio"
    echo ""
fi

# Install Python packages
echo "📦 Installing Python packages..."
$PIP_CMD install -r requirements.txt
echo "✅ Python packages installed"
echo ""

# Create config directory
echo "📁 Setting up configuration..."
mkdir -p config
mkdir -p logs

if [ ! -f "config/.env" ]; then
    echo "📝 Creating .env file..."
    cp config/.env.example config/.env 2>/dev/null || cat > config/.env << EOF
# Google Gemini API Key (optional - for AI features)
# Get your key from: https://makersuite.google.com/app/apikey
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

# Test imports
echo "🧪 Testing imports..."
$PYTHON_CMD -c "import PyQt6; import websockets; print('✅ Core packages OK')" 2>/dev/null || echo "⚠️  Some packages may not import correctly"
echo ""

echo "✅ PC Setup Complete!"
echo ""
echo "🚀 To run the application:"

if [ "$IN_VENV" = false ]; then
    echo "   cd pc_app"
    if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
        echo "   venv\\Scripts\\activate"
    else
        echo "   source venv/bin/activate"
    fi
fi

echo "   python main.py"
echo ""
echo "📖 Need help? Check docs/SETUP_GUIDE.md"
echo ""
echo "💡 Tips:"
echo "   - Add your Gemini API key to config/.env for AI features"
echo "   - Run 'python ../scripts/test_connection.py <robot-ip>' to test"
