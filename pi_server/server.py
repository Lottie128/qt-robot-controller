#!/usr/bin/env python3
"""Qt Robot Controller - Raspberry Pi Server

Simple WebSocket server that:
1. Auto-detects local IP addresses
2. Displays connection information
3. Handles commands from PC Qt application
4. Streams sensor data back to PC
"""

import asyncio
import json
import socket
import sys
import time
from pathlib import Path
from typing import Dict, Set

import websockets
from colorama import Fore, Style, init
import yaml

# Add parent directory to path for shared modules
sys.path.append(str(Path(__file__).parent.parent))
from shared.protocol import MessageType, Status, DEFAULT_PORT
from shared.constants import VERSION

# Import hardware modules
from hardware.motor_controller import MotorController

# Initialize colorama
init(autoreset=True)


class RobotServer:
    """Main robot server class."""
    
    def __init__(self, config_path: str = "config/hardware_config.yaml"):
        """Initialize robot server.
        
        Args:
            config_path: Path to hardware configuration file
        """
        self.config = self._load_config(config_path)
        self.port = self.config.get("server_port", DEFAULT_PORT)
        self.connected_clients: Set[websockets.WebSocketServerProtocol] = set()
        
        # Initialize hardware
        self.motor_controller = None
        self._init_hardware()
        
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}🤖 Qt Robot Server v{VERSION}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"{Fore.YELLOW}⚠️  Config not found, using defaults{Style.RESET_ALL}")
            return {"server_port": DEFAULT_PORT}
    
    def _init_hardware(self):
        """Initialize hardware controllers."""
        try:
            motor_config = self.config.get("motors", {})
            self.motor_controller = MotorController(motor_config)
            print(f"{Fore.GREEN}✅ Motors initialized{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Motor init failed: {e}{Style.RESET_ALL}")
    
    def get_local_ips(self) -> Dict[str, str]:
        """Get all local IP addresses.
        
        Returns:
            Dictionary of interface names to IP addresses
        """
        ips = {}
        
        # Get hostname IP
        try:
            hostname = socket.gethostname()
            host_ip = socket.gethostbyname(hostname)
            if host_ip != "127.0.0.1":
                ips["hostname"] = host_ip
        except:
            pass
        
        # Get all interface IPs (Linux)
        try:
            import netifaces
            for interface in netifaces.interfaces():
                if interface.startswith(('eth', 'wlan', 'en', 'wl')):
                    addrs = netifaces.ifaddresses(interface)
                    if netifaces.AF_INET in addrs:
                        ip = addrs[netifaces.AF_INET][0]['addr']
                        if ip != "127.0.0.1":
                            ips[interface] = ip
        except ImportError:
            # Fallback if netifaces not available
            pass
        
        # Fallback: connect to external IP
        if not ips:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                ips["default"] = s.getsockname()[0]
                s.close()
            except:
                ips["localhost"] = "127.0.0.1"
        
        return ips
    
    def display_connection_info(self):
        """Display connection information for user."""
        ips = self.get_local_ips()
        
        print(f"\n{Fore.CYAN}📡 Network Interfaces:{Style.RESET_ALL}")
        for interface, ip in ips.items():
            print(f"   {Fore.WHITE}• {interface}: {Fore.YELLOW}{ip}{Style.RESET_ALL}")
        
        print(f"\n{Fore.GREEN}🔌 Server running on {Fore.YELLOW}0.0.0.0:{self.port}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}⚡ Waiting for PC connection...{Style.RESET_ALL}")
        print(f"\n{Fore.WHITE}Enter this IP in your PC Qt application:{Style.RESET_ALL}")
        
        # Show primary IP prominently
        primary_ip = next(iter(ips.values()))
        print(f"{Fore.GREEN}→ {Fore.YELLOW}{primary_ip}:{self.port}{Style.RESET_ALL}")
        print()
    
    async def handle_client(self, websocket: websockets.WebSocketServerProtocol):
        """Handle connected client.
        
        Args:
            websocket: WebSocket connection
        """
        client_addr = websocket.remote_address
        print(f"{Fore.GREEN}✅ Client connected: {client_addr[0]}:{client_addr[1]}{Style.RESET_ALL}")
        
        self.connected_clients.add(websocket)
        
        try:
            async for message in websocket:
                await self.process_message(websocket, message)
        except websockets.exceptions.ConnectionClosed:
            print(f"{Fore.YELLOW}⚠️  Client disconnected: {client_addr[0]}:{client_addr[1]}{Style.RESET_ALL}")
        finally:
            self.connected_clients.remove(websocket)
    
    async def process_message(self, websocket: websockets.WebSocketServerProtocol, message: str):
        """Process incoming message from client.
        
        Args:
            websocket: WebSocket connection
            message: JSON message string
        """
        try:
            data = json.loads(message)
            msg_type = data.get("type")
            
            print(f"{Fore.CYAN}← Received: {msg_type}{Style.RESET_ALL}")
            
            # Handle different message types
            if msg_type == MessageType.MOVE_FORWARD.value:
                await self.handle_move_forward(websocket, data)
            elif msg_type == MessageType.MOVE_BACKWARD.value:
                await self.handle_move_backward(websocket, data)
            elif msg_type == MessageType.TURN_LEFT.value:
                await self.handle_turn_left(websocket, data)
            elif msg_type == MessageType.TURN_RIGHT.value:
                await self.handle_turn_right(websocket, data)
            elif msg_type == MessageType.STOP.value:
                await self.handle_stop(websocket, data)
            elif msg_type == MessageType.GPIO_CONFIG.value:
                await self.handle_gpio_config(websocket, data)
            else:
                await self.send_error(websocket, f"Unknown message type: {msg_type}")
        
        except json.JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON")
        except Exception as e:
            await self.send_error(websocket, str(e))
    
    async def handle_move_forward(self, websocket, data: Dict):
        """Handle move forward command."""
        speed = data.get("speed", 70)
        duration = data.get("duration")
        
        if self.motor_controller:
            self.motor_controller.move_forward(speed)
            if duration:
                await asyncio.sleep(duration)
                self.motor_controller.stop()
        
        await self.send_response(websocket, "success", {"action": "move_forward"})
    
    async def handle_move_backward(self, websocket, data: Dict):
        """Handle move backward command."""
        speed = data.get("speed", 70)
        duration = data.get("duration")
        
        if self.motor_controller:
            self.motor_controller.move_backward(speed)
            if duration:
                await asyncio.sleep(duration)
                self.motor_controller.stop()
        
        await self.send_response(websocket, "success", {"action": "move_backward"})
    
    async def handle_turn_left(self, websocket, data: Dict):
        """Handle turn left command."""
        speed = data.get("speed", 50)
        duration = data.get("duration")
        
        if self.motor_controller:
            self.motor_controller.turn_left(speed)
            if duration:
                await asyncio.sleep(duration)
                self.motor_controller.stop()
        
        await self.send_response(websocket, "success", {"action": "turn_left"})
    
    async def handle_turn_right(self, websocket, data: Dict):
        """Handle turn right command."""
        speed = data.get("speed", 50)
        duration = data.get("duration")
        
        if self.motor_controller:
            self.motor_controller.turn_right(speed)
            if duration:
                await asyncio.sleep(duration)
                self.motor_controller.stop()
        
        await self.send_response(websocket, "success", {"action": "turn_right"})
    
    async def handle_stop(self, websocket, data: Dict):
        """Handle stop command."""
        if self.motor_controller:
            self.motor_controller.stop()
        
        await self.send_response(websocket, "success", {"action": "stop"})
    
    async def handle_gpio_config(self, websocket, data: Dict):
        """Handle GPIO configuration update."""
        try:
            new_config = data.get("config", {})
            
            # Reinitialize motor controller with new config
            if self.motor_controller:
                self.motor_controller.cleanup()
            
            self.motor_controller = MotorController(new_config)
            
            # Update config file
            self.config["motors"] = new_config
            with open("config/hardware_config.yaml", 'w') as f:
                yaml.dump(self.config, f)
            
            print(f"{Fore.GREEN}✅ GPIO configuration updated{Style.RESET_ALL}")
            await self.send_response(websocket, "success", {"action": "gpio_config_updated"})
        
        except Exception as e:
            await self.send_error(websocket, f"GPIO config failed: {e}")
    
    async def send_response(self, websocket, status: str, data: Dict = None):
        """Send response to client."""
        response = {
            "type": MessageType.RESPONSE.value,
            "status": status,
            "timestamp": time.time(),
            "data": data or {}
        }
        await websocket.send(json.dumps(response))
        print(f"{Fore.GREEN}→ Sent: {status}{Style.RESET_ALL}")
    
    async def send_error(self, websocket, error_msg: str):
        """Send error response to client."""
        response = {
            "type": MessageType.ERROR.value,
            "status": Status.ERROR.value,
            "error": error_msg,
            "timestamp": time.time()
        }
        await websocket.send(json.dumps(response))
        print(f"{Fore.RED}❌ Error: {error_msg}{Style.RESET_ALL}")
    
    async def start(self):
        """Start the WebSocket server."""
        self.display_connection_info()
        
        async with websockets.serve(self.handle_client, "0.0.0.0", self.port):
            await asyncio.Future()  # Run forever
    
    def cleanup(self):
        """Cleanup resources."""
        print(f"\n{Fore.YELLOW}Shutting down server...{Style.RESET_ALL}")
        if self.motor_controller:
            self.motor_controller.cleanup()
        print(f"{Fore.GREEN}✅ Cleanup complete{Style.RESET_ALL}")


def main():
    """Main entry point."""
    server = RobotServer()
    
    try:
        asyncio.run(server.start())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Received interrupt signal{Style.RESET_ALL}")
    finally:
        server.cleanup()


if __name__ == "__main__":
    main()
