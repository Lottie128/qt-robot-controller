# macOS Setup Guide - Qt Robot Controller

Complete guide for setting up the Qt Robot Controller PC application on macOS (Intel and Apple Silicon).

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Install (Recommended)](#quick-install-recommended)
3. [Manual Installation](#manual-installation)
4. [Troubleshooting](#troubleshooting)
5. [Common Issues](#common-issues)
6. [Testing Your Installation](#testing-your-installation)

---

## Prerequisites

### Required Software

- **macOS:** 10.15 (Catalina) or later
- **Python:** 3.9 or higher
- **Homebrew:** Package manager for macOS
- **Xcode Command Line Tools:** For compiling native extensions

### Check Your System

```bash
# Check macOS version
sw_vers

# Check Python version
python3 --version

# Check if Homebrew is installed
brew --version
```

---

## Quick Install (Recommended)

### One-Command Installation

```bash
# Clone the repository
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller

# Run the macOS installer
chmod +x scripts/macos_install.sh
./scripts/macos_install.sh
```

### What the Installer Does

1. ✅ Detects your Mac type (Apple Silicon or Intel)
2. ✅ Checks for Homebrew (prompts to install if missing)
3. ✅ Installs PortAudio (required for microphone support)
4. ✅ Creates Python virtual environment
5. ✅ Installs all Python dependencies
6. ✅ Handles Python 3.9 compatibility automatically
7. ✅ Configures PyAudio with proper compiler flags
8. ✅ Sets up configuration files
9. ✅ Tests the installation

### After Installation

```bash
# Navigate to app directory
cd pc_app

# Activate virtual environment
source venv/bin/activate

# Run the application
python main.py
```

---

## Manual Installation

If you prefer to install manually or the automated script doesn't work:

### Step 1: Install Homebrew

If Homebrew is not installed:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

**After installation, add Homebrew to your PATH:**

**For Apple Silicon (M1/M2/M3):**
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**For Intel Mac:**
```bash
echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
eval "$(/usr/local/bin/brew shellenv)"
```

### Step 2: Install PortAudio

```bash
# Install PortAudio for audio support
brew install portaudio

# Verify installation
brew list portaudio
ls -la $(brew --prefix portaudio)/include/portaudio.h
```

### Step 3: Clone Repository

```bash
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pc_app
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip
```

### Step 5: Install Python Packages

**Important: Use quotes around packages with brackets in zsh!**

```bash
# Install core packages
pip install PyQt6 PyQt6-WebEngine websockets "aiohttp>=3.8.0,<3.9.0" \
    "python-socketio[client]" google-genai numpy opencv-python Pillow \
    pyyaml python-dotenv requests colorama

# Install audio utilities
pip install SpeechRecognition pyttsx3 edge-tts pydub

# Install PyAudio with PortAudio support
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

### Step 6: Configure Application

```bash
# Create config directory
mkdir -p config logs

# Create .env file
cat > config/.env << 'EOF'
# Google Gemini API Key
# Get your key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your_api_key_here

# Application Settings
DEBUG_MODE=false
LOG_LEVEL=INFO
EOF
```

### Step 7: Test Installation

```bash
# Test imports
python -c "import PyQt6; print('✅ PyQt6')"
python -c "import websockets; print('✅ websockets')"
python -c "import pyaudio; print('✅ PyAudio')"
python -c "import speech_recognition; print('✅ SpeechRecognition')"

# Run the app
python main.py
```

---

## Troubleshooting

### Issue 1: Homebrew Not Found

**Symptoms:**
```bash
zsh: command not found: brew
```

**Solution:**

Add Homebrew to your PATH:

**Apple Silicon:**
```bash
eval "$(/opt/homebrew/bin/brew shellenv)"
```

**Intel Mac:**
```bash
eval "$(/usr/local/bin/brew shellenv)"
```

To make it permanent:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

### Issue 2: PyAudio Installation Fails

**Symptoms:**
```
fatal error: 'portaudio.h' file not found
```

**Solution:**

```bash
# Install PortAudio
brew install portaudio

# Find PortAudio location
brew --prefix portaudio

# Install PyAudio with explicit paths
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

**Alternative (if still fails):**
```bash
# For Apple Silicon
CFLAGS="-I/opt/homebrew/include" \
LDFLAGS="-L/opt/homebrew/lib" \
pip install --no-cache-dir pyaudio

# For Intel Mac
CFLAGS="-I/usr/local/include" \
LDFLAGS="-L/usr/local/lib" \
pip install --no-cache-dir pyaudio
```

### Issue 3: aiohttp Version Error

**Symptoms:**
```
ERROR: No matching distribution found for aiohttp>=3.9.0
```

**Solution:**

You're using Python 3.9. Use compatible version:

```bash
pip install "aiohttp>=3.8.0,<3.9.0"
```

Or upgrade Python:
```bash
brew install python@3.11
```

### Issue 4: zsh Bracket Error

**Symptoms:**
```bash
zsh: no matches found: python-socketio[client]
```

**Solution:**

Use quotes around packages with brackets:

```bash
# ✅ Correct
pip install "python-socketio[client]"

# ❌ Wrong
pip install python-socketio[client]
```

### Issue 5: Microphone Permission Denied

**Symptoms:**
- Voice input doesn't work
- "Permission denied" error when using microphone

**Solution:**

1. Open **System Preferences** (or **System Settings** on macOS 13+)
2. Go to **Security & Privacy** → **Privacy**
3. Select **Microphone** from the left sidebar
4. Check the boxes for:
   - **Terminal** (if running from terminal)
   - **Python**
   - Your application name

5. Restart the application

### Issue 6: "Command Not Found" for Python

**Symptoms:**
```bash
zsh: command not found: python
```

**Solution:**

macOS uses `python3` by default:

```bash
# Use python3 instead
python3 main.py

# Or create alias
echo 'alias python=python3' >> ~/.zshrc
source ~/.zshrc
```

### Issue 7: Qt Platform Plugin Error

**Symptoms:**
```
qt.qpa.plugin: Could not load the Qt platform plugin
```

**Solution:**

```bash
# Reinstall PyQt6
pip uninstall PyQt6 PyQt6-WebEngine
pip install PyQt6 PyQt6-WebEngine

# If still fails, install system package
brew install pyqt@6
```

---

## Common Issues

### Virtual Environment Not Activating

```bash
# Make sure you're in the right directory
cd ~/path/to/qt-robot-controller/pc_app

# Activate venv
source venv/bin/activate

# You should see (venv) in your prompt
```

### Packages Not Found After Installation

```bash
# Make sure venv is activated
which python
# Should show: .../pc_app/venv/bin/python

# If not, activate venv and reinstall
source venv/bin/activate
pip install -r requirements.txt
```

### Application Crashes on Startup

```bash
# Check error messages
python main.py 2>&1 | tee error.log

# Test individual components
python -c "import PyQt6; print('PyQt6 OK')"
python -c "import websockets; print('websockets OK')"
python -c "import pyaudio; print('PyAudio OK')"
```

---

## Testing Your Installation

### Basic Tests

```bash
cd pc_app
source venv/bin/activate

# Test 1: Import all packages
python << 'EOF'
import PyQt6
import websockets
import aiohttp
import pyaudio
import speech_recognition
import google.generativeai
import cv2
import PIL
print("✅ All imports successful!")
EOF

# Test 2: Check PyAudio devices
python << 'EOF'
import pyaudio
p = pyaudio.PyAudio()
print(f"Found {p.get_device_count()} audio devices")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"  {i}: {info['name']}")
p.terminate()
EOF

# Test 3: Test speech recognition
python << 'EOF'
import speech_recognition as sr
r = sr.Recognizer()
print("✅ Speech recognition initialized")
EOF

# Test 4: Run the application
python main.py
```

### Full System Test

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Test Connection Dialog**
   - Should see connection dialog
   - Try entering a dummy IP (e.g., 192.168.1.100)

3. **Test Voice (if connected to robot)**
   - Click microphone button
   - Grant permission if prompted
   - Speak a test command

4. **Check Logs**
   ```bash
   tail -f logs/app.log
   ```

---

## Performance Optimization

### For Apple Silicon (M1/M2/M3)

Some packages may have ARM-optimized versions:

```bash
# Install ARM-native packages when available
brew install python@3.11

# Create venv with native Python
/opt/homebrew/bin/python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Enable GPU Acceleration (Optional)

For AI features:

```bash
# Install Metal Performance Shaders support
pip install tensorflow-metal
```

---

## Uninstallation

### Remove Application

```bash
# Remove repository
rm -rf ~/path/to/qt-robot-controller

# Optional: Remove Homebrew packages
brew uninstall portaudio
```

### Keep Homebrew

If you want to keep Homebrew for other uses, just remove PortAudio:

```bash
brew uninstall portaudio
```

---

## Additional Resources

- [Homebrew Documentation](https://docs.brew.sh/)
- [PyQt6 Documentation](https://doc.qt.io/qtforpython/)
- [Python Virtual Environments](https://docs.python.org/3/tutorial/venv.html)
- [macOS Terminal Guide](https://support.apple.com/guide/terminal/welcome/mac)

---

## Getting Help

If you're still having issues:

1. Check the [main troubleshooting guide](TROUBLESHOOTING.md)
2. Search [existing issues](https://github.com/Lottie128/qt-robot-controller/issues)
3. Open a [new issue](https://github.com/Lottie128/qt-robot-controller/issues/new) with:
   - macOS version (`sw_vers`)
   - Python version (`python3 --version`)
   - Error messages
   - Steps to reproduce

---

**Last Updated:** January 2026  
**macOS Versions Tested:** 10.15 (Catalina) through 14.x (Sonoma)
