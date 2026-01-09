"""Network client for communicating with robot.

WebSocket client that sends commands and receives data from Pi server.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets not available")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.protocol import MessageType, Protocol, Status


class RobotClient:
    """WebSocket client for robot communication."""
    
    def __init__(self):
        """Initialize robot client."""
        self.logger = logging.getLogger(__name__)
        self.websocket = None
        self.connected = False
        self.host = ""
        self.port = 0
        
        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_message: Optional[Callable[[Dict], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Receive task
        self.receive_task = None
    
    async def connect(self, host: str, port: int) -> bool:
        """Connect to robot server.
        
        Args:
            host: Robot IP address
            port: Server port
            
        Returns:
            True if connection successful
        """
        if not WEBSOCKETS_AVAILABLE:
            self.logger.error("websockets library not available")
            if self.on_error:
                self.on_error("websockets library not installed")
            return False
        
        try:
            self.host = host
            self.port = port
            
            uri = f"ws://{host}:{port}"
            self.logger.info(f"Connecting to {uri}...")
            
            self.websocket = await websockets.connect(uri)
            self.connected = True
            
            # Start receive loop
            self.receive_task = asyncio.create_task(self._receive_loop())
            
            self.logger.info("✅ Connected to robot")
            if self.on_connected:
                self.on_connected()
            
            return True
        
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            if self.on_error:
                self.on_error(f"Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from robot."""
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
        
        self.connected = False
        self.websocket = None
        
        if self.receive_task:
            self.receive_task.cancel()
        
        self.logger.info("Disconnected from robot")
        if self.on_disconnected:
            self.on_disconnected()
    
    async def _receive_loop(self):
        """Receive messages from robot."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    
                    if self.on_message:
                        self.on_message(data)
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Connection closed by robot")
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected()
        
        except Exception as e:
            self.logger.error(f"Receive error: {e}")
            if self.on_error:
                self.on_error(str(e))
    
    async def _send_message(self, msg_type: MessageType, data: Dict[str, Any] = None):
        """Send message to robot.
        
        Args:
            msg_type: Message type
            data: Message data
        """
        if not self.connected or not self.websocket:
            self.logger.warning("Not connected to robot")
            return
        
        try:
            message = Protocol.create_message(msg_type, data)
            await self.websocket.send(message)
        
        except Exception as e:
            self.logger.error(f"Send error: {e}")
            if self.on_error:
                self.on_error(str(e))
    
    # Movement commands
    async def move_forward(self, speed: int = 70, duration: float = None):
        """Move robot forward.
        
        Args:
            speed: Speed percentage (0-100)
            duration: Optional duration in seconds
        """
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        
        await self._send_message(MessageType.MOVE_FORWARD, data)
    
    async def move_backward(self, speed: int = 70, duration: float = None):
        """Move robot backward."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        
        await self._send_message(MessageType.MOVE_BACKWARD, data)
    
    async def turn_left(self, speed: int = 50, duration: float = None):
        """Turn robot left."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        
        await self._send_message(MessageType.TURN_LEFT, data)
    
    async def turn_right(self, speed: int = 50, duration: float = None):
        """Turn robot right."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        
        await self._send_message(MessageType.TURN_RIGHT, data)
    
    async def stop(self):
        """Stop robot."""
        await self._send_message(MessageType.STOP)
    
    async def set_speed(self, speed: int):
        """Set motor speed."""
        await self._send_message(MessageType.SET_SPEED, {"speed": speed})
    
    # Camera commands
    async def start_camera(self):
        """Start camera streaming."""
        await self._send_message(MessageType.START_CAMERA)
    
    async def stop_camera(self):
        """Stop camera streaming."""
        await self._send_message(MessageType.STOP_CAMERA)
    
    # LiDAR commands
    async def start_lidar(self):
        """Start LiDAR scanning."""
        await self._send_message(MessageType.START_LIDAR)
    
    async def stop_lidar(self):
        """Stop LiDAR scanning."""
        await self._send_message(MessageType.STOP_LIDAR)
    
    # Configuration
    async def update_gpio_config(self, config: Dict):
        """Update GPIO configuration.
        
        Args:
            config: GPIO configuration dictionary
        """
        await self._send_message(MessageType.GPIO_CONFIG, {"config": config})
    
    async def get_config(self):
        """Request current configuration."""
        await self._send_message(MessageType.GET_CONFIG)
    
    # Voice/AI
    async def send_voice_command(self, command: str):
        """Send voice command to robot.
        
        Args:
            command: Voice command text
        """
        await self._send_message(MessageType.VOICE_COMMAND, {"command": command})
    
    async def send_face_expression(self, expression: str):
        """Set robot face expression.
        
        Args:
            expression: Expression name
        """
        await self._send_message(MessageType.FACE_EXPRESSION, {"expression": expression})
