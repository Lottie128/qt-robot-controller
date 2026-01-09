# Setup Guide - Qt Robot Controller

Complete setup instructions for both Raspberry Pi and PC application.

## Table of Contents

1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi Setup](#raspberry-pi-setup)
3. [PC Application Setup](#pc-application-setup)
4. [First Connection](#first-connection)
5. [Testing](#testing)

## Hardware Requirements

### Raspberry Pi Components

**Required:**
- Raspberry Pi 3 Model B+ or newer (4/5 recommended)
- MicroSD card (16GB minimum, 32GB recommended)
- Power supply (5V 3A for Pi 4/5)
- L298N or TB6612 motor driver
- DC motors (2x for differential drive)
- Robot chassis with wheels

**Optional:**
- Raspberry Pi Camera Module or USB webcam
- RP-LIDAR A1/A2 for SLAM
- HC-SR04 ultrasonic sensor
- MPU6050 IMU sensor
- OLED display (128x64 SSD1306)
- Battery pack with voltage regulator

### PC Requirements

- **Operating System:** Windows 10/11, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **Python:** 3.9 or newer
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Network:** WiFi or Ethernet connection

## Raspberry Pi Setup

### Step 1: Install Raspberry Pi OS

1. **Download Raspberry Pi Imager:**
   - Visit: https://www.raspberrypi.com/software/
   - Install for your platform

2. **Flash OS to SD Card:**
   ```bash
   # Choose "Raspberry Pi OS (64-bit)" - recommended
   # or "Raspberry Pi OS Lite" for headless setup
   ```

3. **Configure Before First Boot:**
   - Click settings gear icon
   - Set hostname: `robot-pi`
   - Enable SSH
   - Configure WiFi credentials
   - Set username/password

### Step 2: Initial System Configuration

1. **Boot and Connect:**
   ```bash
   # From your PC, SSH into Pi
   ssh pi@robot-pi.local
   # Or use IP address if hostname doesn't resolve
   ssh pi@192.168.1.xxx
   ```

2. **Update System:**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo reboot
   ```

3. **Install System Dependencies:**
   ```bash
   sudo apt install -y \
     python3-pip \
     python3-dev \
     python3-opencv \
     python3-pyaudio \
     git \
     i2c-tools \
     libatlas-base-dev \
     libhdf5-dev \
     libjpeg-dev \
     libopenblas-dev
   ```

### Step 3: Enable Hardware Interfaces

1. **Run Configuration Tool:**
   ```bash
   sudo raspi-config
   ```

2. **Enable Interfaces:**
   - Navigate to: **Interface Options**
   - Enable:
     - Camera (if using CSI camera)
     - I2C (for sensors/displays)
     - SPI (if needed)
     - Serial Port (for LiDAR)

3. **Reboot:**
   ```bash
   sudo reboot
   ```

### Step 4: Setup GPIO Permissions

```bash
# Add user to GPIO groups
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER
sudo usermod -a -G spi $USER
sudo usermod -a -G dialout $USER

# Create udev rules for LiDAR
sudo nano /etc/udev/rules.d/99-rplidar.rules
```

Add:
```
KERNEL=="ttyUSB*", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE:="0666", GROUP:="dialout", SYMLINK+="rplidar"
```

Reload and logout:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
logout
```

### Step 5: Install Robot Software

1. **Clone Repository:**
   ```bash
   cd ~
   git clone https://github.com/Lottie128/qt-robot-controller.git
   cd qt-robot-controller
   ```

2. **Install Python Dependencies:**
   ```bash
   cd pi_server
   pip3 install -r requirements.txt
   ```

3. **Test Installation:**
   ```bash
   python3 server.py
   ```

   You should see:
   ```
   🤖 Qt Robot Server v1.0.0
   📡 Network Interfaces:
      • eth0: 192.168.1.105
   ```

### Step 6: Configure Hardware

1. **Edit Configuration:**
   ```bash
   nano config/hardware_config.yaml
   ```

2. **Set GPIO Pins:**
   ```yaml
   motors:
     pin_mode: "BOARD"  # or "BCM"
     pins:
       L1: 33  # Adjust to your wiring
       L2: 38
       R1: 35
       R2: 40
   ```

3. **Save and Test:**
   ```bash
   python3 server.py
   ```

### Step 7: Setup Auto-Start (Optional)

1. **Create Systemd Service:**
   ```bash
   sudo nano /etc/systemd/system/robot-server.service
   ```

2. **Add Configuration:**
   ```ini
   [Unit]
   Description=Qt Robot Controller Server
   After=network.target

   [Service]
   Type=simple
   User=pi
   WorkingDirectory=/home/pi/qt-robot-controller/pi_server
   ExecStart=/usr/bin/python3 /home/pi/qt-robot-controller/pi_server/server.py
   Restart=on-failure
   RestartSec=5

   [Install]
   WantedBy=multi-user.target
   ```

3. **Enable Service:**
   ```bash
   sudo systemctl enable robot-server
   sudo systemctl start robot-server
   sudo systemctl status robot-server
   ```

## PC Application Setup

### Step 1: Install Python

**Windows:**
1. Download from: https://www.python.org/downloads/
2. Run installer
3. **Check:** "Add Python to PATH"
4. Click "Install Now"

**macOS:**
```bash
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Step 2: Clone Repository

```bash
# Navigate to desired location
cd ~/Projects  # or C:\Users\YourName\Projects on Windows

# Clone repository
git clone https://github.com/Lottie128/qt-robot-controller.git
cd qt-robot-controller
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
cd pc_app
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Configure API Keys (Optional)

For AI features:

1. **Copy Environment Template:**
   ```bash
   cp config/.env.example config/.env
   ```

2. **Edit Configuration:**
   ```bash
   nano config/.env  # or use text editor
   ```

3. **Add API Keys:**
   ```
   GEMINI_API_KEY=your_google_gemini_api_key_here
   ```

### Step 6: Test Installation

```bash
python3 main.py
```

Application window should open.

## First Connection

### Step 1: Start Pi Server

On Raspberry Pi:
```bash
cd ~/qt-robot-controller/pi_server
python3 server.py
```

Note the displayed IP address (e.g., `192.168.1.105`)

### Step 2: Launch PC Application

On PC:
```bash
cd qt-robot-controller/pc_app
source venv/bin/activate  # if using virtual environment
python3 main.py
```

### Step 3: Connect

1. **Enter Connection Details:**
   - IP Address: `192.168.1.105` (from Pi terminal)
   - Port: `8888` (default)

2. **Click "Connect"**

3. **Verify Connection:**
   - PC app shows "Connected"
   - Pi terminal shows "Client connected"

### Step 4: Test Basic Movement

1. **Use Keyboard:**
   - Arrow Up: Move forward
   - Arrow Down: Move backward
   - Arrow Left: Turn left
   - Arrow Right: Turn right
   - Space: Stop

2. **Or Use GUI Buttons**

## Testing

### Test Motors

```bash
# On Pi, test motor controller
cd ~/qt-robot-controller/pi_server
python3 -c "from hardware.motor_controller import MotorController; \
m = MotorController({'pins': {'L1': 33, 'L2': 38, 'R1': 35, 'R2': 40}}); \
m.move_forward(50); import time; time.sleep(2); m.stop(); m.cleanup()"
```

### Test Camera

```bash
# Test camera capture
python3 -c "import cv2; cap = cv2.VideoCapture(0); \
ret, frame = cap.read(); print('Camera OK' if ret else 'Camera FAILED'); cap.release()"
```

### Test Sensors

```bash
# Test ultrasonic sensor
python3 -c "from hardware.sensors import UltrasonicSensor; \
s = UltrasonicSensor(11, 13); print(f'Distance: {s.get_distance()} cm')"
```

### Network Test

```bash
# From PC, test connectivity
ping 192.168.1.105

# Test port
telnet 192.168.1.105 8888
```

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

## Next Steps

- Configure GPIO pins: [GPIO_CONFIGURATION.md](GPIO_CONFIGURATION.md)
- Network setup: [NETWORK_GUIDE.md](NETWORK_GUIDE.md)
- Advanced features: See main [README.md](../README.md)
