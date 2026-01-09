"""Face animator for robot display.

Animates robot face expressions locally in the UI.
"""

import logging
from typing import Optional
from enum import Enum


class FaceExpression(Enum):
    """Face expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    THINKING = "thinking"
    SLEEPING = "sleeping"
    CONFUSED = "confused"


class FaceAnimator:
    """Animate robot face expressions in UI."""
    
    def __init__(self):
        """Initialize face animator."""
        self.current_expression = FaceExpression.NEUTRAL
        self.is_animating = False
        self.logger = logging.getLogger(__name__)
    
    def set_expression(self, expression: FaceExpression):
        """Set current face expression.
        
        Args:
            expression: Expression to display
        """
        self.current_expression = expression
        self.logger.info(f"Face expression: {expression.value}")
    
    def get_expression(self) -> FaceExpression:
        """Get current expression."""
        return self.current_expression
    
    def get_expression_emoji(self) -> str:
        """Get emoji representation of current expression.
        
        Returns:
            Emoji string
        """
        emoji_map = {
            FaceExpression.NEUTRAL: "😐",
            FaceExpression.HAPPY: "😀",
            FaceExpression.SAD: "😢",
            FaceExpression.ANGRY: "😠",
            FaceExpression.SURPRISED: "😮",
            FaceExpression.THINKING: "🤔",
            FaceExpression.SLEEPING: "😴",
            FaceExpression.CONFUSED: "😕"
        }
        return emoji_map.get(self.current_expression, "🤖")
    
    def get_svg_data(self, width: int = 200, height: int = 200) -> str:
        """Generate SVG data for current expression.
        
        Args:
            width: SVG width
            height: SVG height
            
        Returns:
            SVG XML string
        """
        # Simple SVG face generator
        svg = f'''<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">
'''
        
        # Face circle
        svg += f'''  <circle cx="{width//2}" cy="{height//2}" r="{min(width, height)//2 - 10}" 
                   fill="#FFD700" stroke="#FFA500" stroke-width="3"/>
'''
        
        # Eyes
        left_eye_x = width // 2 - 40
        right_eye_x = width // 2 + 40
        eye_y = height // 2 - 20
        
        if self.current_expression == FaceExpression.SLEEPING:
            # Closed eyes (lines)
            svg += f'''  <line x1="{left_eye_x - 10}" y1="{eye_y}" x2="{left_eye_x + 10}" y2="{eye_y}" 
                        stroke="#000" stroke-width="3"/>
'''
            svg += f'''  <line x1="{right_eye_x - 10}" y1="{eye_y}" x2="{right_eye_x + 10}" y2="{eye_y}" 
                        stroke="#000" stroke-width="3"/>
'''
        elif self.current_expression == FaceExpression.SURPRISED:
            # Wide eyes
            svg += f'''  <circle cx="{left_eye_x}" cy="{eye_y}" r="15" fill="#000"/>
'''
            svg += f'''  <circle cx="{right_eye_x}" cy="{eye_y}" r="15" fill="#000"/>
'''
        else:
            # Normal eyes
            svg += f'''  <circle cx="{left_eye_x}" cy="{eye_y}" r="10" fill="#000"/>
'''
            svg += f'''  <circle cx="{right_eye_x}" cy="{eye_y}" r="10" fill="#000"/>
'''
        
        # Mouth
        mouth_y = height // 2 + 30
        
        if self.current_expression == FaceExpression.HAPPY:
            # Smile
            svg += f'''  <path d="M {width//2 - 40} {mouth_y} Q {width//2} {mouth_y + 20} {width//2 + 40} {mouth_y}" 
                        stroke="#000" stroke-width="3" fill="none"/>
'''
        elif self.current_expression == FaceExpression.SAD:
            # Frown
            svg += f'''  <path d="M {width//2 - 40} {mouth_y + 10} Q {width//2} {mouth_y - 10} {width//2 + 40} {mouth_y + 10}" 
                        stroke="#000" stroke-width="3" fill="none"/>
'''
        elif self.current_expression == FaceExpression.SURPRISED:
            # O mouth
            svg += f'''  <circle cx="{width//2}" cy="{mouth_y}" r="15" fill="none" 
                        stroke="#000" stroke-width="3"/>
'''
        elif self.current_expression == FaceExpression.ANGRY:
            # Angry line
            svg += f'''  <line x1="{width//2 - 40}" y1="{mouth_y}" x2="{width//2 + 40}" y2="{mouth_y}" 
                        stroke="#000" stroke-width="4"/>
'''
            # Angry eyebrows
            svg += f'''  <line x1="{left_eye_x - 15}" y1="{eye_y - 15}" x2="{left_eye_x + 15}" y2="{eye_y - 20}" 
                        stroke="#000" stroke-width="3"/>
'''
            svg += f'''  <line x1="{right_eye_x - 15}" y1="{eye_y - 20}" x2="{right_eye_x + 15}" y2="{eye_y - 15}" 
                        stroke="#000" stroke-width="3"/>
'''
        else:
            # Neutral line
            svg += f'''  <line x1="{width//2 - 30}" y1="{mouth_y}" x2="{width//2 + 30}" y2="{mouth_y}" 
                        stroke="#000" stroke-width="3"/>
'''
        
        svg += '</svg>'
        return svg
    
    def start_animation(self):
        """Start face animation."""
        self.is_animating = True
    
    def stop_animation(self):
        """Stop face animation."""
        self.is_animating = False
