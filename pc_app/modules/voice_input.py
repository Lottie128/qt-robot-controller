"""Voice input module using speech recognition.

Captures and transcribes voice commands.
"""

import logging
from typing import Optional, Callable

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False


class VoiceInput:
    """Voice input handler."""
    
    def __init__(self):
        """Initialize voice input."""
        self.logger = logging.getLogger(__name__)
        self.recognizer = None
        self.microphone = None
        
        # Callback
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        
        if SR_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                self.logger.info("✅ Voice input initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Voice input init failed: {e}")
        else:
            self.logger.warning("⚠️  speech_recognition not available")
    
    def is_available(self) -> bool:
        """Check if voice input is available."""
        return self.recognizer is not None and self.microphone is not None
    
    def listen_once(self, timeout: int = 5) -> Optional[str]:
        """Listen for single voice command.
        
        Args:
            timeout: Listen timeout in seconds
            
        Returns:
            Transcribed text or None
        """
        if not self.is_available():
            return None
        
        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.logger.info("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen
                audio = self.recognizer.listen(source, timeout=timeout)
                
                # Recognize
                self.logger.info("🔍 Recognizing...")
                text = self.recognizer.recognize_google(audio)
                
                self.logger.info(f"📝 Recognized: {text}")
                
                if self.on_speech_detected:
                    self.on_speech_detected(text)
                
                return text
        
        except sr.WaitTimeoutError:
            self.logger.warning("⏱️  Listening timeout")
            return None
        except sr.UnknownValueError:
            self.logger.warning("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            self.logger.error(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            self.logger.error(f"❌ Voice input error: {e}")
            return None
    
    def start_continuous(self, callback: Callable[[str], None]):
        """Start continuous listening (background thread).
        
        Args:
            callback: Function called with recognized text
        """
        if not self.is_available():
            return
        
        def listen_callback(recognizer, audio):
            try:
                text = recognizer.recognize_google(audio)
                callback(text)
            except:
                pass
        
        # Start background listening
        self.stop_listening = self.recognizer.listen_in_background(
            self.microphone, 
            listen_callback
        )
        
        self.logger.info("🎤 Continuous listening started")
    
    def stop_continuous(self):
        """Stop continuous listening."""
        if hasattr(self, 'stop_listening'):
            self.stop_listening(wait_for_stop=False)
            self.logger.info("⏹️  Continuous listening stopped")
