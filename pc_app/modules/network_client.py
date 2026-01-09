"""Network client for communicating with Raspberry Pi robot server.

Handles WebSocket connection, command sending, and data receiving.
"""

import asyncio
import json
import logging
from typing import Optional, Callable, Dict, Any
from datetime import datetime

try:
    import websockets
    from websockets.client import WebSocketClientProtocol
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("⚠️  websockets not available - install with: pip install websockets")

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.protocol import MessageType, Status, Protocol
from shared.constants import DEFAULT_PORT, CONNECTION_TIMEOUT


class RobotClient:
    """WebSocket client for robot communication."""
    
    def __init__(self):
        """Initialize robot client."""
        self.websocket: Optional[WebSocketClientProtocol] = None
        self.connected = False
        self.host = ""
        self.port = DEFAULT_PORT
        
        # Callbacks
        self.on_connected: Optional[Callable] = None
        self.on_disconnected: Optional[Callable] = None
        self.on_message: Optional[Callable[[Dict], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        # Reception loop
        self.receive_task: Optional[asyncio.Task] = None
        
        # Logging
        self.logger = logging.getLogger(__name__)
    
    async def connect(self, host: str, port: int = DEFAULT_PORT) -> bool:
        """Connect to robot server.
        
        Args:
            host: Server IP address
            port: Server port (default 8888)
            
        Returns:
            True if connected successfully
        """
        if not WEBSOCKETS_AVAILABLE:
            self.logger.error("websockets library not available")
            return False
        
        self.host = host
        self.port = port
        uri = f"ws://{host}:{port}"
        
        try:
            self.logger.info(f"Connecting to {uri}...")
            self.websocket = await asyncio.wait_for(
                websockets.connect(uri),
                timeout=CONNECTION_TIMEOUT
            )
            
            self.connected = True
            self.logger.info(f"✅ Connected to robot at {host}:{port}")
            
            # Start receive loop
            self.receive_task = asyncio.create_task(self._receive_loop())
            
            if self.on_connected:
                self.on_connected()
            
            return True
        
        except asyncio.TimeoutError:
            self.logger.error(f"Connection timeout to {uri}")
            if self.on_error:
                self.on_error(f"Connection timeout to {host}:{port}")
            return False
        
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            if self.on_error:
                self.on_error(f"Connection failed: {str(e)}")
            return False
    
    async def disconnect(self):
        """Disconnect from robot server."""
        if self.websocket:
            self.connected = False
            
            # Cancel receive task
            if self.receive_task:
                self.receive_task.cancel()
                try:
                    await self.receive_task
                except asyncio.CancelledError:
                    pass
            
            # Close WebSocket
            await self.websocket.close()
            self.websocket = None
            
            self.logger.info("Disconnected from robot")
            
            if self.on_disconnected:
                self.on_disconnected()
    
    async def _receive_loop(self):
        """Receive messages from server."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    
                    # Log received message
                    msg_type = data.get("type", "unknown")
                    self.logger.debug(f"← Received: {msg_type}")
                    
                    # Call message callback
                    if self.on_message:
                        self.on_message(data)
                
                except json.JSONDecodeError as e:
                    self.logger.error(f"Invalid JSON received: {e}")
        
        except websockets.exceptions.ConnectionClosed:
            self.logger.warning("Connection closed by server")
            self.connected = False
            if self.on_disconnected:
                self.on_disconnected()
        
        except Exception as e:
            self.logger.error(f"Receive loop error: {e}")
            if self.on_error:
                self.on_error(f"Receive error: {str(e)}")
    
    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send message to robot.
        
        Args:
            message: Message dictionary
            
        Returns:
            True if sent successfully
        """
        if not self.connected or not self.websocket:
            self.logger.error("Not connected to robot")
            return False
        
        try:
            message_str = json.dumps(message)
            await self.websocket.send(message_str)
            
            msg_type = message.get("type", "unknown")
            self.logger.debug(f"→ Sent: {msg_type}")
            return True
        
        except Exception as e:
            self.logger.error(f"Failed to send message: {e}")
            if self.on_error:
                self.on_error(f"Send failed: {str(e)}")
            return False
    
    async def send_command(self, msg_type: MessageType, data: Dict[str, Any] = None) -> bool:
        """Send command to robot.
        
        Args:
            msg_type: Message type
            data: Command data
            
        Returns:
            True if sent successfully
        """
        message = {
            "type": msg_type.value,
            "data": data or {},
            "timestamp": datetime.now().isoformat()
        }
        return await self.send_message(message)
    
    # Movement commands
    async def move_forward(self, speed: int = 70, duration: float = None) -> bool:
        """Move robot forward."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        return await self.send_command(MessageType.MOVE_FORWARD, data)
    
    async def move_backward(self, speed: int = 70, duration: float = None) -> bool:
        """Move robot backward."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        return await self.send_command(MessageType.MOVE_BACKWARD, data)
    
    async def turn_left(self, speed: int = 50, duration: float = None) -> bool:
        """Turn robot left."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        return await self.send_command(MessageType.TURN_LEFT, data)
    
    async def turn_right(self, speed: int = 50, duration: float = None) -> bool:
        """Turn robot right."""
        data = {"speed": speed}
        if duration:
            data["duration"] = duration
        return await self.send_command(MessageType.TURN_RIGHT, data)
    
    async def stop(self) -> bool:
        """Stop robot."""
        return await self.send_command(MessageType.STOP)
    
    async def set_speed(self, speed: int) -> bool:
        """Set motor speed."""
        return await self.send_command(MessageType.SET_SPEED, {"speed": speed})
    
    # Camera commands
    async def start_camera(self) -> bool:
        """Start camera streaming."""
        return await self.send_command(MessageType.START_CAMERA)
    
    async def stop_camera(self) -> bool:
        """Stop camera streaming."""
        return await self.send_command(MessageType.STOP_CAMERA)
    
    # LiDAR commands
    async def start_lidar(self) -> bool:
        """Start LiDAR scanning."""
        return await self.send_command(MessageType.START_LIDAR)
    
    async def stop_lidar(self) -> bool:
        """Stop LiDAR scanning."""
        return await self.send_command(MessageType.STOP_LIDAR)
    
    # Configuration
    async def update_gpio_config(self, config: Dict) -> bool:
        """Update GPIO configuration."""
        return await self.send_command(MessageType.GPIO_CONFIG, {"config": config})
    
    async def get_config(self) -> bool:
        """Request current configuration."""
        return await self.send_command(MessageType.GET_CONFIG)
    
    # Voice/AI commands
    async def send_voice_command(self, text: str) -> bool:
        """Send voice command text."""
        return await self.send_command(MessageType.VOICE_COMMAND, {"text": text})
    
    async def send_tts(self, text: str) -> bool:
        """Send text-to-speech command."""
        return await self.send_command(MessageType.TTS_SPEAK, {"text": text})
    
    # Face expression
    async def set_expression(self, expression: str) -> bool:
        """Set robot face expression."""
        return await self.send_command(MessageType.FACE_EXPRESSION, {"expression": expression})
    
    def is_connected(self) -> bool:
        """Check if connected to robot."""
        return self.connected
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get connection information."""
        return {
            "connected": self.connected,
            "host": self.host,
            "port": self.port
        }
