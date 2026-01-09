"""Face animator for robot expressions.

Simple emoji-based face animation.
"""

import random
from enum import Enum


class FaceExpression(Enum):
    """Face expressions."""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    SURPRISED = "surprised"
    THINKING = "thinking"
    SLEEPING = "sleeping"
    ANGRY = "angry"
    CONFUSED = "confused"


class FaceAnimator:
    """Simple face animation with emojis."""
    
    # Expression to emoji mapping
    EXPRESSIONS = {
        FaceExpression.NEUTRAL: "🤖",
        FaceExpression.HAPPY: "😊",
        FaceExpression.SAD: "☹️",
        FaceExpression.SURPRISED: "😮",
        FaceExpression.THINKING: "🤔",
        FaceExpression.SLEEPING: "😴",
        FaceExpression.ANGRY: "😠",
        FaceExpression.CONFUSED: "😕"
    }
    
    def __init__(self):
        """Initialize face animator."""
        self.current_expression = FaceExpression.NEUTRAL
        self.blink_counter = 0
    
    def set_expression(self, expression: FaceExpression):
        """Set face expression.
        
        Args:
            expression: Expression to display
        """
        self.current_expression = expression
    
    def get_expression(self) -> FaceExpression:
        """Get current expression."""
        return self.current_expression
    
    def get_expression_emoji(self) -> str:
        """Get emoji for current expression."""
        return self.EXPRESSIONS.get(self.current_expression, "🤖")
    
    def update(self):
        """Update animation (call periodically)."""
        # Blink occasionally
        self.blink_counter += 1
        if self.blink_counter >= 30:  # Every ~3 seconds at 10Hz
            self.blink_counter = 0
            # TODO: Add blink animation
    
    def random_expression(self):
        """Set random expression."""
        expressions = list(FaceExpression)
        self.current_expression = random.choice(expressions)
