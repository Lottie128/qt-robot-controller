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

## ⚡ Quick Start (3 Steps!)

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

### Step 2: Setup PC Application (5 minutes)

```bash
# Clone repository on PC
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pc_app

# Install Qt dependencies
pip install -r requirements.txt

# Run the Qt application
python3 main.py
```

### Step 3: Connect & Control!

1. **Enter Pi IP** - Type the IP shown on Pi terminal into PC app
2. **Click Connect** - Establishes secure connection
3. **Start Controlling** - Use voice, keyboard, or GUI buttons!

## 📁 Project Structure

```
qt-robot-controller/
├── pc_app/                    # Qt Desktop Application (PC)
│   ├── main.py               # Application entry point
│   ├── ui/
│   │   ├── main_window.py    # Main Qt window
│   │   ├── login_dialog.py   # Connection dialog
│   │   ├── settings_dialog.py # GPIO & settings configuration
│   │   └── resources/        # UI assets, icons, themes
│   ├── modules/
│   │   ├── network_client.py # Socket client for Pi communication
│   │   ├── ai_brain.py       # Google Gemini integration
│   │   ├── voice_input.py    # Speech recognition
│   │   ├── tts_engine.py     # Text-to-speech
│   │   ├── face_animator.py  # Face animation engine
│   │   └── vision_processor.py
│   ├── config/
│   │   └── app_config.yaml   # Application configuration
│   └── requirements.txt
│
├── pi_server/                 # Raspberry Pi Server Script
│   ├── server.py             # Main server script (simple!)
│   ├── hardware/
│   │   ├── motor_controller.py
│   │   ├── camera_module.py
│   │   ├── lidar_module.py
│   │   └── sensors.py
│   ├── display/
│   │   └── face_display.py   # LCD/screen face display
│   ├── config/
│   │   └── hardware_config.yaml
│   └── requirements.txt
│
├── shared/                    # Shared utilities
│   ├── protocol.py           # Communication protocol
│   └── constants.py          # Shared constants
│
├── docs/                      # Documentation
│   ├── SETUP_GUIDE.md
│   ├── GPIO_CONFIGURATION.md
│   ├── NETWORK_GUIDE.md
│   └── TROUBLESHOOTING.md
│
├── scripts/                   # Utility scripts
│   ├── install_pc.sh         # PC setup script
│   ├── install_pi.sh         # Pi setup script
│   └── test_connection.py    # Test network connection
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

## 🔌 Network Communication

### How It Works

1. **Pi Server Starts** → Binds to all interfaces (`0.0.0.0:8888`)
2. **Auto-detects IP** → Shows local IP on terminal
3. **PC Connects** → User enters IP in Qt app login
4. **WebSocket Established** → Fast bidirectional communication
5. **Commands Flow** → PC sends, Pi executes, responds

### Protocol

```python
# Command Structure (JSON over WebSocket)
{
    "type": "command",
    "action": "move_forward",
    "params": {"speed": 70, "duration": 2.0}
}

# Response Structure
{
    "type": "response",
    "status": "success",
    "data": {"distance_traveled": 1.5}
}
```

## 📝 Requirements

### PC Requirements
- **OS:** Windows 10/11, macOS 10.15+, or Linux
- **Python:** 3.9+
- **RAM:** 4GB minimum, 8GB recommended
- **GPU:** Optional (for AI acceleration)

### Raspberry Pi Requirements
- **Model:** Raspberry Pi 3/4/5
- **OS:** Raspberry Pi OS (Bookworm)
- **Python:** 3.9+
- **Camera:** CSI or USB camera
- **Accessories:** L298N motor driver, motors, power supply

## 🚀 Detailed Setup

### PC Installation

```bash
# Clone repository
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pc_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Configure API keys (optional for AI features)
cp config/.env.example config/.env
nano config/.env  # Add GEMINI_API_KEY

