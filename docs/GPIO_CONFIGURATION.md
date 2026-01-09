# GPIO Configuration Guide

Complete guide for configuring GPIO pins for motors, sensors, and other hardware.

## Table of Contents

1. [Pin Numbering Modes](#pin-numbering-modes)
2. [Motor Driver Configuration](#motor-driver-configuration)
3. [Sensor Configuration](#sensor-configuration)
4. [Display Configuration](#display-configuration)
5. [Changing Configuration](#changing-configuration)

## Pin Numbering Modes

### BOARD vs BCM

Raspberry Pi supports two GPIO numbering modes:

**BOARD Mode (Physical Pin Numbers):**
- Uses physical pin numbers (1-40)
- Independent of Pi model
- **Recommended for beginners**
- Example: Pin 33 is always the same physical location

**BCM Mode (Broadcom SOC Channel):**
- Uses GPIO channel numbers
- Changes between Pi models
- More flexible for advanced use
- Example: GPIO 13 may be different physical pins

### Pin Layout Reference

```
Raspberry Pi GPIO Layout (BOARD Mode)

    3V3  [1] [2]  5V
  GPIO2  [3] [4]  5V
  GPIO3  [5] [6]  GND
  GPIO4  [7] [8]  GPIO14
    GND  [9] [10] GPIO15
 GPIO17 [11] [12] GPIO18
 GPIO27 [13] [14] GND
 GPIO22 [15] [16] GPIO23
    3V3 [17] [18] GPIO24
 GPIO10 [19] [20] GND
  GPIO9 [21] [22] GPIO25
 GPIO11 [23] [24] GPIO8
    GND [25] [26] GPIO7
  GPIO0 [27] [28] GPIO1
  GPIO5 [29] [30] GND
  GPIO6 [31] [32] GPIO12
 GPIO13 [33] [34] GND
 GPIO19 [35] [36] GPIO16
 GPIO26 [37] [38] GPIO20
    GND [39] [40] GPIO21
```

## Motor Driver Configuration

### L298N Motor Driver

**Wiring:**
```
L298N Pin    -> Raspberry Pi Pin (BOARD)
============================================
IN1 (Left+)  -> GPIO 33 (configurable)
IN2 (Left-)  -> GPIO 38
IN3 (Right+) -> GPIO 35
IN4 (Right-) -> GPIO 40
ENA (Left)   -> 5V (or PWM pin)
ENB (Right)  -> 5V (or PWM pin)
GND          -> GND (Pin 6, 9, 14, etc.)
+12V         -> External battery (NOT Pi)
+5V          -> 5V (Pin 2 or 4) - Optional for logic

Motors:
Motor A      -> Left motor
Motor B      -> Right motor
```

**Default Configuration:**
```yaml
motors:
  pin_mode: "BOARD"
  pins:
    L1: 33  # Left motor forward
    L2: 38  # Left motor backward
    R1: 35  # Right motor forward
    R2: 40  # Right motor backward
  pwm_frequency: 100  # Hz
  default_speed: 70   # 0-100%
  turn_speed: 50
```

### TB6612 Motor Driver

**Wiring:**
```
TB6612 Pin   -> Raspberry Pi Pin (BOARD)
============================================
AIN1         -> GPIO 33
AIN2         -> GPIO 38
PWMA         -> GPIO 12 (hardware PWM)
BIN1         -> GPIO 35
BIN2         -> GPIO 40
PWMB         -> GPIO 32 (hardware PWM)
STBY         -> 3.3V (always enabled)
GND          -> GND
VM           -> External battery (2.7-13.5V)
VCC          -> 3.3V or 5V
```

**TB6612 Configuration:**
```yaml
motors:
  pin_mode: "BOARD"
  driver_type: "TB6612"
  pins:
    L1: 33
    L2: 38
    L_PWM: 12  # Hardware PWM
    R1: 35
    R2: 40
    R_PWM: 32  # Hardware PWM
  pwm_frequency: 100
```

### Testing Motors

```python
# Test script
from hardware.motor_controller import MotorController
import time

config = {
    "pin_mode": "BOARD",
    "pins": {
        "L1": 33,
        "L2": 38,
        "R1": 35,
        "R2": 40
    }
}

motor = MotorController(config)

# Test forward
print("Moving forward...")
motor.move_forward(50)
time.sleep(2)

# Test backward
print("Moving backward...")
motor.move_backward(50)
time.sleep(2)

# Test turning
print("Turning left...")
motor.turn_left(50)
time.sleep(1)

motor.stop()
motor.cleanup()
```

## Sensor Configuration

### HC-SR04 Ultrasonic Sensor

**Wiring:**
```
HC-SR04 Pin  -> Raspberry Pi Pin
================================
VCC          -> 5V (Pin 2 or 4)
Trig         -> GPIO 11 (Board Pin 23)
Echo         -> GPIO 13 (Board Pin 33) via voltage divider!
GND          -> GND

IMPORTANT: Echo pin needs voltage divider (5V -> 3.3V)
Use 1kΩ and 2kΩ resistors
```

**Configuration:**
```yaml
ultrasonic:
  enabled: true
  trigger_pin: 11  # BOARD numbering
  echo_pin: 13
  max_distance: 400  # cm
  obstacle_threshold: 30  # cm
```

### MPU6050 IMU

**Wiring (I2C):**
```
MPU6050 Pin  -> Raspberry Pi Pin
================================
VCC          -> 3.3V (Pin 1)
GND          -> GND (Pin 6)
SCL          -> SCL (Pin 5, GPIO 3)
SDA          -> SDA (Pin 3, GPIO 2)
AD0          -> GND (for address 0x68)
```

**Configuration:**
```yaml
imu:
  enabled: true
  i2c_address: 0x68
  sample_rate: 100  # Hz
```

**Test I2C Device:**
```bash
sudo i2cdetect -y 1
# Should show device at 0x68
```

### Multiple Ultrasonic Sensors

```yaml
ultrasonic_sensors:
  front:
    trigger_pin: 11
    echo_pin: 13
  left:
    trigger_pin: 15
    echo_pin: 16
  right:
    trigger_pin: 18
    echo_pin: 22
```

## Display Configuration

### SSD1306 OLED Display (128x64)

**Wiring (I2C):**
```
OLED Pin     -> Raspberry Pi Pin
================================
VCC          -> 3.3V (Pin 1)
GND          -> GND (Pin 6)
SCL          -> SCL (Pin 5)
SDA          -> SDA (Pin 3)
```

**Configuration:**
```yaml
display:
  enabled: true
  type: "oled"
  interface: "i2c"
  i2c_address: 0x3C
  width: 128
  height: 64
```

**Test Display:**
```bash
sudo i2cdetect -y 1
# Should show device at 0x3C
```

## Changing Configuration

### Method 1: Edit Configuration File (Pi)

```bash
cd ~/qt-robot-controller/pi_server
nano config/hardware_config.yaml
```

Modify settings, save, and restart server:
```bash
python3 server.py
```

### Method 2: PC Application GUI

1. **Open PC Application**
2. **Connect to Robot**
3. **Go to Settings → Hardware Configuration**
4. **Modify Pin Numbers:**
   - Click on pin fields
   - Enter new pin numbers
5. **Click "Apply"**
6. **Changes sync to Pi automatically**

### Method 3: Runtime Configuration

```python
# Send GPIO config from PC app
import json

new_config = {
    "motors": {
        "pin_mode": "BOARD",
        "pins": {
            "L1": 29,
            "L2": 31,
            "R1": 32,
            "R2": 33
        }
    }
}

# Send to robot
client.send_config(new_config)
```

## Pin Assignment Best Practices

### Reserved Pins (Do Not Use)

- **Pin 1, 17**: 3.3V power
- **Pin 2, 4**: 5V power
- **Pin 6, 9, 14, 20, 25, 30, 34, 39**: Ground
- **Pin 27, 28**: I2C ID EEPROM (reserved)

### Hardware PWM Pins (Recommended for Motors)

- **GPIO 12** (Pin 32): PWM0
- **GPIO 13** (Pin 33): PWM1
- **GPIO 18** (Pin 12): PWM0
- **GPIO 19** (Pin 35): PWM1

### I2C Pins (For Sensors/Displays)

- **GPIO 2** (Pin 3): SDA
- **GPIO 3** (Pin 5): SCL

### Common Pin Assignments

**Typical Robot Configuration:**
```yaml
# Motors
L1: 33  # Left forward
L2: 38  # Left backward
R1: 35  # Right forward
R2: 40  # Right backward

# Ultrasonic
Trigger: 11
Echo: 13

# I2C (auto-assigned)
SDA: 3   # For IMU, OLED
SCL: 5

# Camera: CSI port or USB
# LiDAR: USB
```

## Troubleshooting

### Motors Don't Move

1. **Check Wiring:**
   ```bash
   # Test GPIO output
   gpio -g mode 13 out  # BCM numbering
   gpio -g write 13 1
   gpio -g write 13 0
   ```

2. **Check Power:**
   - Motor driver needs external power
   - Don't power motors from Pi

3. **Check Pin Configuration:**
   - Verify BOARD vs BCM mode
   - Confirm pin numbers

### Sensor Not Detected

```bash
# Check I2C devices
sudo i2cdetect -y 1

# Check GPIO permissions
groups | grep gpio

# Test GPIO read
gpio -g mode 17 in
gpio -g read 17
```

### Permission Errors

```bash
# Add to gpio group
sudo usermod -a -G gpio $USER
sudo usermod -a -G i2c $USER

# Logout and login again
logout
```

## References

- [Raspberry Pi GPIO Pinout](https://pinout.xyz/)
- [L298N Datasheet](https://www.sparkfun.com/datasheets/Robotics/L298_H_Bridge.pdf)
- [TB6612 Datasheet](https://www.sparkfun.com/datasheets/Robotics/TB6612FNG.pdf)
- [HC-SR04 Datasheet](https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf)
