"""Vision processor for camera feed analysis.

Processes video frames from robot camera for object detection, etc.
"""

import logging
import numpy as np
from typing import Optional, List, Tuple, Dict

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("⚠️  opencv-python not available - install with: pip install opencv-python")


class VisionProcessor:
    """Process video frames from robot camera."""
    
    def __init__(self):
        """Initialize vision processor."""
        self.logger = logging.getLogger(__name__)
        self.face_cascade = None
        
        if CV2_AVAILABLE:
            self._init_detectors()
        else:
            self.logger.warning("OpenCV not available")
    
    def _init_detectors(self):
        """Initialize detection models."""
        try:
            # Load face detection cascade
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
            
            if self.face_cascade.empty():
                self.logger.warning("Failed to load face cascade")
                self.face_cascade = None
            else:
                self.logger.info("✅ Vision processor initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize detectors: {e}")
    
    def is_available(self) -> bool:
        """Check if vision processing is available."""
        return CV2_AVAILABLE
    
    def decode_frame(self, frame_data: bytes) -> Optional[np.ndarray]:
        """Decode JPEG frame data to numpy array.
        
        Args:
            frame_data: JPEG bytes
            
        Returns:
            Frame as numpy array or None
        """
        if not CV2_AVAILABLE:
            return None
        
        try:
            # Decode JPEG
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            return frame
        
        except Exception as e:
            self.logger.error(f"Frame decode error: {e}")
            return None
    
    def encode_frame(self, frame: np.ndarray, quality: int = 80) -> Optional[bytes]:
        """Encode frame to JPEG bytes.
        
        Args:
            frame: Frame as numpy array
            quality: JPEG quality (0-100)
            
        Returns:
            JPEG bytes or None
        """
        if not CV2_AVAILABLE:
            return None
        
        try:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
            _, buffer = cv2.imencode('.jpg', frame, encode_param)
            return buffer.tobytes()
        
        except Exception as e:
            self.logger.error(f"Frame encode error: {e}")
            return None
    
    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect faces in frame.
        
        Args:
            frame: Input frame
            
        Returns:
            List of (x, y, w, h) tuples for detected faces
        """
        if not self.face_cascade:
            return []
        
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            return faces.tolist()
        
        except Exception as e:
            self.logger.error(f"Face detection error: {e}")
            return []
    
    def draw_faces(self, frame: np.ndarray, faces: List[Tuple]) -> np.ndarray:
        """Draw rectangles around detected faces.
        
        Args:
            frame: Input frame
            faces: List of (x, y, w, h) tuples
            
        Returns:
            Frame with rectangles drawn
        """
        if not CV2_AVAILABLE:
            return frame
        
        result = frame.copy()
        
        for (x, y, w, h) in faces:
            cv2.rectangle(result, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(result, "Face", (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result
    
    def add_overlay(self, frame: np.ndarray, text: str, 
                   position: Tuple[int, int] = (10, 30)) -> np.ndarray:
        """Add text overlay to frame.
        
        Args:
            frame: Input frame
            text: Text to display
            position: (x, y) position
            
        Returns:
            Frame with overlay
        """
        if not CV2_AVAILABLE:
            return frame
        
        result = frame.copy()
        cv2.putText(result, text, position, 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        return result
    
    def resize_frame(self, frame: np.ndarray, width: int, height: int) -> np.ndarray:
        """Resize frame to specified dimensions.
        
        Args:
            frame: Input frame
            width: Target width
            height: Target height
            
        Returns:
            Resized frame
        """
        if not CV2_AVAILABLE:
            return frame
        
        try:
            return cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
        except Exception as e:
            self.logger.error(f"Resize error: {e}")
            return frame
    
    def apply_filter(self, frame: np.ndarray, filter_type: str = "none") -> np.ndarray:
        """Apply visual filter to frame.
        
        Args:
            frame: Input frame
            filter_type: Filter type (none, grayscale, blur, edge)
            
        Returns:
            Filtered frame
        """
        if not CV2_AVAILABLE:
            return frame
        
        try:
            if filter_type == "grayscale":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
            
            elif filter_type == "blur":
                return cv2.GaussianBlur(frame, (15, 15), 0)
            
            elif filter_type == "edge":
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                edges = cv2.Canny(gray, 50, 150)
                return cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
            
            else:
                return frame
        
        except Exception as e:
            self.logger.error(f"Filter error: {e}")
            return frame
    
    def get_frame_info(self, frame: np.ndarray) -> Dict:
        """Get information about frame.
        
        Args:
            frame: Input frame
            
        Returns:
            Dictionary with frame info
        """
        if frame is None:
            return {}
        
        return {
            "width": frame.shape[1],
            "height": frame.shape[0],
            "channels": frame.shape[2] if len(frame.shape) > 2 else 1,
            "dtype": str(frame.dtype)
        }
