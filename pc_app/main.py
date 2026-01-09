#!/usr/bin/env python3
"""Qt Robot Controller - Main Entry Point

Launch the robot controller application.
"""

import sys
import asyncio
import logging
from pathlib import Path

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    PYQT_AVAILABLE = True
except ImportError:
    PYQT_AVAILABLE = False
    print("❌ PyQt6 not installed. Install with: pip install PyQt6")
    sys.exit(1)

# Add parent to path for shared modules
sys.path.append(str(Path(__file__).parent.parent))
from shared.constants import VERSION, APP_NAME

# Import UI
from ui.main_window import MainWindow


def setup_logging():
    """Setup application logging."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "app.log"),
            logging.StreamHandler()
        ]
    )


def main():
    """Main application entry point."""
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info(f"Starting {APP_NAME} v{VERSION}")
    
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setApplicationVersion(VERSION)
    
    # Apply dark theme
    app.setStyle("Fusion")
    
    # Create and show main window
    try:
        window = MainWindow()
        window.show()
        
        # Run event loop
        sys.exit(app.exec())
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
