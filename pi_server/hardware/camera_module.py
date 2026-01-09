"""Camera module for video streaming.

Supports:
- OpenCV USB cameras
- Raspberry Pi Camera Module (CSI)
- JPEG encoding for streaming
- Adjustable resolution and quality
"""

import cv2
import base64
import threading
import time
from typing import Optional, Tuple
import numpy as np

try:
    from picamera2 import Picamera2
    PICAMERA2_AVAILABLE = True
except ImportError:
    PICAMERA2_AVAILABLE = False
    print("⚠️  picamera2 not available - using OpenCV only")


class CameraModule:
    """Camera handler for video capture and streaming."""
    
    def __init__(self, config: dict):
        """Initialize camera module.
        
        Args:
            config: Camera configuration dictionary
        """
        self.config = config
        self.camera_type = config.get("type", "opencv")
        self.device_id = config.get("device_id", 0)
        self.width = config.get("width", 640)
        self.height = config.get("height", 480)
        self.fps = config.get("fps", 30)
        self.quality = config.get("stream_quality", 80)
        
        self.camera = None
        self.is_streaming = False
        self.current_frame = None
        self.frame_lock = threading.Lock()
        self.capture_thread = None
        
        self._init_camera()
    
    def _init_camera(self):
        """Initialize camera based on type."""
        try:
            if self.camera_type == "picamera2" and PICAMERA2_AVAILABLE:
                self._init_picamera()
            else:
                self._init_opencv_camera()
            
            print(f"✅ Camera initialized: {self.camera_type} ({self.width}x{self.height})")
        except Exception as e:
            print(f"❌ Camera init failed: {e}")
            raise
    
    def _init_opencv_camera(self):
        """Initialize OpenCV camera."""
        self.camera = cv2.VideoCapture(self.device_id)
        
        if not self.camera.isOpened():
            raise RuntimeError(f"Failed to open camera {self.device_id}")
        
        # Set resolution
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
        self.camera.set(cv2.CAP_PROP_FPS, self.fps)
        
        self.camera_type = "opencv"
    
    def _init_picamera(self):
        """Initialize Raspberry Pi camera."""
        self.camera = Picamera2()
        config = self.camera.create_preview_configuration(
            main={"size": (self.width, self.height)}
        )
        self.camera.configure(config)
        self.camera.start()
        time.sleep(2)  # Camera warm-up
    
    def start_streaming(self):
        """Start camera streaming."""
        if self.is_streaming:
            print("⚠️  Camera already streaming")
            return
        
        self.is_streaming = True
        self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        print("📹 Camera streaming started")
    
    def stop_streaming(self):
        """Stop camera streaming."""
        self.is_streaming = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2)
        print("⏹️  Camera streaming stopped")
    
    def _capture_loop(self):
        """Continuous frame capture loop."""
        while self.is_streaming:
            try:
                frame = self._capture_frame()
                if frame is not None:
                    with self.frame_lock:
                        self.current_frame = frame
                
                # Maintain frame rate
                time.sleep(1.0 / self.fps)
            except Exception as e:
                print(f"❌ Frame capture error: {e}")
                time.sleep(0.1)
    
    def _capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame.
        
        Returns:
            Frame as numpy array or None if failed
        """
        if self.camera_type == "opencv":
            ret, frame = self.camera.read()
            return frame if ret else None
        elif self.camera_type == "picamera2":
            return self.camera.capture_array()
        return None
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the latest captured frame.
        
        Returns:
            Latest frame or None
        """
        with self.frame_lock:
            return self.current_frame.copy() if self.current_frame is not None else None
    
    def get_frame_jpeg(self) -> Optional[bytes]:
        """Get latest frame as JPEG bytes.
        
        Returns:
            JPEG encoded frame or None
        """
        frame = self.get_frame()
        if frame is None:
            return None
        
        # Encode to JPEG
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), self.quality]
        _, buffer = cv2.imencode('.jpg', frame, encode_param)
        return buffer.tobytes()
    
    def get_frame_base64(self) -> Optional[str]:
        """Get latest frame as base64 encoded JPEG.
        
        Returns:
            Base64 string or None
        """
        jpeg_bytes = self.get_frame_jpeg()
        if jpeg_bytes is None:
            return None
        
        return base64.b64encode(jpeg_bytes).decode('utf-8')
    
    def adjust_settings(self, brightness: int = None, contrast: int = None):
        """Adjust camera settings.
        
        Args:
            brightness: Brightness level (0-100)
            contrast: Contrast level (0-100)
        """
        if self.camera_type == "opencv" and self.camera:
            if brightness is not None:
                self.camera.set(cv2.CAP_PROP_BRIGHTNESS, brightness / 100.0)
            if contrast is not None:
                self.camera.set(cv2.CAP_PROP_CONTRAST, contrast / 100.0)
    
    def get_resolution(self) -> Tuple[int, int]:
        """Get current camera resolution.
        
        Returns:
            (width, height) tuple
        """
        return (self.width, self.height)
    
    def set_resolution(self, width: int, height: int):
        """Change camera resolution.
        
        Args:
            width: New width
            height: New height
        """
        was_streaming = self.is_streaming
        
        if was_streaming:
            self.stop_streaming()
        
        self.width = width
        self.height = height
        
        if self.camera_type == "opencv":
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        elif self.camera_type == "picamera2":
            self.camera.stop()
            config = self.camera.create_preview_configuration(
                main={"size": (width, height)}
            )
            self.camera.configure(config)
            self.camera.start()
        
        if was_streaming:
            self.start_streaming()
        
        print(f"📐 Resolution changed to {width}x{height}")
    
    def cleanup(self):
        """Cleanup camera resources."""
        self.stop_streaming()
        
        if self.camera:
            if self.camera_type == "opencv":
                self.camera.release()
            elif self.camera_type == "picamera2":
                self.camera.stop()
        
        print("✅ Camera cleaned up")
