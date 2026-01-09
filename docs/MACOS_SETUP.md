# Complete macOS Setup Guide

**Detailed installation and configuration guide for Qt Robot Controller on macOS**

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install](#quick-install)
3. [Detailed Manual Install](#detailed-manual-install)
4. [Post-Installation](#post-installation)
5. [Troubleshooting](#troubleshooting)
6. [Advanced Configuration](#advanced-configuration)

## Prerequisites

### System Requirements

- **macOS Version:** 10.15 (Catalina) or newer
- **Mac Type:** Intel or Apple Silicon (M1/M2/M3)
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 2GB free space
- **Internet:** For downloading dependencies

### Pre-Installation Checklist

- [ ] Command Line Tools installed
- [ ] Homebrew installed (or willing to install)
- [ ] Python 3.9+ available
- [ ] Admin/sudo access (for Homebrew)

### Installing Command Line Tools

```bash
xcode-select --install
```

Click "Install" when prompted.

### Installing Homebrew

If you don't have Homebrew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**Apple Silicon Macs:** After installation, run:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel Macs:** After installation, run:
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

## Quick Install

### One-Command Installation

```bash
curl -fsSL https://raw.githubusercontent.com/Lottie128/qt-robot-controller/main/scripts/macos_install.sh | bash
```

### Or Clone First, Then Install

```bash
# Clone repository
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller

# Run installer
chmod +x scripts/macos_install.sh
./scripts/macos_install.sh
```

The installer will:
1. ✅ Check/install Homebrew
2. ✅ Install PortAudio for audio support
3. ✅ Create Python virtual environment
4. ✅ Install all Python dependencies
5. ✅ Handle Python 3.9 compatibility
6. ✅ Configure audio with proper compiler flags
7. ✅ Setup configuration files
8. ✅ Test the installation

After installation:
```bash
cd pc_app
source venv/bin/activate
python main.py
```

## Detailed Manual Install

### Step 1: Setup Homebrew Environment

First, ensure Homebrew is in your PATH.

**For Apple Silicon (M1/M2/M3):**
```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
brew --version  # Verify it works
```

**For Intel Mac:**
```bash
eval "$(/usr/local/bin/brew shellenv)"
brew --version  # Verify it works
```

### Step 2: Install System Dependencies

```bash
# Install PortAudio (required for microphone support)
brew install portaudio

# Verify installation
brew list portaudio
ls -la $(brew --prefix portaudio)/include/portaudio.h
```

### Step 3: Clone Repository

```bash
# Clone to your preferred location
cd ~/Documents/codes  # Or wherever you prefer
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
```

### Step 4: Create Virtual Environment

```bash
cd pc_app

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Verify activation
which python  # Should show: /path/to/pc_app/venv/bin/python
```

### Step 5: Upgrade pip

```bash
pip install --upgrade pip
```

### Step 6: Install Core Packages

**Important:** Notice the quotes around packages with brackets!

```bash
pip install PyQt6 PyQt6-WebEngine websockets \
    "python-socketio[client]" google-genai numpy \
    opencv-python Pillow pyyaml python-dotenv \
    requests colorama
```

**For Python 3.9 users (check with `python --version`):**
```bash
pip install PyQt6 PyQt6-WebEngine websockets \
    "aiohttp>=3.8.0,<3.9.0" "python-socketio[client]" \
    google-genai numpy opencv-python Pillow pyyaml \
    python-dotenv requests colorama
```

### Step 7: Install Audio Packages

```bash
# Install audio utilities
pip install SpeechRecognition pyttsx3 edge-tts pydub
```

### Step 8: Install PyAudio with PortAudio

This is the most critical step for audio support:

```bash
# Set compiler flags and install
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

**If it fails, try with explicit paths:**

```bash
# For Apple Silicon
CFLAGS="-I/opt/homebrew/include" \
LDFLAGS="-L/opt/homebrew/lib" \
pip install --no-cache-dir pyaudio

# For Intel
CFLAGS="-I/usr/local/include" \
LDFLAGS="-L/usr/local/lib" \
pip install --no-cache-dir pyaudio
```

### Step 9: Setup Configuration

```bash
# Create directories
mkdir -p config logs

# Create .env file
cat > config/.env << 'EOF'
# Google Gemini API Key (optional - for AI features)
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF

echo "✅ Configuration files created"
```

### Step 10: Test Installation

```bash
# Test core imports
python -c "import PyQt6; print('✅ PyQt6 OK')"
python -c "import websockets; print('✅ websockets OK')"
python -c "import pyaudio; print('✅ PyAudio OK')"
python -c "import speech_recognition; print('✅ SpeechRecognition OK')"

echo "
✨ Installation complete!"
```

### Step 11: Run the Application

```bash
python main.py
```

## Post-Installation

### Grant Microphone Permission

1. Open **System Preferences** → **Security & Privacy**
2. Click **Privacy** tab
3. Select **Microphone** from left sidebar
4. Check the boxes for:
   - Terminal (if running from terminal)
   - Python (if it appears)
   - Your Qt application

### Add to Shell Profile (Permanent Setup)

Add Homebrew to your shell profile for automatic loading:

**For zsh (default on modern macOS):**

```bash
# Apple Silicon
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile

# Intel
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile

# Reload shell
source ~/.zprofile
```

### Create Convenient Aliases

```bash
cat >> ~/.zshrc << 'EOF'

# Qt Robot Controller aliases
alias robot-cd="cd ~/Documents/codes/qt-robot-controller/pc_app"
alias robot-activate="cd ~/Documents/codes/qt-robot-controller/pc_app && source venv/bin/activate"
alias robot-run="cd ~/Documents/codes/qt-robot-controller/pc_app && source venv/bin/activate && python main.py"
EOF

source ~/.zshrc
```

Now you can simply type:
```bash
robot-run  # Starts the app from anywhere!
```

### Configure Gemini API (Optional)

For AI chat features:

1. Get API key from: https://makersuite.google.com/app/apikey
2. Edit config file:
   ```bash
   nano pc_app/config/.env
   ```
3. Replace `your_api_key_here` with your actual key
4. Save and exit (Ctrl+X, then Y, then Enter)

## Troubleshooting

### Issue: "zsh: command not found: brew"

**Cause:** Homebrew not in PATH

**Solution:**
```bash
# Test which Homebrew you have
ls -la /opt/homebrew/bin/brew      # Apple Silicon
ls -la /usr/local/bin/brew         # Intel

# Add the one that exists to PATH
eval "$(/opt/homebrew/bin/brew shellenv)"  # or /usr/local

# Make permanent
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

### Issue: "zsh: no matches found: python-socketio[client]"

**Cause:** zsh interprets brackets as glob patterns

**Solution:** Always quote packages with brackets
```bash
pip install "python-socketio[client]"  # ✅ Correct
```

### Issue: "No matching distribution found for aiohttp>=3.9.0"

**Cause:** Python 3.9 can't use latest aiohttp

**Solution:**
```bash
pip install "aiohttp>=3.8.0,<3.9.0"
```

Check your Python version:
```bash
python --version
```

### Issue: "fatal error: 'portaudio.h' file not found"

**Cause:** PyAudio can't find PortAudio headers

**Solution:**
```bash
# Install PortAudio
brew install portaudio

# Install PyAudio with flags
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

### Issue: Microphone Not Working

**Causes & Solutions:**

1. **Permission not granted**
   - System Preferences → Security & Privacy → Microphone
   - Enable Terminal/Python

2. **PyAudio not installed correctly**
   ```bash
   pip uninstall pyaudio
   CFLAGS="-I$(brew --prefix portaudio)/include" \
   LDFLAGS="-L$(brew --prefix portaudio)/lib" \
   pip install --no-cache-dir pyaudio
   ```

3. **No audio devices found**
   ```bash
   python << 'EOF'
   import pyaudio
   p = pyaudio.PyAudio()
   print(f"Devices: {p.get_device_count()}")
   p.terminate()
   EOF
   ```

### Issue: "ModuleNotFoundError: No module named 'PyQt6'"

**Cause:** Not in virtual environment or packages not installed

**Solution:**
```bash
cd pc_app
source venv/bin/activate  # Make sure you're in venv
which python              # Should show venv path
pip install PyQt6 PyQt6-WebEngine
```

### Issue: Application Won't Start

**Diagnostic steps:**

```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check virtual environment
echo $VIRTUAL_ENV  # Should show venv path

# 3. Test imports one by one
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import websockets; print('websockets OK')"
python -c "import aiohttp; print('aiohttp OK')"

# 4. Check main.py exists
ls -la main.py

# 5. Run with verbose output
python -v main.py
```

## Advanced Configuration

### Using a Different Python Version

```bash
# Install Python 3.11 via Homebrew
brew install python@3.11

# Create venv with specific Python
cd pc_app
rm -rf venv
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Development Mode Installation

```bash
# Install with editable packages
cd pc_app
source venv/bin/activate
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Multiple Environments

```bash
# Create production environment
python3 -m venv venv-prod
source venv-prod/bin/activate
pip install -r requirements.txt
deactivate

# Create development environment
python3 -m venv venv-dev
source venv-dev/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
deactivate

# Switch between them
source venv-prod/bin/activate  # For production
source venv-dev/bin/activate   # For development
```

### Performance Tuning

```bash
# Install performance packages
pip install cython numpy --upgrade

# Use faster JSON library
pip install ujson

# Enable JIT compilation
export PYTHONOPTIMIZE=1
python main.py
```

## Verification Checklist

Before reporting issues, verify:

- [ ] Homebrew installed and in PATH
- [ ] PortAudio installed (`brew list portaudio`)
- [ ] Virtual environment activated (`which python`)
- [ ] All packages installed (`pip list`)
- [ ] PyAudio imports successfully
- [ ] Microphone permission granted
- [ ] Config files exist (`ls config/.env`)
- [ ] Running from correct directory (`pwd`)

## Getting Help

### Collect System Information

```bash
# Create debug info
cat > debug_info.txt << EOF
macOS Version: $(sw_vers -productVersion)
Mac Type: $(uname -m)
Homebrew: $(brew --version | head -1)
Python: $(python --version)
Pip: $(pip --version)
Virtual Env: $VIRTUAL_ENV
PortAudio: $(brew list portaudio 2>&1 | head -1)
PyAudio: $(pip show pyaudio | grep Version)
PyQt6: $(pip show PyQt6 | grep Version)
EOF

cat debug_info.txt
```

### Where to Get Help

- **GitHub Issues:** [Report bugs](https://github.com/Lottie128/qt-robot-controller/issues)
- **Discussions:** [Ask questions](https://github.com/Lottie128/qt-robot-controller/discussions)
- **Quick Reference:** [MACOS_QUICKREF.md](MACOS_QUICKREF.md)

## Next Steps

1. 🚀 [Connect to your Raspberry Pi](../README.md#step-3-connect--control)
2. 🎮 [Learn keyboard controls](CONTROLS.md)
3. ⚙️ [Configure GPIO pins](GPIO_CONFIGURATION.md)
4. 🤖 [Setup AI features](AI_SETUP.md)

---

**Last Updated:** January 2026  
**Tested On:** macOS Sonoma 14.x, Apple Silicon & Intel Macs