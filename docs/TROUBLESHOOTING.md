# Troubleshooting Guide

Common issues and solutions for Qt Robot Controller.

## Table of Contents

1. [Connection Issues](#connection-issues)
2. [Motor Problems](#motor-problems)
3. [Camera Issues](#camera-issues)
4. [Sensor Problems](#sensor-problems)
5. [Software Errors](#software-errors)
6. [Performance Issues](#performance-issues)

## Connection Issues

### Pi Server Won't Start

**Error: `Address already in use`**

```bash
# Find process using port 8888
sudo netstat -tulpn | grep 8888

# Kill the process
sudo kill -9 <PID>

# Or use different port
nano config/hardware_config.yaml
# Change server_port to 8889
```

**Error: `Permission denied`**

```bash
# Add user to required groups
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER
sudo usermod -a -G dialout $USER

# Logout and login again
logout
```

**Error: `Module not found`**

```bash
# Reinstall dependencies
cd ~/qt-robot-controller/pi_server
pip3 install -r requirements.txt --force-reinstall

# Or install specific missing module
pip3 install websockets
```

### PC Can't Connect to Pi

**Error: `Connection refused`**

✅ **Solutions:**

1. **Check Pi server is running:**
   ```bash
   # On Pi
   sudo netstat -tulpn | grep 8888
   ```

2. **Verify IP address:**
   ```bash
   # On Pi
   hostname -I
   ```

3. **Test connectivity:**
   ```bash
   # From PC
   ping 192.168.1.100  # Use your Pi IP
   ```

4. **Check firewall:**
   ```bash
   # On Pi
   sudo ufw status
   sudo ufw allow 8888/tcp
   ```

**Error: `Connection timeout`**

✅ **Solutions:**

1. **Wrong IP address** - Double-check IP from Pi terminal
2. **Different networks** - Ensure PC and Pi on same WiFi
3. **Firewall blocking** - Temporarily disable to test
4. **Wrong port** - Verify using 8888 (default)

**Error: `No route to host`**

✅ **Solutions:**

```bash
# Check if devices on same subnet
# Pi: 192.168.1.100
# PC: 192.168.1.50
# Both should start with 192.168.1.x

# Check routing
ip route

# Check WiFi connection
iwconfig wlan0
```

### Connection Drops Frequently

**WiFi Signal Issues:**

```bash
# Check signal strength on Pi
iwconfig wlan0 | grep -i "signal level"
# Should be > -70 dBm for good connection

# Disable power management
sudo nano /etc/rc.local
# Add before exit 0:
iwconfig wlan0 power off
```

**Network Congestion:**

- Move to 5GHz WiFi if available
- Reduce camera quality/framerate
- Use Ethernet instead

**Router Issues:**

- Restart router
- Update router firmware
- Change WiFi channel (less congestion)

## Motor Problems

### Motors Don't Move

**Check 1: Power Supply**

❌ **Common Mistake:** Powering motors from Pi
- Motors need **separate power supply**
- 7-12V battery for motor driver
- Pi and motor driver share common ground

✅ **Correct Wiring:**
```
Battery (+) → Motor Driver VM
Battery (-) → Motor Driver GND
Pi GND → Motor Driver GND (common ground)
Pi GPIO → Motor Driver IN1-IN4
Motors → Motor Driver OUT1-OUT4
```

**Check 2: GPIO Configuration**

```bash
# Test GPIO output
sudo python3 << EOF
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)

print("Testing GPIO 33...")
for i in range(5):
    GPIO.output(33, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(33, GPIO.LOW)
    time.sleep(0.5)

GPIO.cleanup()
print("Test complete")
EOF
```

**Check 3: Pin Configuration**

```bash
# Verify configuration
cat ~/qt-robot-controller/pi_server/config/hardware_config.yaml

# Test with simple script
cd ~/qt-robot-controller/pi_server
python3 << EOF
from hardware.motor_controller import MotorController
import time

config = {'pins': {'L1': 33, 'L2': 38, 'R1': 35, 'R2': 40}}
motor = MotorController(config)
motor.move_forward(70)
time.sleep(2)
motor.stop()
motor.cleanup()
EOF
```

**Check 4: Motor Driver**

- LED indicators on driver should light up
- Check for loose connections
- Test with multimeter
- Enable pin (ENA/ENB) must be HIGH

### Motors Move in Wrong Direction

✅ **Solution 1:** Swap motor wires
```
Motor OUT1 ↔ OUT2
```

✅ **Solution 2:** Swap GPIO pins in config
```yaml
motors:
  pins:
    L1: 38  # Swap these
    L2: 33  # two pins
```

### Motors Weak or Slow

**Check voltage:**
```bash
# Use multimeter
# Battery should be 9-12V for most motors
# Below 7V = weak performance
```

**Increase PWM frequency:**
```yaml
motors:
  pwm_frequency: 1000  # Try higher value
  default_speed: 100   # Increase speed
```

**Check battery:**
- Charge battery
- Replace if old
- Check connections

### One Motor Doesn't Work

1. **Swap motor connections** - Test if motor is faulty
2. **Check wiring** - Loose connection
3. **Test GPIO pin** - Use different pin
4. **Motor driver channel** - May be damaged

## Camera Issues

### Camera Not Detected

**For CSI Camera:**

```bash
# Enable camera interface
sudo raspi-config
# Interface Options → Camera → Enable

# Check if detected
vcgencmd get_camera
# Should show: supported=1 detected=1

# Test capture
raspistill -o test.jpg
```

**For USB Camera:**

```bash
# List video devices
ls -l /dev/video*

# Check device info
v4l2-ctl --list-devices

# Test with OpenCV
python3 -c "import cv2; cap = cv2.VideoCapture(0); print('OK' if cap.read()[0] else 'FAIL')"
```

### Camera Shows Black Screen

**CSI Camera:**
- Check ribbon cable connection
- Cable inserted correct way (blue side up)
- Camera not covered/lens cap removed

**USB Camera:**
- Try different USB port
- Check if camera LED is on
- Test on different computer

### Poor Video Quality

**Adjust settings:**
```yaml
camera:
  width: 640  # Lower if laggy
  height: 480
  fps: 30
  stream_quality: 80  # 0-100, lower = smaller file
```

**Lighting:**
- Add more light to environment
- Avoid pointing at bright lights

### Video Lag/Delay

**Reduce resolution:**
```yaml
camera:
  width: 320
  height: 240
  fps: 15
  stream_quality: 60
```

**Check network:**
```bash
ping -c 100 <pi-ip>
# Should have < 50ms latency, 0% loss
```

**Use Ethernet:**
- WiFi adds latency
- Ethernet = more stable

## Sensor Problems

### Ultrasonic Sensor Returns Invalid Data

**Check wiring:**
```
Ultrasonic  Raspberry Pi
=========================
VCC      →  5V (Pin 2)
Trig     →  GPIO 11
Echo     →  GPIO 13 (via voltage divider!)
GND      →  GND
```

⚠️ **CRITICAL:** Echo pin needs voltage divider!
- Echo outputs 5V
- Pi GPIO accepts max 3.3V
- Use 1kΩ and 2kΩ resistors

**Test sensor:**
```bash
python3 << EOF
from hardware.sensors import UltrasonicSensor
import time

sensor = UltrasonicSensor(trigger_pin=11, echo_pin=13)

for i in range(10):
    dist = sensor.get_distance()
    print(f"Distance: {dist} cm")
    time.sleep(0.5)
EOF
```

### I2C Devices Not Detected

**Enable I2C:**
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

**Check detection:**
```bash
# Install tools
sudo apt install i2c-tools

# Scan bus
sudo i2cdetect -y 1

# Should show device address (e.g., 0x68 for MPU6050)
```

**If not detected:**
- Check wiring (SDA to Pin 3, SCL to Pin 5)
- Use pull-up resistors (4.7kΩ)
- Check device is powered
- Try different I2C address

### LiDAR Not Working

**Check USB connection:**
```bash
# List USB devices
lsusb

# Check serial ports
ls -l /dev/ttyUSB*
```

**Permissions:**
```bash
sudo usermod -a -G dialout $USER
logout
```

**Test LiDAR:**
```bash
python3 << EOF
from rplidar import RPLidar

lidar = RPLidar('/dev/ttyUSB0')
info = lidar.get_info()
print(info)
lidar.disconnect()
EOF
```

## Software Errors

### Import Errors

**Error: `No module named 'XXX'`**

```bash
# Check installed packages
pip3 list

# Install missing package
pip3 install <package-name>

# Reinstall all dependencies
cd pi_server  # or pc_app
pip3 install -r requirements.txt
```

### Python Version Issues

**Check version:**
```bash
python3 --version
# Should be 3.9 or newer
```

**Update Python:**
```bash
sudo apt update
sudo apt install python3.11
```

### RPi.GPIO Errors

**Error: `RuntimeError: Not running on a RPi`**

- This is expected when testing on PC
- Code will use mock GPIO automatically

**Error: `RuntimeError: Please set pin numbering mode`**

```python
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BOARD)  # Add this before GPIO.setup()
```

**Error: `GPIO already in use`**

```python
# Add at start of script
import RPi.GPIO as GPIO
GPIO.setwarnings(False)
GPIO.cleanup()  # Clean previous usage
```

### Qt Application Won't Start

**Linux:**
```bash
# Install Qt dependencies
sudo apt install python3-pyqt6 python3-pyqt6.qtwebengine

# Or use pip
pip3 install PyQt6 PyQt6-WebEngine
```

**macOS:**
```bash
brew install pyqt@6
pip3 install PyQt6 PyQt6-WebEngine
```

**Windows:**
```cmd
pip install PyQt6 PyQt6-WebEngine
```

## Performance Issues

### High CPU Usage on Pi

**Check processes:**
```bash
top
# Press '1' to see all cores
# Press 'q' to quit
```

**Reduce camera load:**
```yaml
camera:
  fps: 15      # Lower framerate
  width: 320   # Lower resolution
```

**Disable unused features:**
```yaml
lidar:
  enabled: false  # If not using
camera:
  enabled: false  # If not needed
```

### Pi Overheating

**Check temperature:**
```bash
vcgencmd measure_temp
# Should be < 80°C
```

**Solutions:**
- Add heatsink
- Add cooling fan
- Improve ventilation
- Reduce CPU load

### Slow Response Time

**Network latency:**
```bash
ping <pi-ip>
# Should be < 50ms
```

**Reduce processing:**
- Lower camera resolution
- Disable AI features
- Use Ethernet connection

## Emergency Procedures

### Robot Won't Stop

1. **Press SPACE key** in PC app
2. **Click STOP button**
3. **Disconnect from PC app**
4. **Kill Pi server:**
   ```bash
   pkill -f server.py
   ```
5. **Cut motor power** (emergency switch)

### Complete System Reset

**On Pi:**
```bash
# Stop server
pkill -f server.py

# Reset GPIO
sudo python3 -c "import RPi.GPIO as GPIO; GPIO.cleanup()"

# Restart server
cd ~/qt-robot-controller/pi_server
python3 server.py
```

**On PC:**
- Close application
- Restart application
- Reconnect

### Factory Reset Configuration

```bash
# Backup current config
cp config/hardware_config.yaml config/hardware_config.yaml.backup

# Restore from git
git checkout config/hardware_config.yaml

# Or download fresh copy
wget https://raw.githubusercontent.com/Lottie128/qt-robot-controller/main/pi_server/config/hardware_config.yaml
```

## Getting Help

### Gather Information

Before asking for help, collect:

```bash
# System info
uname -a
python3 --version
pip3 list

# Network info
ifconfig
ip addr

# Error logs
cat ~/qt-robot-controller/pi_server/logs/robot.log

# Configuration
cat ~/qt-robot-controller/pi_server/config/hardware_config.yaml
```

### Enable Debug Mode

```yaml
# In hardware_config.yaml
logging:
  level: "DEBUG"  # More detailed logs
  log_to_file: true
```

### Report Issue

1. **GitHub Issues:** https://github.com/Lottie128/qt-robot-controller/issues
2. **Include:**
   - Error message (full text)
   - What you were trying to do
   - System information
   - Configuration files
   - Steps to reproduce

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| `Address already in use` | Port 8888 in use | Kill process or use different port |
| `Permission denied` | Not in gpio group | Add user to groups, logout/login |
| `Connection refused` | Server not running | Start Pi server |
| `No route to host` | Network issue | Check WiFi/Ethernet connection |
| `Module not found` | Missing dependency | `pip3 install -r requirements.txt` |
| `Camera not found` | Camera not enabled | Enable in raspi-config |
| `GPIO already in use` | Previous process | `GPIO.cleanup()` |
| `Timeout` | Network latency | Use Ethernet, reduce camera quality |

## Prevention Tips

### Regular Maintenance

- Update software monthly
- Check connections before each use
- Monitor battery voltage
- Clean sensors
- Backup configuration

### Best Practices

- Use version control (git)
- Document custom changes
- Test after modifications
- Keep spare parts
- Label wires

### Before Running

✅ **Checklist:**
- [ ] Battery charged
- [ ] All cables connected
- [ ] Clear operating area
- [ ] Emergency stop accessible
- [ ] Network connection stable
- [ ] Latest software version

---

**Still having issues?**

Check the other documentation:
- [Setup Guide](SETUP_GUIDE.md)
- [GPIO Configuration](GPIO_CONFIGURATION.md)
- [Network Guide](NETWORK_GUIDE.md)
- Main [README](../README.md)
