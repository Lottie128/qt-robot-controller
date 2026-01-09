"""LiDAR module for SLAM and obstacle detection.

Supports:
- RP-LIDAR A1/A2/A3
- Real-time scan data
- Obstacle detection
- Distance measurements
"""

import time
import threading
from typing import List, Tuple, Optional
import math

try:
    from rplidar import RPLidar
    RPLIDAR_AVAILABLE = True
except ImportError:
    RPLIDAR_AVAILABLE = False
    print("⚠️  rplidar library not available - LiDAR disabled")


class LiDARModule:
    """LiDAR handler for scanning and obstacle detection."""
    
    def __init__(self, config: dict):
        """Initialize LiDAR module.
        
        Args:
            config: LiDAR configuration dictionary
        """
        self.config = config
        self.port = config.get("port", "/dev/ttyUSB0")
        self.baudrate = config.get("baudrate", 115200)
        self.scan_mode = config.get("scan_mode", "standard")
        
        self.lidar = None
        self.is_scanning = False
        self.scan_data = []
        self.data_lock = threading.Lock()
        self.scan_thread = None
        
        if RPLIDAR_AVAILABLE:
            self._init_lidar()
        else:
            print("⚠️  LiDAR module disabled (library not installed)")
    
    def _init_lidar(self):
        """Initialize LiDAR hardware."""
        try:
            self.lidar = RPLidar(self.port, baudrate=self.baudrate)
            
            # Get device info
            info = self.lidar.get_info()
            health = self.lidar.get_health()
            
            print(f"✅ LiDAR initialized: {info}")
            print(f"   Health: {health}")
        except Exception as e:
            print(f"❌ LiDAR init failed: {e}")
            self.lidar = None
    
    def start_scanning(self):
        """Start LiDAR scanning."""
        if not self.lidar:
            print("⚠️  LiDAR not available")
            return
        
        if self.is_scanning:
            print("⚠️  LiDAR already scanning")
            return
        
        self.is_scanning = True
        self.scan_thread = threading.Thread(target=self._scan_loop, daemon=True)
        self.scan_thread.start()
        print("🔄 LiDAR scanning started")
    
    def stop_scanning(self):
        """Stop LiDAR scanning."""
        self.is_scanning = False
        
        if self.scan_thread:
            self.scan_thread.join(timeout=2)
        
        if self.lidar:
            try:
                self.lidar.stop()
                self.lidar.stop_motor()
            except:
                pass
        
        print("⏹️  LiDAR scanning stopped")
    
    def _scan_loop(self):
        """Continuous scanning loop."""
        try:
            for scan in self.lidar.iter_scans():
                if not self.is_scanning:
                    break
                
                with self.data_lock:
                    self.scan_data = scan
        except Exception as e:
            print(f"❌ LiDAR scan error: {e}")
            self.is_scanning = False
    
    def get_scan_data(self) -> List[Tuple[float, float, float]]:
        """Get latest scan data.
        
        Returns:
            List of (quality, angle, distance) tuples
        """
        with self.data_lock:
            return self.scan_data.copy()
    
    def get_obstacles(self, min_distance: float = 500) -> List[Tuple[float, float]]:
        """Get obstacles within minimum distance.
        
        Args:
            min_distance: Minimum distance in mm
            
        Returns:
            List of (angle, distance) tuples for obstacles
        """
        obstacles = []
        scan_data = self.get_scan_data()
        
        for quality, angle, distance in scan_data:
            if 0 < distance < min_distance and quality > 10:
                obstacles.append((angle, distance))
        
        return obstacles
    
    def get_distance_at_angle(self, target_angle: float, tolerance: float = 5.0) -> Optional[float]:
        """Get distance measurement at specific angle.
        
        Args:
            target_angle: Target angle in degrees (0-360)
            tolerance: Angle tolerance in degrees
            
        Returns:
            Distance in mm or None if no measurement
        """
        scan_data = self.get_scan_data()
        
        for quality, angle, distance in scan_data:
            if abs(angle - target_angle) <= tolerance and quality > 10:
                return distance
        
        return None
    
    def get_front_distance(self) -> Optional[float]:
        """Get distance measurement directly ahead.
        
        Returns:
            Distance in mm or None
        """
        return self.get_distance_at_angle(0.0, tolerance=10.0)
    
    def check_path_clear(self, angle_range: Tuple[float, float], min_distance: float = 300) -> bool:
        """Check if path is clear in angle range.
        
        Args:
            angle_range: (start_angle, end_angle) tuple
            min_distance: Minimum safe distance in mm
            
        Returns:
            True if path is clear, False if obstacles detected
        """
        start_angle, end_angle = angle_range
        scan_data = self.get_scan_data()
        
        for quality, angle, distance in scan_data:
            if start_angle <= angle <= end_angle:
                if 0 < distance < min_distance and quality > 10:
                    return False
        
        return True
    
    def get_scan_visualization(self) -> List[Tuple[float, float]]:
        """Get scan data in cartesian coordinates for visualization.
        
        Returns:
            List of (x, y) tuples in meters
        """
        points = []
        scan_data = self.get_scan_data()
        
        for quality, angle, distance in scan_data:
            if quality > 10 and distance > 0:
                # Convert to radians
                angle_rad = math.radians(angle)
                
                # Convert to meters and cartesian
                distance_m = distance / 1000.0
                x = distance_m * math.cos(angle_rad)
                y = distance_m * math.sin(angle_rad)
                
                points.append((x, y))
        
        return points
    
    def cleanup(self):
        """Cleanup LiDAR resources."""
        self.stop_scanning()
        
        if self.lidar:
            try:
                self.lidar.stop()
                self.lidar.stop_motor()
                self.lidar.disconnect()
            except:
                pass
        
        print("✅ LiDAR cleaned up")
