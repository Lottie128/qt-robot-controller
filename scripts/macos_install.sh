#!/bin/bash
# Quick macOS Setup for Qt Robot Controller
# Handles Homebrew, PortAudio, and all Python dependencies

set -e

echo "🍎 Qt Robot Controller - macOS Quick Setup"
echo "============================================="
echo ""

# Detect Homebrew location
if [ -f "/opt/homebrew/bin/brew" ]; then
    BREW_PREFIX="/opt/homebrew"  # Apple Silicon (M1/M2/M3)
    echo "✅ Apple Silicon Mac detected"
elif [ -f "/usr/local/bin/brew" ]; then
    BREW_PREFIX="/usr/local"      # Intel Mac
    echo "✅ Intel Mac detected"
else
    echo "❌ Homebrew not found!"
    echo ""
    echo "Install Homebrew first:"
    echo "  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Setup Homebrew in PATH
eval "\$($BREW_PREFIX/bin/brew shellenv)"
echo "✅ Homebrew loaded from $BREW_PREFIX"
echo ""

# Check Python
echo "🐍 Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found"
    echo "Install with: brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Install PortAudio
echo "🎧 Setting up audio support..."
if ! brew list portaudio &> /dev/null; then
    echo "Installing PortAudio..."
    brew install portaudio
    echo "✅ PortAudio installed"
else
    echo "✅ PortAudio already installed"
fi
echo ""

# Navigate to project
echo "📁 Setting up project..."
cd "$(dirname "$0")"/.. # Go to project root
cd pc_app

# Create/activate virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Activated"
echo ""

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip -q
echo "✅ pip upgraded"
echo ""

# Install packages
echo "📦 Installing Python packages..."
echo "This may take a few minutes..."
echo ""

# Detect Python version for aiohttp compatibility
PYTHON_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MINOR" -eq 9 ]; then
    echo "Using Python 3.9 compatible versions..."
    AIOHTTP_VER='"aiohttp>=3.8.0,<3.9.0"'
else
    AIOHTTP_VER="aiohttp>=3.9.0"
fi

# Core packages
echo "[1/3] Installing core packages..."
pip install -q PyQt6 PyQt6-WebEngine websockets $AIOHTTP_VER \
    python-socketio google-genai numpy opencv-python Pillow \
    pyyaml python-dotenv requests colorama
echo "✅ Core packages installed"

# Audio packages (non-PyAudio)
echo "[2/3] Installing audio utilities..."
pip install -q SpeechRecognition pyttsx3 edge-tts pydub
echo "✅ Audio utilities installed"

# PyAudio with PortAudio
echo "[3/3] Installing PyAudio with microphone support..."
PORTAUDIO_PREFIX="\$(brew --prefix portaudio)"
CFLAGS="-I$PORTAUDIO_PREFIX/include" \
LDFLAGS="-L$PORTAUDIO_PREFIX/lib" \
pip install --no-cache-dir pyaudio

if [ $? -eq 0 ]; then
    echo "✅ PyAudio installed successfully"
else
    echo "⚠️  PyAudio installation failed (voice input may not work)"
fi
echo ""

# Setup config
echo "🔧 Setting up configuration..."
mkdir -p config logs

if [ ! -f "config/.env" ]; then
    cat > config/.env << 'EOF'
# Google Gemini API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF
    echo "✅ Created config/.env"
else
    echo "✅ config/.env already exists"
fi
echo ""

# Test installation
echo "🧪 Testing installation..."
python -c "import PyQt6; print('✅ PyQt6')" 2>/dev/null || echo "❌ PyQt6 failed"
python -c "import websockets; print('✅ websockets')" 2>/dev/null || echo "❌ websockets failed"
python -c "import pyaudio; print('✅ PyAudio')" 2>/dev/null || echo "⚠️  PyAudio not available"
python -c "import speech_recognition; print('✅ SpeechRecognition')" 2>/dev/null || echo "⚠️  SpeechRecognition not available"
echo ""

echo "✨ Installation Complete!"
echo ""
echo "🚀 To run the app:"
echo "   cd pc_app"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "💡 Pro tips:"
echo "   1. Add Gemini API key to pc_app/config/.env"
echo "   2. Grant microphone access: System Preferences > Privacy > Microphone"
echo "   3. Connect to robot IP when prompted"
echo ""
echo "📚 Documentation: docs/SETUP_GUIDE.md"
echo ""
