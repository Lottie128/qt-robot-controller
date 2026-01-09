"""Login dialog for connecting to robot.

Simple connection interface to enter robot IP and port.
"""

import sys
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
        QLineEdit, QPushButton, QGroupBox, QMessageBox
    )
    from PyQt6.QtCore import Qt, pyqtSignal
    from PyQt6.QtGui import QFont
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("⚠️  PyQt6 not available - install with: pip install PyQt6")

sys.path.append(str(Path(__file__).parent.parent.parent))
from shared.constants import DEFAULT_PORT


if PYQT_AVAILABLE:
    class LoginDialog(QDialog):
        """Connection dialog for robot."""
        
        # Signal emitted when connection is requested
        connect_requested = pyqtSignal(str, int)
        
        def __init__(self, parent=None):
            """Initialize login dialog.
            
            Args:
                parent: Parent widget
            """
            super().__init__(parent)
            self.setWindowTitle("Connect to Robot")
            self.setModal(True)
            self.setFixedSize(400, 250)
            
            self._init_ui()
            self._load_last_connection()
        
        def _init_ui(self):
            """Initialize user interface."""
            layout = QVBoxLayout()
            layout.setSpacing(15)
            
            # Title
            title = QLabel("🤖 Qt Robot Controller")
            title_font = QFont()
            title_font.setPointSize(16)
            title_font.setBold(True)
            title.setFont(title_font)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Connection group
            conn_group = QGroupBox("Connection Settings")
            conn_layout = QVBoxLayout()
            
            # IP address
            ip_layout = QHBoxLayout()
            ip_label = QLabel("Robot IP:")
            ip_label.setFixedWidth(80)
            self.ip_input = QLineEdit()
            self.ip_input.setPlaceholderText("192.168.1.100")
            self.ip_input.returnPressed.connect(self._on_connect)
            ip_layout.addWidget(ip_label)
            ip_layout.addWidget(self.ip_input)
            conn_layout.addLayout(ip_layout)
            
            # Port
            port_layout = QHBoxLayout()
            port_label = QLabel("Port:")
            port_label.setFixedWidth(80)
            self.port_input = QLineEdit()
            self.port_input.setText(str(DEFAULT_PORT))
            self.port_input.setPlaceholderText("8888")
            self.port_input.returnPressed.connect(self._on_connect)
            port_layout.addWidget(port_label)
            port_layout.addWidget(self.port_input)
            conn_layout.addLayout(port_layout)
            
            conn_group.setLayout(conn_layout)
            layout.addWidget(conn_group)
            
            # Info label
            info_label = QLabel(
                "💡 Tip: Run the Pi server and enter the IP shown in the terminal"
            )
            info_label.setWordWrap(True)
            info_label.setStyleSheet("color: gray; font-size: 10px;")
            layout.addWidget(info_label)
            
            layout.addStretch()
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            self.connect_btn = QPushButton("🔌 Connect")
            self.connect_btn.setFixedWidth(120)
            self.connect_btn.clicked.connect(self._on_connect)
            self.connect_btn.setDefault(True)
            button_layout.addWidget(self.connect_btn)
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.setFixedWidth(100)
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
        
        def _on_connect(self):
            """Handle connect button click."""
            ip = self.ip_input.text().strip()
            port_text = self.port_input.text().strip()
            
            # Validate IP
            if not ip:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please enter robot IP address"
                )
                return
            
            # Validate port
            try:
                port = int(port_text)
                if port < 1 or port > 65535:
                    raise ValueError()
            except ValueError:
                QMessageBox.warning(
                    self,
                    "Invalid Port",
                    "Please enter a valid port number (1-65535)"
                )
                return
            
            # Save connection info
            self._save_last_connection(ip, port)
            
            # Emit signal
            self.connect_requested.emit(ip, port)
            self.accept()
        
        def _load_last_connection(self):
            """Load last connection info from settings."""
            try:
                from PyQt6.QtCore import QSettings
                settings = QSettings("ZeroAI Tech", "Qt Robot Controller")
                
                last_ip = settings.value("connection/last_ip", "")
                last_port = settings.value("connection/last_port", DEFAULT_PORT)
                
                if last_ip:
                    self.ip_input.setText(last_ip)
                if last_port:
                    self.port_input.setText(str(last_port))
            except:
                pass
        
        def _save_last_connection(self, ip: str, port: int):
            """Save connection info to settings."""
            try:
                from PyQt6.QtCore import QSettings
                settings = QSettings("ZeroAI Tech", "Qt Robot Controller")
                settings.setValue("connection/last_ip", ip)
                settings.setValue("connection/last_port", port)
            except:
                pass
        
        def get_connection_info(self):
            """Get entered connection info.
            
            Returns:
                Tuple of (ip, port)
            """
            return self.ip_input.text().strip(), int(self.port_input.text().strip())
else:
    # Fallback if PyQt6 not available
    class LoginDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyQt6 is required for GUI")
