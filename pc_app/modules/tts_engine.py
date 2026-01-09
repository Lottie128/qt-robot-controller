"""Text-to-speech engine module.

Convert text responses to speech for robot voice.
"""

import logging
from typing import Optional
import threading

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    print("⚠️  pyttsx3 not available - install with: pip install pyttsx3")


class TTSEngine:
    """Text-to-speech engine."""
    
    def __init__(self):
        """Initialize TTS engine."""
        self.engine = None
        self.is_speaking = False
        self.logger = logging.getLogger(__name__)
        
        if PYTTSX3_AVAILABLE:
            self._init_tts()
        else:
            self.logger.warning("TTS not available")
    
    def _init_tts(self):
        """Initialize pyttsx3 engine."""
        try:
            self.engine = pyttsx3.init()
            
            # Set default properties
            self.engine.setProperty('rate', 150)    # Speed (words per minute)
            self.engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            # Try to use a good voice
            voices = self.engine.getProperty('voices')
            if voices:
                # Prefer female voice if available
                for voice in voices:
                    if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                        self.engine.setProperty('voice', voice.id)
                        break
            
            self.logger.info("✅ TTS engine initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize TTS: {e}")
            self.engine = None
    
    def is_available(self) -> bool:
        """Check if TTS is available."""
        return self.engine is not None
    
    def speak(self, text: str, wait: bool = False):
        """Speak text.
        
        Args:
            text: Text to speak
            wait: Wait for speech to complete before returning
        """
        if not self.is_available():
            self.logger.warning("TTS not available")
            return
        
        if not text:
            return
        
        try:
            self.is_speaking = True
            
            if wait:
                # Blocking speech
                self.engine.say(text)
                self.engine.runAndWait()
                self.is_speaking = False
            else:
                # Non-blocking speech in thread
                def speak_thread():
                    self.engine.say(text)
                    self.engine.runAndWait()
                    self.is_speaking = False
                
                thread = threading.Thread(target=speak_thread, daemon=True)
                thread.start()
            
            self.logger.info(f"🔊 Speaking: {text}")
        
        except Exception as e:
            self.logger.error(f"TTS error: {e}")
            self.is_speaking = False
    
    def stop(self):
        """Stop current speech."""
        if self.engine and self.is_speaking:
            try:
                self.engine.stop()
                self.is_speaking = False
                self.logger.info("Speech stopped")
            except Exception as e:
                self.logger.error(f"Failed to stop speech: {e}")
    
    def set_rate(self, rate: int):
        """Set speech rate.
        
        Args:
            rate: Words per minute (50-300)
        """
        if self.engine:
            rate = max(50, min(300, rate))
            self.engine.setProperty('rate', rate)
            self.logger.info(f"Speech rate set to {rate}")
    
    def set_volume(self, volume: float):
        """Set speech volume.
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            volume = max(0.0, min(1.0, volume))
            self.engine.setProperty('volume', volume)
            self.logger.info(f"Speech volume set to {volume}")
    
    def get_voices(self) -> list:
        """Get available voices.
        
        Returns:
            List of voice names
        """
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [voice.name for voice in voices]
        except:
            return []
    
    def set_voice(self, voice_id: str):
        """Set voice by ID.
        
        Args:
            voice_id: Voice identifier
        """
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
                self.logger.info(f"Voice changed to {voice_id}")
            except Exception as e:
                self.logger.error(f"Failed to set voice: {e}")
