# Configuration Directory

This directory contains configuration files for the Qt Robot Controller PC application.

## Files

### app_config.yaml

Main application configuration including:
- UI settings (window size, update rate)
- Connection settings (default port, timeout)
- Video settings (resolution, auto-start)
- AI/Voice settings (providers, languages)
- Logging configuration

### .env

Environment variables (not in version control):
- API keys (Gemini, etc.)
- Custom endpoints
- Secrets

**Note:** Copy `.env.example` to `.env` and fill in your values.

### recent_connections.json

Auto-generated file storing recent robot connections for quick access.

## Usage

### Loading Configuration

```python
import yaml
from pathlib import Path

config_file = Path("config/app_config.yaml")
with open(config_file, 'r') as f:
    config = yaml.safe_load(f)

print(config['app']['name'])
print(config['connection']['default_port'])
```

### Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv('config/.env')
api_key = os.getenv('GEMINI_API_KEY')
```

## Customization

Edit `app_config.yaml` to customize:

- **Window size**: `ui.window_width`, `ui.window_height`
- **Update rate**: `ui.update_rate` (Hz)
- **Default port**: `connection.default_port`
- **Voice language**: `voice.language`
- **TTS settings**: `tts.rate`, `tts.volume`
- **Log level**: `logging.level`

## Security

- Never commit `.env` to version control
- Keep API keys secret
- Use `.env.example` for documentation only
