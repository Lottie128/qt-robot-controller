# Qt Robot Controller

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Qt6](https://img.shields.io/badge/Qt-6.0+-green.svg)](https://www.qt.io/)

A modern, practical distributed robot control system with **Qt desktop application** (PC) and **simple Python script** (Raspberry Pi). No complex network configuration - just run the Pi script, enter the IP in your PC app, and start controlling!

## 🎯 Why This Approach?

**Original System Issues:**
- Flask web server = slower response times
- Manual static IP configuration = tedious setup
- Browser-based = less responsive UI
- Connection breaks when moving networks

**New Qt-Based Solution:**
- ✅ **Native Qt GUI** - Fast, responsive desktop application
- ✅ **Dynamic Network Discovery** - No manual IP configuration
- ✅ **Simple Connection** - Run Pi script, enter IP, connect!
- ✅ **Configurable GPIO** - Change pin mappings in software
- ✅ **Works Anywhere** - Automatically adapts to any network

## ⚡ Quick Start

### 🍎 macOS Users - Start Here!

For the best experience on macOS, use our automated installer:

```bash
# Clone and install in one go
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
chmod +x scripts/macos_install.sh
./scripts/macos_install.sh
```

**What it does:**
- ✅ Auto-detects Apple Silicon (M1/M2/M3) or Intel Mac
- ✅ Installs Homebrew if needed
- ✅ Installs PortAudio for microphone support
- ✅ Fixes Python 3.9 compatibility issues
- ✅ Handles zsh shell quoting correctly
- ✅ Configures audio with proper compiler flags
- ✅ Tests everything automatically

**📖 Full macOS Guide:** See [docs/MACOS_SETUP.md](docs/MACOS_SETUP.md) for detailed instructions and troubleshooting.

---

### Step 1: Setup Raspberry Pi (5 minutes)

```bash
# Clone repository on Pi
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pi_server

# Install dependencies
pip install -r requirements.txt

# Run the Pi server script
python3 server.py
```

**The script will display:**
```
🤖 Robot Server Running!
📡 Connect from PC using this IP: 192.168.1.105
🔌 Port: 8888
⚡ Waiting for connection...
```

### Step 2: Setup PC Application

#### 🍎 macOS (Automated)

```bash
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
./scripts/macos_install.sh

# Then run:
cd pc_app
source venv/bin/activate
python main.py
```

👉 **Having issues?** Check [docs/MACOS_SETUP.md](docs/MACOS_SETUP.md)

#### 🐧 Linux

```bash
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
./scripts/install_pc.sh
```

#### 🪟 Windows

```bash
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller\pc_app
pip install -r requirements.txt
python main.py
```

### Step 3: Connect & Control!

1. **Enter Pi IP** - Type the IP shown on Pi terminal into PC app
2. **Click Connect** - Establishes secure connection
3. **Start Controlling** - Use voice, keyboard, or GUI buttons!

## 📖 Documentation

### Platform-Specific Guides
- **[🍎 macOS Setup Guide](docs/MACOS_SETUP.md)** - Complete macOS installation and troubleshooting
- **General Setup Guide** - [docs/SETUP_GUIDE.md](docs/SETUP_GUIDE.md)
- **GPIO Configuration** - [docs/GPIO_CONFIGURATION.md](docs/GPIO_CONFIGURATION.md)
- **Network Guide** - [docs/NETWORK_GUIDE.md](docs/NETWORK_GUIDE.md)
- **Troubleshooting** - [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

## 📁 Project Structure

```
qt-robot-controller/
├── pc_app/                    # Qt Desktop Application (PC)
│   ├── main.py               # Application entry point
│   ├── ui/                   # User interface components
│   ├── modules/              # Core functionality modules
│   ├── config/               # Configuration files
│   └── requirements.txt      # Python dependencies
│
├── pi_server/                 # Raspberry Pi Server
│   ├── server.py             # Main server script
│   ├── hardware/             # Hardware control modules
│   ├── display/              # Display management
│   └── config/               # Hardware configuration
│
├── docs/                      # Documentation
│   ├── MACOS_SETUP.md        # 🍎 macOS-specific guide
│   ├── SETUP_GUIDE.md
│   ├── GPIO_CONFIGURATION.md
│   └── TROUBLESHOOTING.md
│
├── scripts/                   # Installation & utility scripts
│   ├── macos_install.sh      # 🍎 macOS one-click installer
│   ├── install_pc.sh         # Cross-platform installer
│   ├── install_pi.sh         # Raspberry Pi installer
│   └── test_connection.py    # Network test utility
│
└── README.md
```

## 🔧 Features

### PC Qt Application
- **Modern GUI** - Clean, responsive Qt6 interface
- **Login Screen** - Enter Pi IP and connect
- **Live Video Stream** - View robot camera feed
- **Voice Control** - Speak commands naturally
- **Manual Controls** - Keyboard/mouse control
- **GPIO Settings** - Configure pin mappings in UI
- **AI Chat Interface** - Interact with Gemini AI
- **SLAM Visualization** - Real-time mapping display
- **Status Dashboard** - Battery, sensors, connection status

### Raspberry Pi Server
- **Auto Network Detection** - Displays current IP automatically
- **Simple Socket Server** - Lightweight, fast communication
- **Motor Control** - L298N/TB6612 motor driver support
- **Camera Streaming** - Real-time video over network
- **LiDAR Integration** - RP-LIDAR A1 SLAM support
- **Face Display** - Animated face on LCD/OLED
- **Sensor Monitoring** - Ultrasonic, IMU, battery

## ⚙️ Hardware Configuration

### Default GPIO Pin Mapping (BOARD Mode)

```yaml
Motors (L298N):
  L1 (Left Forward):  Pin 33
  L2 (Left Backward): Pin 38
  R1 (Right Forward): Pin 35
  R2 (Right Backward): Pin 40

Sensors:
  Ultrasonic Trigger: Pin 11
  Ultrasonic Echo:    Pin 13

Camera:
  CSI Camera or USB (auto-detected)

LiDAR:
  USB Serial (/dev/ttyUSB0)
```

**To Change Pins:**
1. Open PC Qt app
2. Go to **Settings → GPIO Configuration**
3. Modify pin numbers
4. Click **Save & Apply**
5. Changes sync automatically to Pi

## 📝 Requirements

### PC Requirements
- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **Python:** 3.9+
- **RAM:** 4GB minimum, 8GB recommended
- **Microphone:** For voice control (optional)

### Raspberry Pi Requirements
- **Model:** Raspberry Pi 3/4/5
- **OS:** Raspberry Pi OS (Bookworm)
- **Python:** 3.9+
- **Camera:** CSI or USB camera
- **Accessories:** L298N motor driver, motors, power supply

## 🎮 Usage

### Starting the System

**1. Start Pi Server (Always First)**
```bash
cd pi_server
python3 server.py
```

Output:
```
🤖 Qt Robot Server v1.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Server IP: 192.168.1.105:8888
⚡ Waiting for PC connection...
```

**2. Launch Qt App (PC)**
```bash
cd pc_app
source venv/bin/activate  # macOS/Linux
python main.py
```

**3. Connect & Control**
- Enter IP from Pi terminal
- Click Connect
- Use voice, keyboard, or GUI controls

## 🐛 Common Issues

### macOS Issues

**PyAudio won't install?**
```bash
brew install portaudio
CFLAGS="-I$(brew --prefix portaudio)/include" \
LDFLAGS="-L$(brew --prefix portaudio)/lib" \
pip install pyaudio
```

**zsh bracket errors?**
```bash
# Use quotes:
pip install "python-socketio[client]"
```

**Microphone permission?**
- System Preferences → Security & Privacy → Microphone
- Enable Terminal/Python

**📖 Full troubleshooting:** [docs/MACOS_SETUP.md](docs/MACOS_SETUP.md)

### Pi/PC Connection Issues

```bash
# Test connection
ping <pi-ip>
telnet <pi-ip> 8888

# Check firewall
sudo ufw allow 8888/tcp
```

## 🔒 Security Notes

**Current Setup (Home/Lab):**
- Local network only
- No authentication
- Simple, fast communication

**For Production:** Add authentication, SSL/TLS, rate limiting

## 🤝 Contributing

Contributions welcome!

1. Fork the repository
2. Create feature branch (`git checkout -b feature/name`)
3. Commit changes
4. Push and open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🙏 Acknowledgments

- Inspired by [vivan129/distributed-robot-system](https://github.com/vivan129/distributed-robot-system)
- Built with Qt6, Python, and Raspberry Pi
- Google Gemini AI integration

## 🔗 Resources

### Documentation
- **[🍎 macOS Setup](docs/MACOS_SETUP.md)** - Complete macOS guide
- [Setup Guide](docs/SETUP_GUIDE.md)
- [GPIO Configuration](docs/GPIO_CONFIGURATION.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

### External Links
- [Qt for Python](https://doc.qt.io/qtforpython/)
- [Raspberry Pi GPIO](https://pinout.xyz/)
- [Google Gemini API](https://ai.google.dev/)
- [Homebrew](https://docs.brew.sh/)

### Project Links
- **GitHub:** [Lottie128/qt-robot-controller](https://github.com/Lottie128/qt-robot-controller)
- **Issues:** [Report bugs](https://github.com/Lottie128/qt-robot-controller/issues)
- **Discussions:** [Get help](https://github.com/Lottie128/qt-robot-controller/discussions)

---

**Made with ❤️ by robotics enthusiasts**

⭐ **If this project helps you, please star it!**

---

## 🚨 Quick Command Reference

### macOS
```bash
# Install
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller && ./scripts/macos_install.sh

# Run
cd pc_app && source venv/bin/activate && python main.py
```

### Raspberry Pi
```bash
# Setup
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pi_server && pip install -r requirements.txt

# Run
python3 server.py
```

### Testing
```bash
# Test connection from PC
ping <pi-ip>
python scripts/test_connection.py <pi-ip>

# Test imports
python -c "import PyQt6, websockets, pyaudio; print('OK')"
```