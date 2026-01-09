"""Shared constants for Qt Robot Controller.

Version information, limits, and configuration constants
used across PC application and Raspberry Pi server.
"""

# Version information
VERSION = "1.0.0"
APP_NAME = "Qt Robot Controller"
ORGANIZATION = "ZeroAI Tech"

# Network constants
DEFAULT_PORT = 8888
MAX_CONNECTIONS = 5
BUFFER_SIZE = 8192
HEARTBEAT_INTERVAL = 5  # seconds
CONNECTION_TIMEOUT = 30  # seconds
RECONNECT_ATTEMPTS = 3
RECONNECT_DELAY = 5  # seconds

# Motor constants
MOTOR_MIN_SPEED = 0
MOTOR_MAX_SPEED = 100
MOTOR_DEFAULT_SPEED = 70
MOTOR_TURN_SPEED = 50
MOTOR_PWM_FREQUENCY = 100  # Hz

# Camera constants
CAMERA_DEFAULT_WIDTH = 640
CAMERA_DEFAULT_HEIGHT = 480
CAMERA_DEFAULT_FPS = 30
CAMERA_JPEG_QUALITY = 80
CAMERA_STREAM_PORT = 8889

# Sensor constants
ULTRASONIC_MAX_DISTANCE = 400  # cm
ULTRASONIC_MIN_DISTANCE = 2    # cm
OBSTACLE_THRESHOLD = 30        # cm (stop distance)
SENSOR_UPDATE_RATE = 10        # Hz

# LiDAR constants
LIDAR_BAUDRATE = 115200
LIDAR_TIMEOUT = 1  # seconds
LIDAR_SCAN_RATE = 10  # Hz
LIDAR_MAX_DISTANCE = 12000  # mm

# Display constants
DISPLAY_WIDTH = 128
DISPLAY_HEIGHT = 64
DISPLAY_FPS = 30
FACE_ANIMATION_SPEED = 0.1  # seconds per frame

# Safety constants
AUTO_STOP_TIMEOUT = 10  # seconds (motors auto-stop if no command)
WATCHDOG_TIMEOUT = 15   # seconds
MAX_COMMAND_QUEUE = 100
EMERGENCY_STOP_DISTANCE = 10  # cm

# AI/Voice constants
VOICE_RECOGNITION_TIMEOUT = 5  # seconds
VOICE_RECOGNITION_PHRASE_TIME_LIMIT = 10  # seconds
TTS_RATE = 150  # words per minute
TTS_VOLUME = 0.9  # 0.0 to 1.0
AI_RESPONSE_TIMEOUT = 10  # seconds
AI_MAX_TOKENS = 500

# File paths
CONFIG_DIR = "config"
LOGS_DIR = "logs"
DATA_DIR = "data"
RESOURCES_DIR = "resources"

# Logging constants
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_FILE_BACKUP_COUNT = 5

# GPIO pin modes
GPIO_MODE_BOARD = "BOARD"
GPIO_MODE_BCM = "BCM"

# Face expressions
FACE_EXPRESSIONS = [
    "neutral",
    "happy",
    "sad",
    "angry",
    "surprised",
    "thinking",
    "sleeping",
    "confused"
]

# Battery monitoring
BATTERY_MIN_VOLTAGE = 9.0   # V
BATTERY_MAX_VOLTAGE = 12.6  # V
BATTERY_WARNING_LEVEL = 20  # %
BATTERY_CRITICAL_LEVEL = 10 # %

# Error codes
ERROR_CODES = {
    "E001": "Connection failed",
    "E002": "Motor controller error",
    "E003": "Camera not available",
    "E004": "LiDAR not responding",
    "E005": "Sensor read failure",
    "E006": "Invalid command",
    "E007": "Configuration error",
    "E008": "Battery critical",
    "E009": "Emergency stop triggered",
    "E010": "Communication timeout"
}

# Status messages
STATUS_MESSAGES = {
    "IDLE": "Robot is idle",
    "MOVING": "Robot is moving",
    "TURNING": "Robot is turning",
    "STOPPED": "Robot is stopped",
    "SCANNING": "LiDAR scanning active",
    "STREAMING": "Camera streaming active",
    "ERROR": "Error state",
    "EMERGENCY": "Emergency stop active"
}

# Performance monitoring
MAX_CPU_TEMP = 80  # °C
MAX_CPU_USAGE = 90  # %
MAX_MEMORY_USAGE = 90  # %

# Data collection
DATA_BUFFER_SIZE = 1000
DATA_SAVE_INTERVAL = 60  # seconds

# UI constants (for PC app)
UI_UPDATE_RATE = 30  # Hz
UI_THEME_DARK = "dark"
UI_THEME_LIGHT = "light"
UI_DEFAULT_THEME = UI_THEME_DARK

# Map/SLAM constants
MAP_RESOLUTION = 0.05  # meters per pixel
MAP_SIZE = 1000  # pixels
MAP_UPDATE_RATE = 5  # Hz

# Default configurations
DEFAULT_MOTOR_CONFIG = {
    "pin_mode": GPIO_MODE_BOARD,
    "pins": {
        "L1": 33,
        "L2": 38,
        "R1": 35,
        "R2": 40
    },
    "pwm_frequency": MOTOR_PWM_FREQUENCY,
    "default_speed": MOTOR_DEFAULT_SPEED,
    "turn_speed": MOTOR_TURN_SPEED
}

DEFAULT_CAMERA_CONFIG = {
    "enabled": True,
    "type": "opencv",
    "device_id": 0,
    "width": CAMERA_DEFAULT_WIDTH,
    "height": CAMERA_DEFAULT_HEIGHT,
    "fps": CAMERA_DEFAULT_FPS,
    "stream_quality": CAMERA_JPEG_QUALITY
}

DEFAULT_SENSOR_CONFIG = {
    "ultrasonic": {
        "enabled": True,
        "trigger_pin": 11,
        "echo_pin": 13,
        "max_distance": ULTRASONIC_MAX_DISTANCE,
        "obstacle_threshold": OBSTACLE_THRESHOLD
    }
}

DEFAULT_SAFETY_CONFIG = {
    "auto_stop_timeout": AUTO_STOP_TIMEOUT,
    "obstacle_detection": True,
    "watchdog_enabled": True,
    "emergency_stop_distance": EMERGENCY_STOP_DISTANCE
}
