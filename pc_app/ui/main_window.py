"""Main window for Qt Robot Controller application.

Comprehensive GUI with video feed, controls, chat, sensors, and more.
"""

import sys
import asyncio
import logging
from pathlib import Path
from typing import Optional

try:
    from PyQt6.QtWidgets import (
        QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QPushButton, QLabel, QTextEdit, QLineEdit, QSlider,
        QGroupBox, QTabWidget, QStatusBar, QMenuBar, QMenu,
        QMessageBox, QSplitter, QFrame
    )
    from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
    from PyQt6.QtGui import QAction, QKeySequence, QPixmap, QImage
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️  PyQt6 not available")

sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.protocol import MessageType

# Import modules
sys.path.append(str(Path(__file__).parent.parent))
from modules.network_client import RobotClient
from modules.ai_brain import AIBrain
from modules.voice_input import VoiceInput
from modules.tts_engine import TTSEngine
from modules.face_animator import FaceAnimator, FaceExpression
from modules.vision_processor import VisionProcessor

from ui.login_dialog import LoginDialog
from ui.settings_dialog import SettingsDialog


if PYQT_AVAILABLE:
    class MainWindow(QMainWindow):
        """Main application window."""
        
        def __init__(self):
            """Initialize main window."""
            super().__init__()
            self.setWindowTitle("🤖 Qt Robot Controller")
            self.resize(1200, 800)
            
            # Setup logging
            self.logger = logging.getLogger(__name__)
            
            # Initialize modules
            self.client = RobotClient()
            self.ai_brain = AIBrain()
            self.voice_input = VoiceInput()
            self.tts_engine = TTSEngine()
            self.face_animator = FaceAnimator()
            self.vision_processor = VisionProcessor()
            
            # Connection state
            self.connected = False
            self.robot_ip = ""
            self.robot_port = 0
            
            # Control state
            self.current_speed = 70
            self.keyboard_enabled = True
            
            # Video state
            self.video_active = False
            self.current_frame = None
            
            # Setup client callbacks
            self._setup_callbacks()
            
            # Create UI
            self._init_ui()
            self._init_menu()
            
            # Setup update timer
            self.update_timer = QTimer()
            self.update_timer.timeout.connect(self._update_ui)
            self.update_timer.start(100)  # 10 FPS UI update
            
            # Show connection dialog on start
            QTimer.singleShot(500, self._show_connect_dialog)
        
        def _setup_callbacks(self):
            """Setup network client callbacks."""
            self.client.on_connected = self._on_connected
            self.client.on_disconnected = self._on_disconnected
            self.client.on_message = self._on_message_received
            self.client.on_error = self._on_error
            
            # Voice callback
            if self.voice_input.is_available():
                self.voice_input.on_speech_detected = self._on_speech_detected
        
        def _init_ui(self):
            """Initialize user interface."""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # Main layout
            main_layout = QHBoxLayout()
            
            # Left panel (video + face)
            left_panel = self._create_left_panel()
            main_layout.addWidget(left_panel, stretch=2)
            
            # Right panel (controls + chat)
            right_panel = self._create_right_panel()
            main_layout.addWidget(right_panel, stretch=1)
            
            central_widget.setLayout(main_layout)
            
            # Status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)
            self.status_bar.showMessage("⚪ Disconnected")
        
        def _init_menu(self):
            """Initialize menu bar."""
            menubar = self.menuBar()
            
            # File menu
            file_menu = menubar.addMenu("&File")
            
            connect_action = QAction("🔌 &Connect", self)
            connect_action.setShortcut(QKeySequence("Ctrl+N"))
            connect_action.triggered.connect(self._show_connect_dialog)
            file_menu.addAction(connect_action)
            
            disconnect_action = QAction("❌ &Disconnect", self)
            disconnect_action.setShortcut(QKeySequence("Ctrl+D"))
            disconnect_action.triggered.connect(self._disconnect)
            file_menu.addAction(disconnect_action)
            
            file_menu.addSeparator()
            
            exit_action = QAction("E&xit", self)
            exit_action.setShortcut(QKeySequence("Ctrl+Q"))
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # Robot menu
            robot_menu = menubar.addMenu("&Robot")
            
            camera_action = QAction("📷 Start &Camera", self)
            camera_action.triggered.connect(self._toggle_camera)
            robot_menu.addAction(camera_action)
            
            lidar_action = QAction("📍 Start &LiDAR", self)
            lidar_action.triggered.connect(self._toggle_lidar)
            robot_menu.addAction(lidar_action)
            
            robot_menu.addSeparator()
            
            settings_action = QAction("⚙️  &Settings", self)
            settings_action.setShortcut(QKeySequence("Ctrl+,"))
            settings_action.triggered.connect(self._show_settings)
            robot_menu.addAction(settings_action)
            
            # Help menu
            help_menu = menubar.addMenu("&Help")
            
            about_action = QAction("&About", self)
            about_action.triggered.connect(self._show_about)
            help_menu.addAction(about_action)
        
        def _create_left_panel(self) -> QWidget:
            """Create left panel with video and face."""
            panel = QWidget()
            layout = QVBoxLayout()
            
            # Video feed
            video_group = QGroupBox("📹 Camera Feed")
            video_layout = QVBoxLayout()
            
            self.video_label = QLabel("No video feed")
            self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.video_label.setMinimumSize(640, 480)
            self.video_label.setStyleSheet("background-color: #000; color: #888; font-size: 16px;")
            video_layout.addWidget(self.video_label)
            
            # Video controls
            video_controls = QHBoxLayout()
            self.camera_btn = QPushButton("📷 Start Camera")
            self.camera_btn.clicked.connect(self._toggle_camera)
            video_controls.addWidget(self.camera_btn)
            
            self.snapshot_btn = QPushButton("📸 Snapshot")
            self.snapshot_btn.setEnabled(False)
            video_controls.addWidget(self.snapshot_btn)
            
            video_layout.addLayout(video_controls)
            video_group.setLayout(video_layout)
            layout.addWidget(video_group, stretch=3)
            
            # Robot face
            face_group = QGroupBox("🤖 Robot Face")
            face_layout = QVBoxLayout()
            
            self.face_label = QLabel(self.face_animator.get_expression_emoji())
            self.face_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.face_label.setStyleSheet("font-size: 100px;")
            face_layout.addWidget(self.face_label)
            
            face_group.setLayout(face_layout)
            layout.addWidget(face_group, stretch=1)
            
            panel.setLayout(layout)
            return panel
        
        def _create_right_panel(self) -> QWidget:
            """Create right panel with controls and chat."""
            panel = QWidget()
            layout = QVBoxLayout()
            
            # Tab widget
            tabs = QTabWidget()
            
            # Control tab
            control_tab = self._create_control_tab()
            tabs.addTab(control_tab, "🎮 Control")
            
            # Chat tab
            chat_tab = self._create_chat_tab()
            tabs.addTab(chat_tab, "💬 Chat")
            
            # Sensors tab
            sensors_tab = self._create_sensors_tab()
            tabs.addTab(sensors_tab, "📊 Sensors")
            
            layout.addWidget(tabs)
            panel.setLayout(layout)
            return panel
        
        def _create_control_tab(self) -> QWidget:
            """Create control tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Movement controls
            movement_group = QGroupBox("➡️  Movement Controls")
            movement_layout = QVBoxLayout()
            
            # Direction buttons
            btn_layout = QVBoxLayout()
            
            # Forward
            forward_row = QHBoxLayout()
            forward_row.addStretch()
            self.forward_btn = QPushButton("⬆️  Forward")
            self.forward_btn.pressed.connect(lambda: self._move_forward())
            self.forward_btn.released.connect(lambda: self._stop())
            forward_row.addWidget(self.forward_btn)
            forward_row.addStretch()
            btn_layout.addLayout(forward_row)
            
            # Left, Stop, Right
            middle_row = QHBoxLayout()
            self.left_btn = QPushButton("⬅️  Left")
            self.left_btn.pressed.connect(lambda: self._turn_left())
            self.left_btn.released.connect(lambda: self._stop())
            middle_row.addWidget(self.left_btn)
            
            self.stop_btn = QPushButton("🛑 STOP")
            self.stop_btn.clicked.connect(self._stop)
            self.stop_btn.setStyleSheet("background-color: #d32f2f; color: white; font-weight: bold;")
            middle_row.addWidget(self.stop_btn)
            
            self.right_btn = QPushButton("➡️  Right")
            self.right_btn.pressed.connect(lambda: self._turn_right())
            self.right_btn.released.connect(lambda: self._stop())
            middle_row.addWidget(self.right_btn)
            
            btn_layout.addLayout(middle_row)
            
            # Backward
            backward_row = QHBoxLayout()
            backward_row.addStretch()
            self.backward_btn = QPushButton("⬇️  Backward")
            self.backward_btn.pressed.connect(lambda: self._move_backward())
            self.backward_btn.released.connect(lambda: self._stop())
            backward_row.addWidget(self.backward_btn)
            backward_row.addStretch()
            btn_layout.addLayout(backward_row)
            
            movement_layout.addLayout(btn_layout)
            
            # Speed slider
            speed_layout = QHBoxLayout()
            speed_layout.addWidget(QLabel("Speed:"))
            self.speed_slider = QSlider(Qt.Orientation.Horizontal)
            self.speed_slider.setRange(0, 100)
            self.speed_slider.setValue(70)
            self.speed_slider.valueChanged.connect(self._on_speed_changed)
            speed_layout.addWidget(self.speed_slider)
            self.speed_label = QLabel("70%")
            self.speed_label.setFixedWidth(40)
            speed_layout.addWidget(self.speed_label)
            movement_layout.addLayout(speed_layout)
            
            movement_group.setLayout(movement_layout)
            layout.addWidget(movement_group)
            
            # Quick actions
            actions_group = QGroupBox("⚡ Quick Actions")
            actions_layout = QVBoxLayout()
            
            lidar_btn = QPushButton("📍 Toggle LiDAR")
            lidar_btn.clicked.connect(self._toggle_lidar)
            actions_layout.addWidget(lidar_btn)
            
            actions_group.setLayout(actions_layout)
            layout.addWidget(actions_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_chat_tab(self) -> QWidget:
            """Create chat/AI tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Chat history
            self.chat_display = QTextEdit()
            self.chat_display.setReadOnly(True)
            self.chat_display.setStyleSheet("background-color: #1e1e1e; color: #e0e0e0;")
            layout.addWidget(self.chat_display)
            
            # Input area
            input_layout = QHBoxLayout()
            
            self.chat_input = QLineEdit()
            self.chat_input.setPlaceholderText("Type a command or message...")
            self.chat_input.returnPressed.connect(self._send_chat_message)
            input_layout.addWidget(self.chat_input)
            
            send_btn = QPushButton("➡️  Send")
            send_btn.clicked.connect(self._send_chat_message)
            input_layout.addWidget(send_btn)
            
            layout.addLayout(input_layout)
            
            # Voice button
            voice_layout = QHBoxLayout()
            self.voice_btn = QPushButton("🎤 Voice Command")
            self.voice_btn.clicked.connect(self._voice_command)
            voice_layout.addWidget(self.voice_btn)
            
            speak_btn = QPushButton("🔊 Speak Response")
            speak_btn.clicked.connect(self._test_tts)
            voice_layout.addWidget(speak_btn)
            
            layout.addLayout(voice_layout)
            
            tab.setLayout(layout)
            return tab
        
        def _create_sensors_tab(self) -> QWidget:
            """Create sensors tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Sensor display
            sensors_group = QGroupBox("📊 Sensor Data")
            sensors_layout = QVBoxLayout()
            
            self.sensor_display = QTextEdit()
            self.sensor_display.setReadOnly(True)
            self.sensor_display.setMaximumHeight(200)
            sensors_layout.addWidget(self.sensor_display)
            
            sensors_group.setLayout(sensors_layout)
            layout.addWidget(sensors_group)
            
            # Console
            console_group = QGroupBox("📝 Console Log")
            console_layout = QVBoxLayout()
            
            self.console_display = QTextEdit()
            self.console_display.setReadOnly(True)
            self.console_display.setStyleSheet("background-color: #000; color: #0f0; font-family: monospace;")
            console_layout.addWidget(self.console_display)
            
            console_group.setLayout(console_layout)
            layout.addWidget(console_group)
            
            tab.setLayout(layout)
            return tab
        
        # Event handlers
        def _show_connect_dialog(self):
            """Show connection dialog."""
            dialog = LoginDialog(self)
            dialog.connect_requested.connect(self._connect_to_robot)
            dialog.exec()
        
        def _connect_to_robot(self, ip: str, port: int):
            """Connect to robot."""
            self.robot_ip = ip
            self.robot_port = port
            self._log(f"Connecting to {ip}:{port}...")
            
            # Use asyncio event loop
            asyncio.create_task(self._async_connect(ip, port))
        
        async def _async_connect(self, ip: str, port: int):
            """Async connect to robot."""
            success = await self.client.connect(ip, port)
            if not success:
                self._log("❌ Connection failed")
        
        def _disconnect(self):
            """Disconnect from robot."""
            if self.connected:
                asyncio.create_task(self.client.disconnect())
        
        def _on_connected(self):
            """Handle connection established."""
            self.connected = True
            self.status_bar.showMessage(f"✅ Connected to {self.robot_ip}:{self.robot_port}")
            self.status_bar.setStyleSheet("color: green;")
            self._log(f"✅ Connected to robot")
        
        def _on_disconnected(self):
            """Handle disconnection."""
            self.connected = False
            self.status_bar.showMessage("⚪ Disconnected")
            self.status_bar.setStyleSheet("")
            self._log("⚪ Disconnected from robot")
        
        def _on_message_received(self, message: dict):
            """Handle message from robot."""
            msg_type = message.get("type")
            data = message.get("data", {})
            
            # Handle different message types
            if msg_type == "sensor_data":
                self._update_sensors(data)
            elif msg_type == "camera_frame":
                self._update_video(data)
            elif msg_type == "status":
                status = data.get("message", "")
                self._log(f"🤖 Robot: {status}")
        
        def _on_error(self, error: str):
            """Handle error."""
            self._log(f"❌ Error: {error}")
        
        # Movement commands
        def _move_forward(self):
            """Move forward."""
            if self.connected:
                asyncio.create_task(self.client.move_forward(self.current_speed))
                self._log(f"⬆️  Moving forward at {self.current_speed}%")
        
        def _move_backward(self):
            """Move backward."""
            if self.connected:
                asyncio.create_task(self.client.move_backward(self.current_speed))
                self._log(f"⬇️  Moving backward at {self.current_speed}%")
        
        def _turn_left(self):
            """Turn left."""
            if self.connected:
                asyncio.create_task(self.client.turn_left(50))
                self._log("⬅️  Turning left")
        
        def _turn_right(self):
            """Turn right."""
            if self.connected:
                asyncio.create_task(self.client.turn_right(50))
                self._log("➡️  Turning right")
        
        def _stop(self):
            """Stop robot."""
            if self.connected:
                asyncio.create_task(self.client.stop())
                self._log("🛑 Stopped")
        
        def _on_speed_changed(self, value: int):
            """Handle speed slider change."""
            self.current_speed = value
            self.speed_label.setText(f"{value}%")
        
        # Camera
        def _toggle_camera(self):
            """Toggle camera."""
            if not self.connected:
                return
            
            if not self.video_active:
                asyncio.create_task(self.client.start_camera())
                self.camera_btn.setText("📷 Stop Camera")
                self.video_active = True
                self._log("📹 Camera started")
            else:
                asyncio.create_task(self.client.stop_camera())
                self.camera_btn.setText("📷 Start Camera")
                self.video_active = False
                self._log("📹 Camera stopped")
        
        def _toggle_lidar(self):
            """Toggle LiDAR."""
            if not self.connected:
                return
            self._log("📍 LiDAR toggle (not implemented)")
        
        # Chat/AI
        def _send_chat_message(self):
            """Send chat message."""
            text = self.chat_input.text().strip()
            if not text:
                return
            
            self.chat_input.clear()
            self._add_chat_message("You", text)
            
            # Process with AI
            if self.ai_brain.is_available():
                asyncio.create_task(self._process_ai_command(text))
            else:
                self._add_chat_message("Robot", "AI not available")
        
        async def _process_ai_command(self, text: str):
            """Process command with AI."""
            result = await self.ai_brain.process_command(text)
            
            response = result.get("response", "Unknown command")
            action = result.get("action")
            
            self._add_chat_message("Robot", response)
            
            # Execute action
            if action and self.connected:
                if action == "move_forward":
                    await self.client.move_forward(result.get("speed", 70))
                elif action == "move_backward":
                    await self.client.move_backward(result.get("speed", 70))
                elif action == "turn_left":
                    await self.client.turn_left(result.get("speed", 50))
                elif action == "turn_right":
                    await self.client.turn_right(result.get("speed", 50))
                elif action == "stop":
                    await self.client.stop()
        
        def _voice_command(self):
            """Capture voice command."""
            if not self.voice_input.is_available():
                QMessageBox.warning(self, "Voice Input", "Voice input not available")
                return
            
            self._log("🎤 Listening...")
            self.voice_btn.setEnabled(False)
            
            # Listen in thread to avoid blocking
            import threading
            def listen():
                text = self.voice_input.listen_once()
                if text:
                    # Process in main thread
                    self.chat_input.setText(text)
                    self._send_chat_message()
                self.voice_btn.setEnabled(True)
            
            threading.Thread(target=listen, daemon=True).start()
        
        def _on_speech_detected(self, text: str):
            """Handle speech detection."""
            self._log(f"📝 Heard: {text}")
        
        def _test_tts(self):
            """Test TTS."""
            if self.tts_engine.is_available():
                self.tts_engine.speak("Hello, I am your robot assistant!")
            else:
                self._log("⚠️  TTS not available")
        
        # Settings
        def _show_settings(self):
            """Show settings dialog."""
            dialog = SettingsDialog(self)
            dialog.settings_changed.connect(self._on_settings_changed)
            dialog.exec()
        
        def _on_settings_changed(self, config: dict):
            """Handle settings change."""
            self._log("⚙️  Settings updated")
            
            # Send to robot
            if self.connected:
                asyncio.create_task(self.client.update_gpio_config(config))
        
        def _show_about(self):
            """Show about dialog."""
            QMessageBox.about(
                self,
                "About Qt Robot Controller",
                "🤖 <b>Qt Robot Controller v1.0</b><br><br>"
                "Raspberry Pi robot controller with AI integration<br><br>"
                "<b>Features:</b><br>"
                "• Real-time video streaming<br>"
                "• Voice control with AI<br>"
                "• Sensor monitoring<br>"
                "• LiDAR SLAM<br><br>"
                "© 2026 ZeroAI Tech"
            )
        
        # UI updates
        def _update_ui(self):
            """Update UI periodically."""
            # Update face
            self.face_label.setText(self.face_animator.get_expression_emoji())
        
        def _update_video(self, data: dict):
            """Update video display."""
            # TODO: Decode and display video frame
            pass
        
        def _update_sensors(self, data: dict):
            """Update sensor display."""
            text = f"Distance: {data.get('distance', 'N/A')} cm\n"
            text += f"Timestamp: {data.get('timestamp', 'N/A')}"
            self.sensor_display.setText(text)
        
        def _add_chat_message(self, sender: str, message: str):
            """Add message to chat."""
            self.chat_display.append(f"<b>{sender}:</b> {message}")
        
        def _log(self, message: str):
            """Log message to console."""
            self.console_display.append(message)
            self.logger.info(message)
        
        # Keyboard handling
        def keyPressEvent(self, event):
            """Handle key press."""
            if not self.keyboard_enabled or not self.connected:
                return
            
            key = event.key()
            
            if key == Qt.Key.Key_Up:
                self._move_forward()
            elif key == Qt.Key.Key_Down:
                self._move_backward()
            elif key == Qt.Key.Key_Left:
                self._turn_left()
            elif key == Qt.Key.Key_Right:
                self._turn_right()
            elif key == Qt.Key.Key_Space:
                self._stop()
        
        def keyReleaseEvent(self, event):
            """Handle key release."""
            if not self.keyboard_enabled or not self.connected:
                return
            
            key = event.key()
            
            if key in [Qt.Key.Key_Up, Qt.Key.Key_Down, Qt.Key.Key_Left, Qt.Key.Key_Right]:
                self._stop()
        
        def closeEvent(self, event):
            """Handle window close."""
            if self.connected:
                asyncio.create_task(self.client.disconnect())
            event.accept()
else:
    # Fallback
    class MainWindow:
        def __init__(self):
            raise ImportError("PyQt6 is required for GUI")
