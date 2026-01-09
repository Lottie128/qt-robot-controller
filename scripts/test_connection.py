#!/usr/bin/env python3
"""Test connection to robot server.

Simple utility to verify network connectivity.
"""

import asyncio
import sys
import argparse
from pathlib import Path

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    print("❌ websockets not installed")
    print("Install with: pip install websockets")
    sys.exit(1)

from shared.protocol import Protocol, MessageType


async def test_connection(host: str, port: int):
    """Test connection to robot server.
    
    Args:
        host: Robot IP address
        port: Server port
    """
    uri = f"ws://{host}:{port}"
    
    print(f"\n🔌 Testing connection to {uri}...")
    print("-" * 50)
    
    try:
        # Connect
        print("⏳ Connecting...")
        async with websockets.connect(uri, timeout=5) as websocket:
            print("✅ Connection established!")
            
            # Send ping
            print("\n📬 Sending test message...")
            message = Protocol.create_message(MessageType.PING)
            await websocket.send(message)
            print("✅ Message sent")
            
            # Wait for response
            print("\n⏳ Waiting for response...")
            response = await asyncio.wait_for(websocket.recv(), timeout=5)
            print(f"✅ Received: {response}")
            
            print("\n" + "=" * 50)
            print("✅ CONNECTION TEST SUCCESSFUL!")
            print("=" * 50)
            return True
    
    except asyncio.TimeoutError:
        print("\n❌ Timeout - No response from server")
        print("Make sure the robot server is running.")
        return False
    
    except ConnectionRefusedError:
        print("\n❌ Connection refused")
        print("Possible issues:")
        print("  - Robot server not running")
        print("  - Wrong IP address or port")
        print("  - Firewall blocking connection")
        return False
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test connection to Qt Robot Controller server"
    )
    parser.add_argument(
        "host",
        help="Robot IP address (e.g., 192.168.1.100)"
    )
    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8888,
        help="Server port (default: 8888)"
    )
    
    args = parser.parse_args()
    
    print("🤖 Qt Robot Controller - Connection Test")
    
    # Run test
    success = asyncio.run(test_connection(args.host, args.port))
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
