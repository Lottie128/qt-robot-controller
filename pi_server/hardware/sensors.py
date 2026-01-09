"""Sensor modules for ultrasonic, IMU, and other sensors.

Supports:
- HC-SR04 ultrasonic distance sensor
- MPU6050 IMU (accelerometer + gyroscope)
- Battery voltage monitoring
- Temperature sensors
"""

import time
import threading
from typing import Dict, Optional, Tuple

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - using mock sensors")

try:
    import smbus2
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False
    print("⚠️  smbus2 not available - I2C sensors disabled")


class UltrasonicSensor:
    """HC-SR04 ultrasonic distance sensor."""
    
    def __init__(self, trigger_pin: int, echo_pin: int, max_distance: int = 400):
        """Initialize ultrasonic sensor.
        
        Args:
            trigger_pin: GPIO pin for trigger
            echo_pin: GPIO pin for echo
            max_distance: Maximum distance in cm
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        self.max_distance = max_distance
        
        if GPIO_AVAILABLE:
            GPIO.setup(trigger_pin, GPIO.OUT)
            GPIO.setup(echo_pin, GPIO.IN)
            GPIO.output(trigger_pin, GPIO.LOW)
            time.sleep(0.1)
            print(f"✅ Ultrasonic sensor initialized (Trigger: {trigger_pin}, Echo: {echo_pin})")
        else:
            print("⚠️  Ultrasonic sensor in mock mode")
    
    def get_distance(self) -> Optional[float]:
        """Measure distance in centimeters.
        
        Returns:
            Distance in cm or None if measurement failed
        """
        if not GPIO_AVAILABLE:
            return 100.0  # Mock distance
        
        try:
            # Send trigger pulse
            GPIO.output(self.trigger_pin, GPIO.HIGH)
            time.sleep(0.00001)  # 10 microseconds
            GPIO.output(self.trigger_pin, GPIO.LOW)
            
            # Wait for echo
            timeout = time.time() + 0.1  # 100ms timeout
            
            # Wait for echo start
            while GPIO.input(self.echo_pin) == GPIO.LOW:
                pulse_start = time.time()
                if pulse_start > timeout:
                    return None
            
            # Wait for echo end
            while GPIO.input(self.echo_pin) == GPIO.HIGH:
                pulse_end = time.time()
                if pulse_end > timeout:
                    return None
            
            # Calculate distance
            pulse_duration = pulse_end - pulse_start
            distance = pulse_duration * 17150  # Speed of sound / 2
            distance = round(distance, 2)
            
            if distance > self.max_distance:
                return self.max_distance
            
            return distance
        except Exception as e:
            print(f"❌ Ultrasonic measurement error: {e}")
            return None
    
    def is_obstacle_detected(self, threshold: float = 30.0) -> bool:
        """Check if obstacle is within threshold distance.
        
        Args:
            threshold: Distance threshold in cm
            
        Returns:
            True if obstacle detected
        """
        distance = self.get_distance()
        return distance is not None and distance < threshold


class IMUSensor:
    """MPU6050 IMU sensor (accelerometer + gyroscope)."""
    
    MPU6050_ADDR = 0x68
    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    GYRO_XOUT_H = 0x43
    
    def __init__(self, bus_number: int = 1):
        """Initialize IMU sensor.
        
        Args:
            bus_number: I2C bus number
        """
        self.bus = None
        
        if SMBUS_AVAILABLE:
            try:
                self.bus = smbus2.SMBus(bus_number)
                # Wake up MPU6050
                self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)
                time.sleep(0.1)
                print("✅ IMU sensor initialized")
            except Exception as e:
                print(f"⚠️  IMU init failed: {e}")
                self.bus = None
        else:
            print("⚠️  IMU sensor disabled (smbus2 not available)")
    
    def _read_word(self, reg: int) -> int:
        """Read 16-bit word from register."""
        high = self.bus.read_byte_data(self.MPU6050_ADDR, reg)
        low = self.bus.read_byte_data(self.MPU6050_ADDR, reg + 1)
        value = (high << 8) + low
        
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value
    
    def get_acceleration(self) -> Optional[Tuple[float, float, float]]:
        """Get acceleration data.
        
        Returns:
            (x, y, z) acceleration in g or None
        """
        if not self.bus:
            return (0.0, 0.0, 1.0)  # Mock data
        
        try:
            ax = self._read_word(self.ACCEL_XOUT_H) / 16384.0
            ay = self._read_word(self.ACCEL_XOUT_H + 2) / 16384.0
            az = self._read_word(self.ACCEL_XOUT_H + 4) / 16384.0
            return (ax, ay, az)
        except Exception as e:
            print(f"❌ IMU read error: {e}")
            return None
    
    def get_gyro(self) -> Optional[Tuple[float, float, float]]:
        """Get gyroscope data.
        
        Returns:
            (x, y, z) angular velocity in deg/s or None
        """
        if not self.bus:
            return (0.0, 0.0, 0.0)  # Mock data
        
        try:
            gx = self._read_word(self.GYRO_XOUT_H) / 131.0
            gy = self._read_word(self.GYRO_XOUT_H + 2) / 131.0
            gz = self._read_word(self.GYRO_XOUT_H + 4) / 131.0
            return (gx, gy, gz)
        except Exception as e:
            print(f"❌ Gyro read error: {e}")
            return None


class SensorManager:
    """Manage all sensors with continuous monitoring."""
    
    def __init__(self, config: dict):
        """Initialize sensor manager.
        
        Args:
            config: Sensor configuration dictionary
        """
        self.config = config
        self.sensors = {}
        self.sensor_data = {}
        self.data_lock = threading.Lock()
        self.monitoring = False
        self.monitor_thread = None
        
        self._init_sensors()
    
    def _init_sensors(self):
        """Initialize all configured sensors."""
        # Ultrasonic sensor
        ultrasonic_config = self.config.get("ultrasonic", {})
        if ultrasonic_config.get("enabled", False):
            trigger = ultrasonic_config.get("trigger_pin", 11)
            echo = ultrasonic_config.get("echo_pin", 13)
            max_dist = ultrasonic_config.get("max_distance", 400)
            self.sensors["ultrasonic"] = UltrasonicSensor(trigger, echo, max_dist)
        
        # IMU sensor
        imu_config = self.config.get("imu", {})
        if imu_config.get("enabled", False):
            self.sensors["imu"] = IMUSensor()
    
    def start_monitoring(self):
        """Start continuous sensor monitoring."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("📊 Sensor monitoring started")
    
    def stop_monitoring(self):
        """Stop sensor monitoring."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print("⏹️  Sensor monitoring stopped")
    
    def _monitor_loop(self):
        """Continuous sensor reading loop."""
        while self.monitoring:
            try:
                data = {}
                
                # Read ultrasonic
                if "ultrasonic" in self.sensors:
                    distance = self.sensors["ultrasonic"].get_distance()
                    if distance is not None:
                        data["distance"] = distance
                
                # Read IMU
                if "imu" in self.sensors:
                    accel = self.sensors["imu"].get_acceleration()
                    gyro = self.sensors["imu"].get_gyro()
                    if accel:
                        data["acceleration"] = {"x": accel[0], "y": accel[1], "z": accel[2]}
                    if gyro:
                        data["gyro"] = {"x": gyro[0], "y": gyro[1], "z": gyro[2]}
                
                # Update sensor data
                with self.data_lock:
                    self.sensor_data = data
                
                time.sleep(0.1)  # 10 Hz update rate
            except Exception as e:
                print(f"❌ Sensor monitoring error: {e}")
                time.sleep(0.5)
    
    def get_sensor_data(self) -> Dict:
        """Get latest sensor readings.
        
        Returns:
            Dictionary of sensor data
        """
        with self.data_lock:
            return self.sensor_data.copy()
    
    def cleanup(self):
        """Cleanup sensor resources."""
        self.stop_monitoring()
        print("✅ Sensors cleaned up")
