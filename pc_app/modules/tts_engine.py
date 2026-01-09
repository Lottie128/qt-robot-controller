"""Text-to-speech engine.

Converts text to speech for robot responses.
"""

import logging
from typing import Optional

try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False


class TTSEngine:
    """Text-to-speech handler."""
    
    def __init__(self):
        """Initialize TTS engine."""
        self.logger = logging.getLogger(__name__)
        self.engine = None
        
        if TTS_AVAILABLE:
            try:
                self.engine = pyttsx3.init()
                
                # Configure voice
                self.engine.setProperty('rate', 150)  # Speed
                self.engine.setProperty('volume', 0.9)  # Volume
                
                # Use female voice if available
                voices = self.engine.getProperty('voices')
                for voice in voices:
                    if 'female' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
                
                self.logger.info("✅ TTS engine initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  TTS init failed: {e}")
        else:
            self.logger.warning("⚠️  pyttsx3 not available")
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None
    
    def speak(self, text: str, wait: bool = False):
        """Speak text.
        
        Args:
            text: Text to speak
            wait: Wait for speech to complete
        """
        if not self.is_available():
            self.logger.warning("TTS not available")
            return
        
        try:
            self.logger.info(f"🔊 Speaking: {text}")
            self.engine.say(text)
            
            if wait:
                self.engine.runAndWait()
            else:
                # Non-blocking
                import threading
                threading.Thread(target=self.engine.runAndWait, daemon=True).start()
        
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
    
    def set_rate(self, rate: int):
        """Set speech rate.
        
        Args:
            rate: Words per minute (50-300)
        """
        if self.engine:
            self.engine.setProperty('rate', rate)
    
    def set_volume(self, volume: float):
        """Set volume.
        
        Args:
            volume: Volume level (0.0-1.0)
        """
        if self.engine:
            self.engine.setProperty('volume', volume)
    
    def stop(self):
        """Stop current speech."""
        if self.engine:
            self.engine.stop()
