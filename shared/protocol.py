"""Communication protocol definitions for Qt Robot Controller."""

from enum import Enum
from typing import Any, Dict, Optional
import json
from dataclasses import dataclass, asdict


class MessageType(Enum):
    """Message types for communication."""
    # Control Commands
    COMMAND = "command"
    RESPONSE = "response"
    
    # Motor Control
    MOVE_FORWARD = "move_forward"
    MOVE_BACKWARD = "move_backward"
    TURN_LEFT = "turn_left"
    TURN_RIGHT = "turn_right"
    STOP = "stop"
    
    # Sensor Data
    SENSOR_DATA = "sensor_data"
    CAMERA_FRAME = "camera_frame"
    LIDAR_SCAN = "lidar_scan"
    
    # Configuration
    CONFIG_UPDATE = "config_update"
    GPIO_CONFIG = "gpio_config"
    
    # Status
    STATUS_UPDATE = "status_update"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class Status(Enum):
    """Response status codes."""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"


@dataclass
class Message:
    """Base message structure."""
    type: str
    timestamp: float
    data: Dict[str, Any]
    
    def to_json(self) -> str:
        """Convert message to JSON string."""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Message':
        """Create message from JSON string."""
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class CommandMessage(Message):
    """Command message from PC to Pi."""
    action: str
    params: Optional[Dict[str, Any]] = None


@dataclass
class ResponseMessage(Message):
    """Response message from Pi to PC."""
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# GPIO Pin Defaults (BOARD Mode)
DEFAULT_GPIO_CONFIG = {
    "pin_mode": "BOARD",
    "motors": {
        "L1": 33,  # Left motor forward
        "L2": 38,  # Left motor backward
        "R1": 35,  # Right motor forward
        "R2": 40,  # Right motor backward
    },
    "sensors": {
        "ultrasonic_trigger": 11,
        "ultrasonic_echo": 13,
    },
    "pwm_frequency": 100,
}


# Network Defaults
DEFAULT_PORT = 8888
HEARTBEAT_INTERVAL = 5  # seconds
CONNECTION_TIMEOUT = 10  # seconds
