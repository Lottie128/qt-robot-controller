"""Settings dialog for robot configuration.

Configure GPIO pins, camera, sensors, etc.
"""

import yaml
from pathlib import Path

try:
    from PyQt6.QtWidgets import (
        QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
        QPushButton, QSpinBox, QLabel, QGroupBox, QTabWidget,
        QWidget, QComboBox, QCheckBox
    )
    from PyQt6.QtCore import pyqtSignal
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False


if PYQT_AVAILABLE:
    class SettingsDialog(QDialog):
        """Settings dialog."""
        
        settings_changed = pyqtSignal(dict)
        
        def __init__(self, parent=None):
            """Initialize dialog."""
            super().__init__(parent)
            self.setWindowTitle("⚙️  Settings")
            self.setModal(True)
            self.resize(500, 400)
            
            self.config = {}
            self._init_ui()
        
        def _init_ui(self):
            """Initialize UI."""
            layout = QVBoxLayout()
            
            # Tabs
            tabs = QTabWidget()
            tabs.addTab(self._create_gpio_tab(), "GPIO Pins")
            tabs.addTab(self._create_camera_tab(), "Camera")
            tabs.addTab(self._create_sensor_tab(), "Sensors")
            layout.addWidget(tabs)
            
            # Buttons
            button_layout = QHBoxLayout()
            button_layout.addStretch()
            
            cancel_btn = QPushButton("Cancel")
            cancel_btn.clicked.connect(self.reject)
            button_layout.addWidget(cancel_btn)
            
            save_btn = QPushButton("Save & Apply")
            save_btn.clicked.connect(self._save_settings)
            button_layout.addWidget(save_btn)
            
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
        
        def _create_gpio_tab(self) -> QWidget:
            """Create GPIO configuration tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            # Pin mode
            mode_group = QGroupBox("Pin Numbering Mode")
            mode_layout = QFormLayout()
            
            self.pin_mode_combo = QComboBox()
            self.pin_mode_combo.addItems(["BOARD", "BCM"])
            mode_layout.addRow("Mode:", self.pin_mode_combo)
            
            mode_group.setLayout(mode_layout)
            layout.addWidget(mode_group)
            
            # Motor pins
            motor_group = QGroupBox("Motor Pins")
            motor_layout = QFormLayout()
            
            self.l1_spin = QSpinBox()
            self.l1_spin.setRange(1, 40)
            self.l1_spin.setValue(33)
            motor_layout.addRow("L1 (Left Forward):", self.l1_spin)
            
            self.l2_spin = QSpinBox()
            self.l2_spin.setRange(1, 40)
            self.l2_spin.setValue(38)
            motor_layout.addRow("L2 (Left Backward):", self.l2_spin)
            
            self.r1_spin = QSpinBox()
            self.r1_spin.setRange(1, 40)
            self.r1_spin.setValue(35)
            motor_layout.addRow("R1 (Right Forward):", self.r1_spin)
            
            self.r2_spin = QSpinBox()
            self.r2_spin.setRange(1, 40)
            self.r2_spin.setValue(40)
            motor_layout.addRow("R2 (Right Backward):", self.r2_spin)
            
            motor_group.setLayout(motor_layout)
            layout.addWidget(motor_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_camera_tab(self) -> QWidget:
            """Create camera settings tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            camera_group = QGroupBox("Camera Configuration")
            camera_layout = QFormLayout()
            
            self.camera_enabled = QCheckBox()
            self.camera_enabled.setChecked(True)
            camera_layout.addRow("Enable Camera:", self.camera_enabled)
            
            self.camera_type = QComboBox()
            self.camera_type.addItems(["opencv", "picamera2"])
            camera_layout.addRow("Camera Type:", self.camera_type)
            
            self.camera_width = QSpinBox()
            self.camera_width.setRange(160, 1920)
            self.camera_width.setValue(640)
            camera_layout.addRow("Width:", self.camera_width)
            
            self.camera_height = QSpinBox()
            self.camera_height.setRange(120, 1080)
            self.camera_height.setValue(480)
            camera_layout.addRow("Height:", self.camera_height)
            
            self.camera_fps = QSpinBox()
            self.camera_fps.setRange(5, 60)
            self.camera_fps.setValue(30)
            camera_layout.addRow("FPS:", self.camera_fps)
            
            camera_group.setLayout(camera_layout)
            layout.addWidget(camera_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _create_sensor_tab(self) -> QWidget:
            """Create sensor settings tab."""
            tab = QWidget()
            layout = QVBoxLayout()
            
            ultrasonic_group = QGroupBox("Ultrasonic Sensor")
            ultrasonic_layout = QFormLayout()
            
            self.ultrasonic_enabled = QCheckBox()
            self.ultrasonic_enabled.setChecked(True)
            ultrasonic_layout.addRow("Enable:", self.ultrasonic_enabled)
            
            self.trigger_pin = QSpinBox()
            self.trigger_pin.setRange(1, 40)
            self.trigger_pin.setValue(11)
            ultrasonic_layout.addRow("Trigger Pin:", self.trigger_pin)
            
            self.echo_pin = QSpinBox()
            self.echo_pin.setRange(1, 40)
            self.echo_pin.setValue(13)
            ultrasonic_layout.addRow("Echo Pin:", self.echo_pin)
            
            ultrasonic_group.setLayout(ultrasonic_layout)
            layout.addWidget(ultrasonic_group)
            
            layout.addStretch()
            tab.setLayout(layout)
            return tab
        
        def _save_settings(self):
            """Save settings and emit signal."""
            config = {
                "motors": {
                    "pin_mode": self.pin_mode_combo.currentText(),
                    "pins": {
                        "L1": self.l1_spin.value(),
                        "L2": self.l2_spin.value(),
                        "R1": self.r1_spin.value(),
                        "R2": self.r2_spin.value()
                    }
                },
                "camera": {
                    "enabled": self.camera_enabled.isChecked(),
                    "type": self.camera_type.currentText(),
                    "width": self.camera_width.value(),
                    "height": self.camera_height.value(),
                    "fps": self.camera_fps.value()
                },
                "ultrasonic": {
                    "enabled": self.ultrasonic_enabled.isChecked(),
                    "trigger_pin": self.trigger_pin.value(),
                    "echo_pin": self.echo_pin.value()
                }
            }
            
            self.settings_changed.emit(config)
            self.accept()
else:
    class SettingsDialog:
        def __init__(self, *args, **kwargs):
            raise ImportError("PyQt6 required")
