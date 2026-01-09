"""Voice input module using speech recognition.

Captures and transcribes user voice commands.
"""

import logging
from typing import Optional, Callable
import threading

try:
    import speech_recognition as sr
    SR_AVAILABLE = True
except ImportError:
    SR_AVAILABLE = False
    print("⚠️  speech_recognition not available - install with: pip install SpeechRecognition")


class VoiceInput:
    """Voice input handler using speech recognition."""
    
    def __init__(self):
        """Initialize voice input."""
        self.recognizer = None
        self.microphone = None
        self.is_listening = False
        self.logger = logging.getLogger(__name__)
        
        # Callbacks
        self.on_speech_detected: Optional[Callable[[str], None]] = None
        self.on_error: Optional[Callable[[str], None]] = None
        
        if SR_AVAILABLE:
            self._init_speech_recognition()
        else:
            self.logger.warning("Speech recognition not available")
    
    def _init_speech_recognition(self):
        """Initialize speech recognition."""
        try:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
            
            # Adjust for ambient noise
            with self.microphone as source:
                self.logger.info("Calibrating microphone for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            self.logger.info("✅ Voice input initialized")
        
        except Exception as e:
            self.logger.error(f"Failed to initialize voice input: {e}")
            self.recognizer = None
    
    def is_available(self) -> bool:
        """Check if voice input is available."""
        return self.recognizer is not None and self.microphone is not None
    
    def listen_once(self, timeout: int = 5, phrase_time_limit: int = 10) -> Optional[str]:
        """Listen for a single voice command.
        
        Args:
            timeout: Seconds to wait for speech to start
            phrase_time_limit: Maximum seconds for phrase
            
        Returns:
            Transcribed text or None
        """
        if not self.is_available():
            self.logger.error("Voice input not available")
            return None
        
        try:
            with self.microphone as source:
                self.logger.info("🎤 Listening...")
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                self.logger.info("🔄 Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                
                self.logger.info(f"📝 Recognized: {text}")
                
                if self.on_speech_detected:
                    self.on_speech_detected(text)
                
                return text
        
        except sr.WaitTimeoutError:
            self.logger.warning("No speech detected (timeout)")
            if self.on_error:
                self.on_error("No speech detected")
            return None
        
        except sr.UnknownValueError:
            self.logger.warning("Could not understand speech")
            if self.on_error:
                self.on_error("Could not understand speech")
            return None
        
        except sr.RequestError as e:
            self.logger.error(f"Speech recognition service error: {e}")
            if self.on_error:
                self.on_error(f"Service error: {str(e)}")
            return None
        
        except Exception as e:
            self.logger.error(f"Voice input error: {e}")
            if self.on_error:
                self.on_error(f"Error: {str(e)}")
            return None
    
    def listen_continuous(self, callback: Callable[[str], None]):
        """Start continuous listening in background.
        
        Args:
            callback: Function to call with recognized text
        """
        if not self.is_available():
            self.logger.error("Voice input not available")
            return
        
        if self.is_listening:
            self.logger.warning("Already listening")
            return
        
        self.is_listening = True
        
        def listen_loop():
            while self.is_listening:
                text = self.listen_once()
                if text:
                    callback(text)
        
        thread = threading.Thread(target=listen_loop, daemon=True)
        thread.start()
        
        self.logger.info("Started continuous listening")
    
    def stop_listening(self):
        """Stop continuous listening."""
        self.is_listening = False
        self.logger.info("Stopped listening")
    
    def test_microphone(self) -> bool:
        """Test if microphone is working.
        
        Returns:
            True if microphone is accessible
        """
        if not SR_AVAILABLE:
            return False
        
        try:
            with sr.Microphone() as source:
                sr.Recognizer().adjust_for_ambient_noise(source, duration=0.5)
            return True
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            return False
