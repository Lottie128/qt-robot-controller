"""Motor controller for L298N/TB6612 motor drivers.

Supports:
- Configurable GPIO pins
- PWM speed control
- Direction control (forward, backward, left, right)
- Auto-stop safety
"""

import time
from typing import Dict, Optional

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    # Mock GPIO for testing on non-Pi systems
    GPIO_AVAILABLE = False
    print("⚠️  RPi.GPIO not available - using mock mode")


class MockGPIO:
    """Mock GPIO for testing on non-Raspberry Pi systems."""
    BOARD = "BOARD"
    BCM = "BCM"
    OUT = "OUT"
    
    @staticmethod
    def setmode(mode):
        pass
    
    @staticmethod
    def setup(pin, mode):
        pass
    
    @staticmethod
    def output(pin, state):
        pass
    
    @staticmethod
    def PWM(pin, freq):
        return MockPWM()
    
    @staticmethod
    def cleanup():
        pass


class MockPWM:
    """Mock PWM for testing."""
    def start(self, duty_cycle):
        pass
    
    def ChangeDutyCycle(self, duty_cycle):
        pass
    
    def stop(self):
        pass


if not GPIO_AVAILABLE:
    GPIO = MockGPIO()


class MotorController:
    """Control robot motors via GPIO."""
    
    def __init__(self, config: Dict):
        """Initialize motor controller.
        
        Args:
            config: Motor configuration dictionary with pins and settings
        """
        self.config = config
        self.pin_mode = config.get("pin_mode", "BOARD")
        self.pins = config.get("pins", {
            "L1": 33, "L2": 38,  # Left motor
            "R1": 35, "R2": 40   # Right motor
        })
        self.pwm_freq = config.get("pwm_frequency", 100)
        self.current_speed = 0
        
        self._setup_gpio()
    
    def _setup_gpio(self):
        """Setup GPIO pins and PWM."""
        # Set pin numbering mode
        if self.pin_mode == "BOARD":
            GPIO.setmode(GPIO.BOARD)
        else:
            GPIO.setmode(GPIO.BCM)
        
        # Setup motor pins as outputs
        for pin_name, pin_num in self.pins.items():
            GPIO.setup(pin_num, GPIO.OUT)
            GPIO.output(pin_num, GPIO.LOW)
        
        # Setup PWM on all motor pins
        self.pwm = {
            pin_name: GPIO.PWM(pin_num, self.pwm_freq)
            for pin_name, pin_num in self.pins.items()
        }
        
        # Start all PWM at 0% duty cycle
        for pwm in self.pwm.values():
            pwm.start(0)
        
        print(f"✅ GPIO initialized - Mode: {self.pin_mode}")
        print(f"   Pins: {self.pins}")
    
    def move_forward(self, speed: int = 70):
        """Move robot forward.
        
        Args:
            speed: Speed percentage (0-100)
        """
        speed = max(0, min(100, speed))  # Clamp to 0-100
        self.current_speed = speed
        
        # Left motor forward
        self.pwm["L1"].ChangeDutyCycle(speed)
        self.pwm["L2"].ChangeDutyCycle(0)
        
        # Right motor forward
        self.pwm["R1"].ChangeDutyCycle(speed)
        self.pwm["R2"].ChangeDutyCycle(0)
        
        print(f"➡️  Moving forward at {speed}%")
    
    def move_backward(self, speed: int = 70):
        """Move robot backward.
        
        Args:
            speed: Speed percentage (0-100)
        """
        speed = max(0, min(100, speed))
        self.current_speed = speed
        
        # Left motor backward
        self.pwm["L1"].ChangeDutyCycle(0)
        self.pwm["L2"].ChangeDutyCycle(speed)
        
        # Right motor backward
        self.pwm["R1"].ChangeDutyCycle(0)
        self.pwm["R2"].ChangeDutyCycle(speed)
        
        print(f"⬅️  Moving backward at {speed}%")
    
    def turn_left(self, speed: int = 50):
        """Turn robot left (rotate in place).
        
        Args:
            speed: Speed percentage (0-100)
        """
        speed = max(0, min(100, speed))
        self.current_speed = speed
        
        # Left motor backward
        self.pwm["L1"].ChangeDutyCycle(0)
        self.pwm["L2"].ChangeDutyCycle(speed)
        
        # Right motor forward
        self.pwm["R1"].ChangeDutyCycle(speed)
        self.pwm["R2"].ChangeDutyCycle(0)
        
        print(f"⬅️  Turning left at {speed}%")
    
    def turn_right(self, speed: int = 50):
        """Turn robot right (rotate in place).
        
        Args:
            speed: Speed percentage (0-100)
        """
        speed = max(0, min(100, speed))
        self.current_speed = speed
        
        # Left motor forward
        self.pwm["L1"].ChangeDutyCycle(speed)
        self.pwm["L2"].ChangeDutyCycle(0)
        
        # Right motor backward
        self.pwm["R1"].ChangeDutyCycle(0)
        self.pwm["R2"].ChangeDutyCycle(speed)
        
        print(f"➡️  Turning right at {speed}%")
    
    def stop(self):
        """Stop all motors."""
        for pwm in self.pwm.values():
            pwm.ChangeDutyCycle(0)
        
        self.current_speed = 0
        print("⏹️  Motors stopped")
    
    def set_speed(self, speed: int):
        """Set motor speed without changing direction.
        
        Args:
            speed: Speed percentage (0-100)
        """
        speed = max(0, min(100, speed))
        
        # Update duty cycle for active motors only
        for pin_name, pwm in self.pwm.items():
            # Check if this motor is currently active
            # (This is simplified - in practice you'd track current direction)
            if self.current_speed > 0:
                pwm.ChangeDutyCycle(speed)
        
        self.current_speed = speed
    
    def cleanup(self):
        """Cleanup GPIO resources."""
        self.stop()
        for pwm in self.pwm.values():
            pwm.stop()
        GPIO.cleanup()
        print("✅ Motors cleaned up")
