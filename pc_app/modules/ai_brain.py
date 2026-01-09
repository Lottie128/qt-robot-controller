"""AI brain using Google Gemini for natural language processing.

Processes voice commands and generates robot actions.
"""

import os
import logging
from typing import Dict, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class AIBrain:
    """AI command processor using Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI brain.
        
        Args:
            api_key: Google Gemini API key (or from env)
        """
        self.logger = logging.getLogger(__name__)
        self.model = None
        
        # Get API key
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if GEMINI_AVAILABLE and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel('gemini-pro')
                self.logger.info("✅ Gemini AI initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Gemini init failed: {e}")
        else:
            self.logger.warning("⚠️  Gemini not available")
    
    def is_available(self) -> bool:
        """Check if AI is available."""
        return self.model is not None
    
    async def process_command(self, text: str) -> Dict:
        """Process natural language command.
        
        Args:
            text: Command text
            
        Returns:
            Dictionary with response and action
        """
        if not self.is_available():
            return self._fallback_process(text)
        
        try:
            # Create prompt
            prompt = self._create_prompt(text)
            
            # Generate response
            response = await self.model.generate_content_async(prompt)
            
            # Parse response
            return self._parse_response(response.text)
        
        except Exception as e:
            self.logger.error(f"AI processing error: {e}")
            return {"response": "Sorry, I encountered an error.", "action": None}
    
    def _create_prompt(self, text: str) -> str:
        """Create prompt for Gemini."""
        return f"""You are a robot assistant. Interpret this command and respond with a JSON object.

Command: "{text}"

Respond ONLY with valid JSON in this exact format:
{{
    "response": "<friendly response to user>",
    "action": "<action name or null>",
    "speed": <0-100 or null>,
    "duration": <seconds or null>
}}

Valid actions: move_forward, move_backward, turn_left, turn_right, stop, null

Examples:
- "go forward" -> {{"response": "Moving forward!", "action": "move_forward", "speed": 70}}
- "turn left" -> {{"response": "Turning left", "action": "turn_left", "speed": 50}}
- "hello" -> {{"response": "Hello! How can I help you?", "action": null}}
"""
    
    def _parse_response(self, text: str) -> Dict:
        """Parse Gemini response."""
        import json
        try:
            # Extract JSON from response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = text[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {"response": text, "action": None}
    
    def _fallback_process(self, text: str) -> Dict:
        """Simple rule-based fallback."""
        text_lower = text.lower()
        
        # Movement commands
        if any(word in text_lower for word in ['forward', 'ahead', 'front']):
            return {"response": "Moving forward", "action": "move_forward", "speed": 70}
        elif any(word in text_lower for word in ['backward', 'back', 'reverse']):
            return {"response": "Moving backward", "action": "move_backward", "speed": 70}
        elif 'left' in text_lower:
            return {"response": "Turning left", "action": "turn_left", "speed": 50}
        elif 'right' in text_lower:
            return {"response": "Turning right", "action": "turn_right", "speed": 50}
        elif 'stop' in text_lower:
            return {"response": "Stopping", "action": "stop"}
        else:
            return {"response": "I didn't understand that command", "action": None}