# Run application
python3 main.py
```

### Raspberry Pi Installation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install system dependencies
sudo apt install -y python3-pip python3-opencv python3-pyaudio
sudo apt install -y libatlas-base-dev libhdf5-dev libjpeg-dev

# Clone repository
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller/pi_server

# Install Python packages
pip install -r requirements.txt

# Enable camera (if using CSI)
sudo raspi-config
# Navigate to: Interface Options → Camera → Enable

# Setup GPIO permissions
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER

# Reboot
sudo reboot

# After reboot, run server
cd qt-robot-controller/pi_server
python3 server.py
```

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
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📡 Network Interfaces:
   • eth0: 192.168.1.105
   • wlan0: 192.168.1.106

🔌 Server running on 0.0.0.0:8888
⚡ Waiting for PC connection...
```

**2. Launch Qt App (PC)**
```bash
cd pc_app
python3 main.py
```

**3. Connect**
- Enter IP: `192.168.1.105` (from Pi terminal)
- Port: `8888` (default)
- Click **Connect**

**4. Control Your Robot!**
- **Voice:** Click mic button, speak "Move forward"
- **Keyboard:** Arrow keys for movement
- **GUI:** Click direction buttons

### Configuration Changes

**Change GPIO Pins:**
1. PC App → **Settings** → **Hardware Configuration**
2. Modify pin numbers
3. Click **Apply**
4. Pi automatically updates without restart!

**Change Network Port:**
- Edit `pi_server/config/hardware_config.yaml`
- Change `server_port: 8888` to desired port
- Restart Pi server

## 🐛 Troubleshooting

### Pi Server Won't Start

```bash
# Check port availability
sudo netstat -tulpn | grep 8888

# If port in use, kill process
sudo kill -9 <PID>

# Or change port in hardware_config.yaml
```

### PC Can't Connect

```bash
# Test connectivity from PC
ping 192.168.1.105  # Use your Pi IP

# Test port
telnet 192.168.1.105 8888

# Check firewall on Pi
sudo ufw status
sudo ufw allow 8888/tcp
```

### "RPi.GPIO Not Found" on Pi

```bash
# Install GPIO library
pip install RPi.GPIO

# If permission error
sudo usermod -a -G gpio $USER
logout  # Then login again
```

### Qt App Shows "Module Not Found"

```bash
# Reinstall Qt dependencies
pip install PyQt6 PyQt6-WebEngine --upgrade

# On Ubuntu, may need system packages
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine
```

### Motors Not Responding

1. **Check Wiring** - Verify GPIO connections
2. **Check Pin Config** - Settings → Hardware → Verify pins
3. **Check Power** - Motor driver needs external power (not Pi)
4. **Test Manual** - Use PC app test panel
5. **Check Permissions**:
   ```bash
   sudo usermod -a -G gpio $USER
   ```

### Camera Not Working

```bash
# List video devices
ls -l /dev/video*

# Test camera
raspistill -o test.jpg  # CSI camera
vcgencmd get_camera     # Check if detected

# For USB camera
v4l2-ctl --list-devices
```

## 🔒 Security Considerations

### For Home/Lab Use (Current Setup)
- ✅ Local network only
- ✅ No authentication (trusted network)
- ✅ Simple, fast communication

### For Public/Production Use (Recommended Changes)

```python
# Add authentication token
CONNECTION_TOKEN = "your_secret_token_here"

# Use SSL/TLS
import ssl
context = ssl.create_default_context()

# Implement user authentication
# Rate limiting
# Encrypted communication
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by [vivan129/distributed-robot-system](https://github.com/vivan129/distributed-robot-system)
- Built with Qt6 and Python
- Google Gemini AI integration
- Raspberry Pi community

## 📚 Additional Resources

- [Qt for Python Documentation](https://doc.qt.io/qtforpython/)
- [Raspberry Pi GPIO Guide](https://pinout.xyz/)
- [Google Gemini API](https://ai.google.dev/)
- [WebSocket Protocol](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)

## 🔗 Links

- **GitHub:** [https://github.com/Lottie128/qt-robot-controller](https://github.com/Lottie128/qt-robot-controller)
- **Issues:** [Report bugs or request features](https://github.com/Lottie128/qt-robot-controller/issues)
- **Discussions:** [Ask questions and share ideas](https://github.com/Lottie128/qt-robot-controller/discussions)

---

**Made with ❤️ by robotics enthusiasts**

⭐ If this project helps you, please give it a star!