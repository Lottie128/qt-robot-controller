"""Login/Connection dialog for robot controller.

Simple dialog to enter robot IP and port.
"""

import json
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
        QLineEdit, QPushButton, QLabel, QComboBox, QGroupBox
    )
    from PyQt6.QtCore import pyqtSignal, Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


if PYQT_AVAILABLE:
    class LoginDialog(QDialog):
        """Connection dialog."""
        
        connect_requested = pyqtSignal(str, int)
        
        def __init__(self, parent=None):
            """Initialize dialog."""
            super().__init__(parent)
            self.setWindowTitle("🔌 Connect to Robot")
            self.setModal(True)
            self.resize(400, 200)
            
            # Recent connections
            self.recent_file = Path("config/recent_connections.json")
            self.recent_connections = self._load_recent()
            
            self._init_ui()
        
        def _init_ui(self):
            """Initialize UI."""
            layout = QVBoxLayout()
            
            # Info label
            info_label = QLabel(
                "Enter the IP address shown on your Raspberry Pi terminal.\n"
                "Make sure both devices are on the same network."
            )
            info_label.setWordWrap(True)
            layout.addWidget(info_label)
            
            # Connection form
            form_group = QGroupBox("Connection Details")
            form_layout = QFormLayout()
            
            # Recent connections dropdown
            if self.recent_connections:
                self.recent_combo = QComboBox()
                self.recent_combo.addItem("-- Recent Connections --")
                for conn in self.recent_connections:
                    self.recent_combo.addItem(f"{conn['ip']}:{conn['port']}")
                self.recent_combo.currentIndexChanged.connect(self._on_recent_selected)
                form_layout.addRow("Recent:", self.recent_combo)
            
            # IP address
            self.ip_input = QLineEdit()
            self.ip_input.setPlaceholderText("192.168.1.100")
            if self.recent_connections:
                self.ip_input.setText(self.recent_connections[0]['ip'])
            form_layout.addRow("IP Address:", self.ip_input)
            
            # Port
            self.port_input = QLineEdit()
            self.port_input.setPlaceholderText("8888")
            self.port_input.setText("8888")
            form_layout.addRow("Port:", self.port_input)
            
            form_group.setLayout(form_layout)
            layout.addWidget(form_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            connect_btn = QPushButton("🔌 Connect")
            connect_btn.setDefault(True)
            connect_btn.clicked.connect(self._connect)
            button_layout.addWidget(connect_btn)
            
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
        
        def _on_recent_selected(self, index: int):
            """Handle recent connection selection."""
            if index > 0 and self.recent_connections:
                conn = self.recent_connections[index - 1]
                self.ip_input.setText(conn['ip'])
                self.port_input.setText(str(conn['port']))
        
        def _connect(self):
            """Handle connect button."""
            ip = self.ip_input.text().strip()
            port_text = self.port_input.text().strip()
            
            # Validate
            if not ip:
                return
            
            try:
                port = int(port_text)
            except ValueError:
                return
            
            # Save to recent
            self._save_recent(ip, port)
            
            # Emit signal
            self.connect_requested.emit(ip, port)
            self.accept()
        
        def _load_recent(self) -> list:
            """Load recent connections."""
            try:
                if self.recent_file.exists():
                    with open(self.recent_file, 'r') as f:
                        return json.load(f)
            except:
                pass
            return []
        
        def _save_recent(self, ip: str, port: int):
            """Save to recent connections."""
            conn = {'ip': ip, 'port': port}
            
            # Remove if exists
            self.recent_connections = [c for c in self.recent_connections if c != conn]
            
            # Add to front
            self.recent_connections.insert(0, conn)
            
            # Keep only last 5
            self.recent_connections = self.recent_connections[:5]
            
            # Save
            try:
                self.recent_file.parent.mkdir(exist_ok=True)
                with open(self.recent_file, 'w') as f:
                    json.dump(self.recent_connections, f)
            except:
                pass
else:
    class LoginDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyQt6 required")
