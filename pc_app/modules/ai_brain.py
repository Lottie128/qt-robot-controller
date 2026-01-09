"""AI Brain module using Google Gemini API.

Handles natural language processing and intelligent responses.
"""

import os
import logging
from typing import Optional, List, Dict
import json

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️  google-generativeai not available - install with: pip install google-generativeai")


class AIBrain:
    """AI brain for robot using Google Gemini."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI brain.
        
        Args:
            api_key: Google Gemini API key (or use GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.model = None
        self.chat = None
        self.conversation_history: List[Dict] = []
        self.logger = logging.getLogger(__name__)
        
        if GEMINI_AVAILABLE and self.api_key:
            self._init_gemini()
        elif not GEMINI_AVAILABLE:
            self.logger.warning("Gemini API not available")
        else:
            self.logger.warning("No API key provided - AI features disabled")
    
    def _init_gemini(self):
        """Initialize Gemini API."""
        try:
            genai.configure(api_key=self.api_key)
            
            # Use Gemini 1.5 Flash for fast responses
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            
            # Start chat with robot context
            system_prompt = (
                "You are an AI assistant for a robot controller. "
                "You help users control their robot through natural language commands. "
                "Parse commands like 'move forward', 'turn left', 'stop', etc. "
                "Be concise and helpful. When you understand a command, "
                "respond with the action to take."
            )
            
            self.chat = self.model.start_chat(history=[])
            self.logger.info("✅ Gemini AI initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize Gemini: {e}")
            self.model = None
    
    def is_available(self) -> bool:
        """Check if AI is available."""
        return self.model is not None
    
    async def process_command(self, user_input: str) -> Dict[str, any]:
        """Process natural language command.
        
        Args:
            user_input: User's voice or text input
            
        Returns:
            Dictionary with action and parameters
        """
        if not self.is_available():
            return {
                "error": "AI not available",
                "response": "AI features are not enabled"
            }
        
        try:
            # Add command parsing instruction
            prompt = (
                f"User command: '{user_input}'\n\n"
                "Parse this command and respond with JSON in this format:\n"
                "{\n"
                '  "action": "move_forward|move_backward|turn_left|turn_right|stop|unknown",\n'
                '  "speed": 70,  // optional, 0-100\n'
                '  "duration": 2.0,  // optional, seconds\n'
                '  "response": "Human-friendly response"\n'
                "}"
            )
            
            response = self.chat.send_message(prompt)
            response_text = response.text
            
            # Try to extract JSON
            try:
                # Remove markdown code blocks if present
                if "```json" in response_text:
                    response_text = response_text.split("```json")[1].split("```")[0]
                elif "```" in response_text:
                    response_text = response_text.split("```")[1].split("```")[0]
                
                result = json.loads(response_text.strip())
                
                # Store in history
                self.conversation_history.append({
                    "user": user_input,
                    "ai": result.get("response", "")
                })
                
                return result
            
            except json.JSONDecodeError:
                # Fallback: simple keyword matching
                return self._fallback_parse(user_input, response_text)
        
        except Exception as e:
            self.logger.error(f"AI processing error: {e}")
            return {
                "action": "unknown",
                "error": str(e),
                "response": "Sorry, I couldn't process that command."
            }
    
    def _fallback_parse(self, user_input: str, ai_response: str) -> Dict:
        """Fallback command parsing using keywords."""
        text = user_input.lower()
        
        # Simple keyword matching
        if "forward" in text or "ahead" in text or "go" in text:
            return {"action": "move_forward", "speed": 70, "response": ai_response}
        elif "backward" in text or "back" in text or "reverse" in text:
            return {"action": "move_backward", "speed": 70, "response": ai_response}
        elif "left" in text:
            return {"action": "turn_left", "speed": 50, "response": ai_response}
        elif "right" in text:
            return {"action": "turn_right", "speed": 50, "response": ai_response}
        elif "stop" in text or "halt" in text:
            return {"action": "stop", "response": ai_response}
        else:
            return {"action": "unknown", "response": ai_response}
    
    async def chat_conversation(self, message: str) -> str:
        """Have a conversation (not command-focused).
        
        Args:
            message: User message
            
        Returns:
            AI response
        """
        if not self.is_available():
            return "AI not available"
        
        try:
            response = self.chat.send_message(message)
            response_text = response.text
            
            # Store in history
            self.conversation_history.append({
                "user": message,
                "ai": response_text
            })
            
            return response_text
        
        except Exception as e:
            self.logger.error(f"Chat error: {e}")
            return f"Sorry, I encountered an error: {str(e)}"
    
    def get_conversation_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
        if self.model:
            self.chat = self.model.start_chat(history=[])
