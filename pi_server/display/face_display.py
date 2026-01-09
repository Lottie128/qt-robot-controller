"""Face display module for LCD/OLED screens.

Supports:
- Animated face expressions
- Eye animations
- Mouth movements for speech
- OLED and LCD displays
"""

import time
import threading
from typing import Optional, Tuple
from enum import Enum

try:
    from PIL import Image, ImageDraw
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - display disabled")

try:
    from luma.core.interface.serial import i2c
    from luma.oled.device import ssd1306
    LUMA_AVAILABLE = True
except ImportError:
    LUMA_AVAILABLE = False
    print("⚠️  luma.oled not available - OLED display disabled")


class Expression(Enum):
    """Face expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    THINKING = "thinking"
    SLEEPING = "sleeping"
    CONFUSED = "confused"


class FaceDisplay:
    """Face animation display controller."""
    
    def __init__(self, config: dict):
        """Initialize face display.
        
        Args:
            config: Display configuration dictionary
        """
        self.config = config
        self.display_type = config.get("type", "oled")
        self.width = config.get("width", 128)
        self.height = config.get("height", 64)
        
        self.device = None
        self.current_expression = Expression.NEUTRAL
        self.is_animating = False
        self.animation_thread = None
        self.blink_counter = 0
        
        if PIL_AVAILABLE and LUMA_AVAILABLE:
            self._init_display()
        else:
            print("⚠️  Face display disabled (missing dependencies)")
    
    def _init_display(self):
        """Initialize display hardware."""
        try:
            if self.display_type == "oled":
                serial = i2c(port=1, address=0x3C)
                self.device = ssd1306(serial, width=self.width, height=self.height)
            
            print(f"✅ Display initialized: {self.display_type} ({self.width}x{self.height})")
            self.show_expression(Expression.NEUTRAL)
        except Exception as e:
            print(f"⚠️  Display init failed: {e}")
            self.device = None
    
    def _create_face_image(self, expression: Expression) -> Image:
        """Create face image for given expression.
        
        Args:
            expression: Face expression
            
        Returns:
            PIL Image object
        """
        img = Image.new('1', (self.width, self.height), color=0)
        draw = ImageDraw.Draw(img)
        
        # Calculate positions
        center_x = self.width // 2
        center_y = self.height // 2
        eye_y = center_y - 10
        eye_spacing = 20
        left_eye_x = center_x - eye_spacing
        right_eye_x = center_x + eye_spacing
        
        # Draw eyes based on expression
        if expression == Expression.NEUTRAL:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "normal")
            self._draw_mouth(draw, center_x, center_y + 15, "neutral")
        
        elif expression == Expression.HAPPY:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "happy")
            self._draw_mouth(draw, center_x, center_y + 15, "smile")
        
        elif expression == Expression.SAD:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "sad")
            self._draw_mouth(draw, center_x, center_y + 15, "frown")
        
        elif expression == Expression.ANGRY:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "angry")
            self._draw_mouth(draw, center_x, center_y + 15, "angry")
        
        elif expression == Expression.SURPRISED:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "wide")
            self._draw_mouth(draw, center_x, center_y + 15, "surprised")
        
        elif expression == Expression.THINKING:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "looking_up")
            self._draw_mouth(draw, center_x, center_y + 15, "thinking")
        
        elif expression == Expression.SLEEPING:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "closed")
            self._draw_mouth(draw, center_x, center_y + 15, "neutral")
        
        elif expression == Expression.CONFUSED:
            self._draw_eyes(draw, left_eye_x, eye_y, right_eye_x, eye_y, "confused")
            self._draw_mouth(draw, center_x, center_y + 15, "wavy")
        
        return img
    
    def _draw_eyes(self, draw, left_x: int, left_y: int, right_x: int, right_y: int, style: str):
        """Draw eyes on the face."""
        eye_size = 8
        
        if style == "normal":
            # Open circular eyes
            draw.ellipse([left_x - eye_size, left_y - eye_size, 
                         left_x + eye_size, left_y + eye_size], outline=1, fill=0)
            draw.ellipse([right_x - eye_size, right_y - eye_size, 
                         right_x + eye_size, right_y + eye_size], outline=1, fill=0)
            # Pupils
            draw.ellipse([left_x - 3, left_y - 3, left_x + 3, left_y + 3], fill=1)
            draw.ellipse([right_x - 3, right_y - 3, right_x + 3, right_y + 3], fill=1)
        
        elif style == "happy":
            # Curved happy eyes
            draw.arc([left_x - eye_size, left_y - eye_size, 
                     left_x + eye_size, left_y + eye_size], 0, 180, fill=1)
            draw.arc([right_x - eye_size, right_y - eye_size, 
                     right_x + eye_size, right_y + eye_size], 0, 180, fill=1)
        
        elif style == "closed":
            # Closed eyes (lines)
            draw.line([left_x - eye_size, left_y, left_x + eye_size, left_y], fill=1, width=2)
            draw.line([right_x - eye_size, right_y, right_x + eye_size, right_y], fill=1, width=2)
        
        elif style == "wide":
            # Wide open eyes
            draw.ellipse([left_x - eye_size, left_y - eye_size, 
                         left_x + eye_size, left_y + eye_size], outline=1, fill=1)
            draw.ellipse([right_x - eye_size, right_y - eye_size, 
                         right_x + eye_size, right_y + eye_size], outline=1, fill=1)
    
    def _draw_mouth(self, draw, x: int, y: int, style: str):
        """Draw mouth on the face."""
        mouth_width = 20
        mouth_height = 8
        
        if style == "neutral":
            draw.line([x - mouth_width, y, x + mouth_width, y], fill=1, width=2)
        
        elif style == "smile":
            draw.arc([x - mouth_width, y - mouth_height, 
                     x + mouth_width, y + mouth_height], 0, 180, fill=1)
        
        elif style == "frown":
            draw.arc([x - mouth_width, y - mouth_height, 
                     x + mouth_width, y + mouth_height], 180, 360, fill=1)
        
        elif style == "surprised":
            draw.ellipse([x - 8, y - 8, x + 8, y + 8], outline=1, fill=0)
    
    def show_expression(self, expression: Expression):
        """Display a face expression.
        
        Args:
            expression: Expression to display
        """
        if not self.device:
            return
        
        self.current_expression = expression
        img = self._create_face_image(expression)
        self.device.display(img)
        print(f"😀 Showing expression: {expression.value}")
    
    def start_animation(self):
        """Start face animation (blinking, etc.)."""
        if self.is_animating:
            return
        
        self.is_animating = True
        self.animation_thread = threading.Thread(target=self._animation_loop, daemon=True)
        self.animation_thread.start()
        print("🎭 Face animation started")
    
    def stop_animation(self):
        """Stop face animation."""
        self.is_animating = False
        if self.animation_thread:
            self.animation_thread.join(timeout=2)
        print("⏹️  Face animation stopped")
    
    def _animation_loop(self):
        """Animation loop for blinking and idle movements."""
        while self.is_animating:
            try:
                # Blink every ~3 seconds
                self.blink_counter += 1
                if self.blink_counter >= 30:
                    self.blink()
                    self.blink_counter = 0
                
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Animation error: {e}")
    
    def blink(self):
        """Perform a blink animation."""
        if not self.device:
            return
        
        # Quick blink
        img = self._create_face_image(Expression.SLEEPING)
        self.device.display(img)
        time.sleep(0.1)
        
        # Back to current expression
        img = self._create_face_image(self.current_expression)
        self.device.display(img)
    
    def clear(self):
        """Clear the display."""
        if self.device:
            self.device.clear()
    
    def cleanup(self):
        """Cleanup display resources."""
        self.stop_animation()
        self.clear()
        print("✅ Display cleaned up")
