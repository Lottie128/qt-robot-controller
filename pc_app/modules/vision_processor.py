"""Vision processor for analyzing camera feed.

Basic image processing and object detection.
"""

import logging
from typing import Optional, List, Tuple
import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


class VisionProcessor:
    """Vision processing handler."""
    
    def __init__(self):
        """Initialize vision processor."""
        self.logger = logging.getLogger(__name__)
        
        if not CV2_AVAILABLE:
            self.logger.warning("⚠️  OpenCV not available")
    
    def is_available(self) -> bool:
        """Check if vision processing is available."""
        return CV2_AVAILABLE
    
    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """Process single video frame.
        
        Args:
            frame: Input frame (BGR)
            
        Returns:
            Processed frame
        """
        if not CV2_AVAILABLE:
            return frame
        
        # Add processing here (edge detection, face detection, etc.)
        return frame
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in frame.
        
        Args:
            frame: Input frame
            
        Returns:
            List of (x, y, w, h) face rectangles
        """
        if not CV2_AVAILABLE:
            return []
        
        # Load face detector
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        return [(x, y, w, h) for x, y, w, h in faces]
    
    def detect_edges(self, frame: np.ndarray) -> np.ndarray:
        """Detect edges in frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Edge image
        """
        if not CV2_AVAILABLE:
            return frame
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        return edges
    
    def decode_jpeg(self, jpeg_bytes: bytes) -> Optional[np.ndarray]:
        """Decode JPEG bytes to frame.
        
        Args:
            jpeg_bytes: JPEG encoded image
            
        Returns:
            Decoded frame or None
        """
        if not CV2_AVAILABLE:
            return None
        
        try:
            nparr = np.frombuffer(jpeg_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        except:
            return None
    
    def decode_base64(self, base64_str: str) -> Optional[np.ndarray]:
        """Decode base64 image to frame.
        
        Args:
            base64_str: Base64 encoded image
            
        Returns:
            Decoded frame or None
        """
        import base64
        try:
            jpeg_bytes = base64.b64decode(base64_str)
            return self.decode_jpeg(jpeg_bytes)
        except:
            return None
