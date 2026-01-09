# macOS Quick Reference Card

**One-page reference for Qt Robot Controller on macOS**

## 🚀 Installation (The Working Method)

### Automated Install (Recommended)

```bash
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
chmod +x scripts/macos_install.sh
./scripts/macos_install.sh
```

### Manual Install (What Actually Works)

```bash
# 1. Setup Homebrew
eval "$(/usr/local/bin/brew shellenv)"  # Intel Mac
# OR
eval "$(/opt/homebrew/bin/brew shellenv)"  # Apple Silicon

# 2. Install PortAudio
brew install portaudio

# 3. Clone & Navigate
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pc_app

# 4. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 5. Install Core Packages (IMPORTANT: Use quotes!)
pip install PyQt6 PyQt6-WebEngine websockets "aiohttp>=3.8.0,<3.9.0" \
    "python-socketio[client]" google-genai numpy opencv-python Pillow \
    pyyaml python-dotenv requests colorama

# 6. Install Audio Packages
pip install SpeechRecognition pyttsx3 edge-tts pydub

# 7. Install PyAudio (Critical Step!)
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio

# 8. Setup Config
mkdir -p config logs
echo "GEMINI_API_KEY=your_key_here" > config/.env

# 9. Run!
python main.py
```

## 🔑 Key Points That Fixed Everything

### 1. Homebrew Path Issue
**Problem:** `zsh: command not found: brew`

**Solution:**
```bash
# Add to PATH (choose your Mac type):
eval "$(/opt/homebrew/bin/brew shellenv)"    # Apple Silicon
eval "$(/usr/local/bin/brew shellenv)"      # Intel Mac

# Make permanent:
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
```

### 2. zsh Bracket Quoting
**Problem:** `zsh: no matches found: python-socketio[client]`

**Solution:** Always quote packages with brackets
```bash
✅ pip install "python-socketio[client]"
❌ pip install python-socketio[client]
```

### 3. Python 3.9 Compatibility
**Problem:** `No matching distribution found for aiohttp>=3.9.0`

**Solution:** Use older version
```bash
pip install "aiohttp>=3.8.0,<3.9.0"
```

### 4. PyAudio Compilation
**Problem:** `fatal error: 'portaudio.h' file not found`

**Solution:** Install PortAudio + use compiler flags
```bash
brew install portaudio
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

## 🧑‍💻 Daily Usage

### Starting the App
```bash
cd ~/path/to/qt-robot-controller/pc_app
source venv/bin/activate
python main.py
```

### One-Liner Startup
```bash
cd ~/Documents/codes/qt-robot-controller/pc_app && \
source venv/bin/activate && \
python main.py
```

### Updating Dependencies
```bash
cd pc_app
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 🔧 Troubleshooting Commands

### Check Homebrew
```bash
brew --version
brew --prefix
brew list portaudio
```

### Check Python Environment
```bash
which python
python --version
which pip
pip list | grep -i pyaudio
```

### Test Imports
```bash
python -c "import PyQt6; print('✅ PyQt6')"
python -c "import websockets; print('✅ websockets')"
python -c "import pyaudio; print('✅ PyAudio')"
python -c "import speech_recognition; print('✅ SpeechRecognition')"
```

### Test Audio Devices
```bash
python << 'EOF'
import pyaudio
p = pyaudio.PyAudio()
print(f"Audio devices: {p.get_device_count()}")
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    print(f"  {i}: {info['name']}")
p.terminate()
EOF
```

### Check Virtual Environment
```bash
which python  # Should show: /path/to/venv/bin/python
echo $VIRTUAL_ENV  # Should show venv path
```

## 🚨 Emergency Fixes

### Reset Everything
```bash
cd qt-robot-controller/pc_app
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
# Then reinstall packages (see above)
```

### Reinstall PyAudio
```bash
source venv/bin/activate
pip uninstall pyaudio
brew reinstall portaudio
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install --no-cache-dir pyaudio
```

### Fix Microphone Permission
1. System Preferences → Security & Privacy → Privacy
2. Microphone → Enable Terminal/Python
3. Restart application

## 📝 Environment Variables

### Add to ~/.zshrc or ~/.zprofile

```bash
# Homebrew (Apple Silicon)
eval "$(/opt/homebrew/bin/brew shellenv)"

# Homebrew (Intel)
eval "$(/usr/local/bin/brew shellenv)"

# Python alias (optional)
alias python=python3
alias pip=pip3

# Project shortcut (optional)
alias robot="cd ~/Documents/codes/qt-robot-controller/pc_app && source venv/bin/activate"
```

Reload shell:
```bash
source ~/.zshrc
```

## 🧐 Understanding the Fixes

### Why Quote Brackets?
zsh interprets brackets as glob patterns. Quotes prevent this.

### Why Older aiohttp?
Python 3.9 is older; aiohttp 3.9+ requires Python 3.10+

### Why Compiler Flags?
PyAudio is a C extension that needs PortAudio headers and libraries.

### Why Homebrew Path?
macOS doesn't add Homebrew to PATH by default.

## 📊 Version Info

**Tested On:**
- macOS Sonoma 14.x
- Python 3.9.x
- Homebrew 4.x
- Apple Silicon & Intel Macs

**Working Package Versions:**
- PyQt6 >= 6.6.0
- aiohttp 3.8.x (for Python 3.9)
- PyAudio >= 0.2.14
- websockets >= 12.0

## 🔗 Quick Links

- [Full macOS Setup Guide](MACOS_SETUP.md)
- [Main README](../README.md)
- [Troubleshooting](TROUBLESHOOTING.md)
- [Report Issue](https://github.com/Lottie128/qt-robot-controller/issues)

---

**Last Updated:** January 2026  
**Tested:** Intel & Apple Silicon Macs