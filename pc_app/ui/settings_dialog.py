"""Settings dialog for application configuration.

Allows user to configure GPIO pins, camera, sensors, and app settings.
"""

import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
        QLineEdit, QPushButton, QGroupBox, QTabWidget,
        QWidget, QSpinBox, QCheckBox, QComboBox,
        QMessageBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️  PyQt6 not available")


if PYQT_AVAILABLE:
    class SettingsDialog(QDialog):
        """Application settings dialog."""
        
        # Signal emitted when settings are saved
        settings_changed = pyqtSignal(dict)
        
        def __init__(self, parent=None, current_config=None):
            """Initialize settings dialog.
            
            Args:
                parent: Parent widget
                current_config: Current configuration dictionary
            """
            super().__init__(parent)
            self.setWindowTitle("Settings")
            self.setModal(True)
            self.resize(600, 500)
            
            self.current_config = current_config or {}
            
            self._init_ui()
            self._load_config()
        
        def _init_ui(self):
            """Initialize user interface."""
            layout = QVBoxLayout()
            
            # Tab widget
            tabs = QTabWidget()
            
            # GPIO tab
            gpio_tab = self._create_gpio_tab()
            tabs.addTab(gpio_tab, "🔌 GPIO Configuration")
            
            # Camera tab
            camera_tab = self._create_camera_tab()
            tabs.addTab(camera_tab, "📷 Camera Settings")
            
            # Control tab
            control_tab = self._create_control_tab()
            tabs.addTab(control_tab, "🎮 Control Settings")
            
            # Voice/AI tab
            ai_tab = self._create_ai_tab()
            tabs.addTab(ai_tab, "🧠 AI & Voice")
            
            layout.addWidget(tabs)
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            save_btn = QPushButton("Save & Apply")
            save_btn.clicked.connect(self._on_save)
            button_layout.addWidget(save_btn)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
        
        def _create_gpio_tab(self) -> QWidget:
            """Create GPIO configuration tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Motor pins group
            motor_group = QGroupBox("Motor Driver Pins (BOARD Mode)")
            motor_layout = QVBoxLayout()
            
            # Left motor
            left_layout = QHBoxLayout()
            left_layout.addWidget(QLabel("Left Motor Forward (L1):"))
            self.l1_spin = QSpinBox()
            self.l1_spin.setRange(1, 40)
            self.l1_spin.setValue(33)
            left_layout.addWidget(self.l1_spin)
            left_layout.addWidget(QLabel("Backward (L2):"))
            self.l2_spin = QSpinBox()
            self.l2_spin.setRange(1, 40)
            self.l2_spin.setValue(38)
            left_layout.addWidget(self.l2_spin)
            left_layout.addStretch()
            motor_layout.addLayout(left_layout)
            
            # Right motor
            right_layout = QHBoxLayout()
            right_layout.addWidget(QLabel("Right Motor Forward (R1):"))
            self.r1_spin = QSpinBox()
            self.r1_spin.setRange(1, 40)
            self.r1_spin.setValue(35)
            right_layout.addWidget(self.r1_spin)
            right_layout.addWidget(QLabel("Backward (R2):"))
            self.r2_spin = QSpinBox()
            self.r2_spin.setRange(1, 40)
            self.r2_spin.setValue(40)
            right_layout.addWidget(self.r2_spin)
            right_layout.addStretch()
            motor_layout.addLayout(right_layout)
            
            motor_group.setLayout(motor_layout)
            layout.addWidget(motor_group)
            
            # Sensor pins group
            sensor_group = QGroupBox("Sensor Pins")
            sensor_layout = QVBoxLayout()
            
            ultrasonic_layout = QHBoxLayout()
            ultrasonic_layout.addWidget(QLabel("Ultrasonic Trigger:"))
            self.trigger_spin = QSpinBox()
            self.trigger_spin.setRange(1, 40)
            self.trigger_spin.setValue(11)
            ultrasonic_layout.addWidget(self.trigger_spin)
            ultrasonic_layout.addWidget(QLabel("Echo:"))
            self.echo_spin = QSpinBox()
            self.echo_spin.setRange(1, 40)
            self.echo_spin.setValue(13)
            ultrasonic_layout.addWidget(self.echo_spin)
            ultrasonic_layout.addStretch()
            sensor_layout.addLayout(ultrasonic_layout)
            
            sensor_group.setLayout(sensor_layout)
            layout.addWidget(sensor_group)
            
            # Info label
            info = QLabel(
                "⚠️  Changes will be sent to the robot when you click Save & Apply"
            )
            info.setWordWrap(True)
            info.setStyleSheet("color: orange; padding: 10px;")
            layout.addWidget(info)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_camera_tab(self) -> QWidget:
            """Create camera settings tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            camera_group = QGroupBox("Camera Settings")
            camera_layout = QVBoxLayout()
            
            # Resolution
            res_layout = QHBoxLayout()
            res_layout.addWidget(QLabel("Resolution:"))
            self.width_spin = QSpinBox()
            self.width_spin.setRange(160, 1920)
            self.width_spin.setValue(640)
            res_layout.addWidget(self.width_spin)
            res_layout.addWidget(QLabel("x"))
            self.height_spin = QSpinBox()
            self.height_spin.setRange(120, 1080)
            self.height_spin.setValue(480)
            res_layout.addWidget(self.height_spin)
            res_layout.addStretch()
            camera_layout.addLayout(res_layout)
            
            # FPS
            fps_layout = QHBoxLayout()
            fps_layout.addWidget(QLabel("Frame Rate:"))
            self.fps_spin = QSpinBox()
            self.fps_spin.setRange(5, 60)
            self.fps_spin.setValue(30)
            fps_layout.addWidget(self.fps_spin)
            fps_layout.addWidget(QLabel("FPS"))
            fps_layout.addStretch()
            camera_layout.addLayout(fps_layout)
            
            # Quality
            quality_layout = QHBoxLayout()
            quality_layout.addWidget(QLabel("JPEG Quality:"))
            self.quality_spin = QSpinBox()
            self.quality_spin.setRange(10, 100)
            self.quality_spin.setValue(80)
            quality_layout.addWidget(self.quality_spin)
            quality_layout.addWidget(QLabel("%"))
            quality_layout.addStretch()
            camera_layout.addLayout(quality_layout)
            
            camera_group.setLayout(camera_layout)
            layout.addWidget(camera_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_control_tab(self) -> QWidget:
            """Create control settings tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            control_group = QGroupBox("Control Settings")
            control_layout = QVBoxLayout()
            
            # Default speed
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Default Speed:"))
            self.speed_spin = QSpinBox()
            self.speed_spin.setRange(0, 100)
            self.speed_spin.setValue(70)
            speed_layout.addWidget(self.speed_spin)
            speed_layout.addWidget(QLabel("%"))
            speed_layout.addStretch()
            control_layout.addLayout(speed_layout)
            
            # Turn speed
            turn_layout = QHBoxLayout()
            turn_layout.addWidget(QLabel("Turn Speed:"))
            self.turn_spin = QSpinBox()
            self.turn_spin.setRange(0, 100)
            self.turn_spin.setValue(50)
            turn_layout.addWidget(self.turn_spin)
            turn_layout.addWidget(QLabel("%"))
            turn_layout.addStretch()
            control_layout.addLayout(turn_layout)
            
            # Keyboard control
            self.keyboard_check = QCheckBox("Enable Keyboard Control")
            self.keyboard_check.setChecked(True)
            control_layout.addWidget(self.keyboard_check)
            
            control_group.setLayout(control_layout)
            layout.addWidget(control_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_ai_tab(self) -> QWidget:
            """Create AI and voice settings tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Voice settings
            voice_group = QGroupBox("Voice Recognition")
            voice_layout = QVBoxLayout()
            
            self.voice_check = QCheckBox("Enable Voice Input")
            self.voice_check.setChecked(True)
            voice_layout.addWidget(self.voice_check)
            
            voice_group.setLayout(voice_layout)
            layout.addWidget(voice_group)
            
            # AI settings
            ai_group = QGroupBox("AI Assistant")
            ai_layout = QVBoxLayout()
            
            self.ai_check = QCheckBox("Enable AI (Gemini)")
            self.ai_check.setChecked(True)
            ai_layout.addWidget(self.ai_check)
            
            ai_group.setLayout(ai_layout)
            layout.addWidget(ai_group)
            
            # TTS settings
            tts_group = QGroupBox("Text-to-Speech")
            tts_layout = QVBoxLayout()
            
            self.tts_check = QCheckBox("Enable TTS")
            self.tts_check.setChecked(True)
            tts_layout.addWidget(self.tts_check)
            
            self.auto_speak_check = QCheckBox("Auto-speak AI responses")
            self.auto_speak_check.setChecked(False)
            tts_layout.addWidget(self.auto_speak_check)
            
            tts_group.setLayout(tts_layout)
            layout.addWidget(tts_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _load_config(self):
            """Load configuration into UI elements."""
            if not self.current_config:
                return
            
            # Load GPIO config
            motors = self.current_config.get("motors", {})
            pins = motors.get("pins", {})
            self.l1_spin.setValue(pins.get("L1", 33))
            self.l2_spin.setValue(pins.get("L2", 38))
            self.r1_spin.setValue(pins.get("R1", 35))
            self.r2_spin.setValue(pins.get("R2", 40))
            
            # Load camera config
            camera = self.current_config.get("camera", {})
            self.width_spin.setValue(camera.get("width", 640))
            self.height_spin.setValue(camera.get("height", 480))
            self.fps_spin.setValue(camera.get("fps", 30))
            self.quality_spin.setValue(camera.get("stream_quality", 80))
        
        def _on_save(self):
            """Handle save button click."""
            config = {
                "motors": {
                    "pin_mode": "BOARD",
                    "pins": {
                        "L1": self.l1_spin.value(),
                        "L2": self.l2_spin.value(),
                        "R1": self.r1_spin.value(),
                        "R2": self.r2_spin.value()
                    },
                    "default_speed": self.speed_spin.value(),
                    "turn_speed": self.turn_spin.value()
                },
                "camera": {
                    "width": self.width_spin.value(),
                    "height": self.height_spin.value(),
                    "fps": self.fps_spin.value(),
                    "stream_quality": self.quality_spin.value()
                },
                "ultrasonic": {
                    "trigger_pin": self.trigger_spin.value(),
                    "echo_pin": self.echo_spin.value()
                },
                "ui": {
                    "keyboard_enabled": self.keyboard_check.isChecked(),
                    "voice_enabled": self.voice_check.isChecked(),
                    "ai_enabled": self.ai_check.isChecked(),
                    "tts_enabled": self.tts_check.isChecked(),
                    "auto_speak": self.auto_speak_check.isChecked()
                }
            }
            
            self.settings_changed.emit(config)
            self.accept()
            
            QMessageBox.information(
                self,
                "Settings Saved",
                "Settings have been saved and will be applied to the robot."
            )
else:
    # Fallback
    class SettingsDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyQt6 is required for GUI")
