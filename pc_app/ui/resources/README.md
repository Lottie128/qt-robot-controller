# UI Resources

This directory contains UI resources for the Qt Robot Controller application.

## Contents

- **icons/** - Application icons and toolbar icons
- **images/** - Images and graphics
- **styles/** - Custom Qt stylesheets

## Adding Resources

### Icons

Place icon files (PNG, SVG) in the `icons/` directory:
- Use consistent sizes (16x16, 24x24, 32x32, 48x48)
- Use transparent backgrounds
- Naming convention: `action_name.png`

### Images

Place image files in the `images/` directory:
- Supported formats: PNG, JPEG, SVG
- Keep file sizes reasonable
- Use descriptive names

### Stylesheets

Create Qt stylesheet (QSS) files in `styles/`:
```css
/* dark_theme.qss */
QMainWindow {
    background-color: #1e1e1e;
    color: #e0e0e0;
}

QPushButton {
    background-color: #2d2d2d;
    border: 1px solid #3d3d3d;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #3d3d3d;
}
```

## Loading Resources in Code

```python
from pathlib import Path
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QPushButton

# Load icon
icon_path = Path(__file__).parent / "resources/icons/connect.png"
button = QPushButton(QIcon(str(icon_path)), "Connect")

# Load image
image_path = Path(__file__).parent / "resources/images/logo.png"
pixmap = QPixmap(str(image_path))

# Load stylesheet
style_path = Path(__file__).parent / "resources/styles/dark_theme.qss"
with open(style_path, 'r') as f:
    app.setStyleSheet(f.read())
```

## Recommended Resources

For icons, consider using:
- [Material Design Icons](https://materialdesignicons.com/)
- [Font Awesome](https://fontawesome.com/)
- [Feather Icons](https://feathericons.com/)

For now, the application uses emoji characters as placeholders.
