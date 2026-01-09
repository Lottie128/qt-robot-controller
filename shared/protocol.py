"""Communication protocol definitions for Qt Robot Controller.

Defines message types, status codes, and communication protocol
between PC application and Raspberry Pi server.
"""

from enum import Enum
from typing import Dict, Any
import json


# Default network settings
DEFAULT_PORT = 8888
DEFAULT_HOST = "0.0.0.0"
CONNECTION_TIMEOUT = 10  # seconds
RECONNECT_DELAY = 5  # seconds


class MessageType(Enum):
    """Message types for communication protocol."""
    
    # Connection messages
    CONNECT = "connect"
    DISCONNECT = "disconnect"
    PING = "ping"
    PONG = "pong"
    
    # Movement commands
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    SET_SPEED = "set_speed"
    
    # Camera commands
    START_CAMERA = "start_camera"
    STOP_CAMERA = "stop_camera"
    CAMERA_FRAME = "camera_frame"
    ADJUST_CAMERA = "adjust_camera"
    
    # Sensor data
    SENSOR_DATA = "sensor_data"
    ULTRASONIC_DATA = "ultrasonic_data"
    IMU_DATA = "imu_data"
    BATTERY_STATUS = "battery_status"
    
    # LiDAR commands
    START_LIDAR = "start_lidar"
    STOP_LIDAR = "stop_lidar"
    LIDAR_SCAN = "lidar_scan"
    
    # Configuration
    GPIO_CONFIG = "gpio_config"
    UPDATE_CONFIG = "update_config"
    GET_CONFIG = "get_config"
    
    # AI/Voice commands
    VOICE_COMMAND = "voice_command"
    AI_RESPONSE = "ai_response"
    TTS_SPEAK = "tts_speak"
    
    # Face display
    FACE_EXPRESSION = "face_expression"
    FACE_ANIMATION = "face_animation"
    
    # System
    RESPONSE = "response"
    ERROR = "error"
    STATUS = "status"
    LOG = "log"


class Status(Enum):
    """Status codes for responses."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    TIMEOUT = "timeout"
    INVALID = "invalid"


class Priority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3


class Protocol:
    """Protocol handler for message serialization/deserialization."""
    
    @staticmethod
    def create_message(
        msg_type: MessageType,
        data: Dict[str, Any] = None,
        priority: Priority = Priority.NORMAL
    ) -> str:
        """Create a protocol message.
        
        Args:
            msg_type: Type of message
            data: Message data payload
            priority: Message priority level
            
        Returns:
            JSON string of the message
        """
        message = {
            "type": msg_type.value,
            "priority": priority.value,
            "data": data or {}
        }
        return json.dumps(message)
    
    @staticmethod
    def parse_message(message_str: str) -> Dict[str, Any]:
        """Parse a protocol message.
        
        Args:
            message_str: JSON message string
            
        Returns:
            Parsed message dictionary
            
        Raises:
            ValueError: If message is invalid
        """
        try:
            message = json.loads(message_str)
            
            if "type" not in message:
                raise ValueError("Message missing 'type' field")
            
            return message
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")
    
    @staticmethod
    def create_response(
        status: Status,
        data: Dict[str, Any] = None,
        error: str = None
    ) -> str:
        """Create a response message.
        
        Args:
            status: Response status
            data: Response data
            error: Error message if status is ERROR
            
        Returns:
            JSON string of the response
        """
        response = {
            "type": MessageType.RESPONSE.value,
            "status": status.value,
            "data": data or {}
        }
        
        if error:
            response["error"] = error
        
        return json.dumps(response)
    
    @staticmethod
    def create_error(error_msg: str, error_code: str = None) -> str:
        """Create an error message.
        
        Args:
            error_msg: Error message
            error_code: Optional error code
            
        Returns:
            JSON string of the error
        """
        error = {
            "type": MessageType.ERROR.value,
            "status": Status.ERROR.value,
            "error": error_msg
        }
        
        if error_code:
            error["code"] = error_code
        
        return json.dumps(error)
    
    @staticmethod
    def validate_message(message: Dict[str, Any]) -> bool:
        """Validate message structure.
        
        Args:
            message: Message dictionary
            
        Returns:
            True if valid, False otherwise
        """
        required_fields = ["type"]
        return all(field in message for field in required_fields)


# Command parameter schemas
COMMAND_SCHEMAS = {
    MessageType.MOVE_FORWARD: {
        "speed": {"type": int, "min": 0, "max": 100, "default": 70},
        "duration": {"type": float, "min": 0, "optional": True}
    },
    MessageType.MOVE_BACKWARD: {
        "speed": {"type": int, "min": 0, "max": 100, "default": 70},
        "duration": {"type": float, "min": 0, "optional": True}
    },
    MessageType.TURN_LEFT: {
        "speed": {"type": int, "min": 0, "max": 100, "default": 50},
        "duration": {"type": float, "min": 0, "optional": True}
    },
    MessageType.TURN_RIGHT: {
        "speed": {"type": int, "min": 0, "max": 100, "default": 50},
        "duration": {"type": float, "min": 0, "optional": True}
    },
    MessageType.SET_SPEED: {
        "speed": {"type": int, "min": 0, "max": 100, "required": True}
    }
}


def validate_command_params(msg_type: MessageType, params: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize command parameters.
    
    Args:
        msg_type: Message type
        params: Command parameters
        
    Returns:
        Validated and normalized parameters
        
    Raises:
        ValueError: If parameters are invalid
    """
    if msg_type not in COMMAND_SCHEMAS:
        return params
    
    schema = COMMAND_SCHEMAS[msg_type]
    validated = {}
    
    for param_name, param_schema in schema.items():
        if param_name in params:
            value = params[param_name]
            
            # Type check
            expected_type = param_schema["type"]
            if not isinstance(value, expected_type):
                raise ValueError(f"{param_name} must be {expected_type.__name__}")
            
            # Range check
            if "min" in param_schema and value < param_schema["min"]:
                raise ValueError(f"{param_name} must be >= {param_schema['min']}")
            if "max" in param_schema and value > param_schema["max"]:
                raise ValueError(f"{param_name} must be <= {param_schema['max']}")
            
            validated[param_name] = value
        elif param_schema.get("required", False):
            raise ValueError(f"{param_name} is required")
        elif "default" in param_schema:
            validated[param_name] = param_schema["default"]
    
    return validated
