#!/bin/bash
# PC Setup Script for Qt Robot Controller
# Optimized for macOS, Linux, and Windows

set -e

echo "🖥️  Qt Robot Controller - PC Setup"
echo "====================================="
echo ""

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macOS"
    BREW_PREFIX=""
    if [ -f "/opt/homebrew/bin/brew" ]; then
        BREW_PREFIX="/opt/homebrew"  # Apple Silicon
    elif [ -f "/usr/local/bin/brew" ]; then
        BREW_PREFIX="/usr/local"      # Intel Mac
    fi
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="Linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    OS_TYPE="Windows"
else
    OS_TYPE="Unknown"
fi

echo "📍 Detected OS: $OS_TYPE"
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

# Handle system dependencies based on OS
if [[ "$OS_TYPE" == "macOS" ]]; then
    echo "🍎 macOS Setup"
    
    # Check for Homebrew
    if [ -z "$BREW_PREFIX" ]; then
        echo "⚠️  Homebrew not found"
        echo "   For audio support, install Homebrew first:"
        echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        echo ""
        read -p "   Continue without audio support? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
        SKIP_AUDIO=true
    else
        echo "✅ Homebrew found at $BREW_PREFIX"
        
        # Setup Homebrew in current shell
        eval "\$($BREW_PREFIX/bin/brew shellenv)"
        
        # Check for PortAudio
        if ! brew list portaudio &> /dev/null; then
            echo "📦 Installing PortAudio for audio support..."
            read -p "   Install PortAudio? (Y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Nn]$ ]]; then
                brew install portaudio
                echo "✅ PortAudio installed"
            else
                SKIP_AUDIO=true
                echo "⏭️  Skipped PortAudio"
            fi
        else
            echo "✅ PortAudio already installed"
        fi
    fi
    echo ""
    
elif [[ "$OS_TYPE" == "Linux" ]]; then
    echo "🐧 Linux Setup"
    
    # Check if packages are available
    if command -v apt &> /dev/null; then
        echo "   Detected apt package manager"
        
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
        echo "   Non-Debian system - install portaudio manually if needed"
    fi
    echo ""
fi

# Install Python packages
echo "📦 Installing Python packages..."

# Check Python version for aiohttp compatibility
if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -eq 9 ]; then
    echo "   Using Python 3.9 compatible versions..."
    AIOHTTP_VERSION='"aiohttp>=3.8.0,<3.9.0"'
else
    AIOHTTP_VERSION="aiohttp>=3.9.0"
fi

# Install core packages (without audio first)
echo "   Installing core packages..."
$PIP_CMD install PyQt6 PyQt6-WebEngine websockets $AIOHTTP_VERSION \
    python-socketio google-genai numpy opencv-python Pillow \
    pyyaml python-dotenv requests colorama edge-tts pydub

echo "✅ Core packages installed"
echo ""

# Install audio packages
if [ "$SKIP_AUDIO" != true ]; then
    echo "🎤 Installing audio packages..."
    
    # Install SpeechRecognition (doesn't need compilation)
    $PIP_CMD install SpeechRecognition pyttsx3
    
    # Install PyAudio with proper flags on macOS
    if [[ "$OS_TYPE" == "macOS" ]] && [ -n "$BREW_PREFIX" ]; then
        echo "   Installing PyAudio with PortAudio support..."
        PORTAUDIO_PREFIX="\$(brew --prefix portaudio)"
        CFLAGS="-I$PORTAUDIO_PREFIX/include" \
        LDFLAGS="-L$PORTAUDIO_PREFIX/lib" \
        $PIP_CMD install --no-cache-dir pyaudio
        
        if [ $? -eq 0 ]; then
            echo "✅ Audio packages installed with microphone support"
        else
            echo "⚠️  PyAudio installation failed - voice input may not work"
        fi
    else
        # Try regular install on other systems
        $PIP_CMD install pyaudio || echo "⚠️  PyAudio installation failed - voice input may not work"
    fi
else
    echo "⏭️  Skipped audio packages"
fi
echo ""

# Create config directory
echo "📁 Setting up configuration..."
mkdir -p config
mkdir -p logs

if [ ! -f "config/.env" ]; then
    echo "📝 Creating .env file..."
    cp config/.env.example config/.env 2>/dev/null || cat > config/.env << 'EOF'
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
$PYTHON_CMD -c "import PyQt6; import websockets; print('✅ Core packages OK')" 2>/dev/null || echo "⚠️  Some core packages may not import correctly"

if [ "$SKIP_AUDIO" != true ]; then
    $PYTHON_CMD -c "import pyaudio; import speech_recognition; print('✅ Audio packages OK')" 2>/dev/null || echo "⚠️  Audio packages may not work (optional)"
fi
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
if [[ "$OS_TYPE" == "macOS" ]]; then
    echo "   - Grant microphone access in System Preferences > Privacy"
fi
echo "   - Run 'python ../scripts/test_connection.py <robot-ip>' to test"
