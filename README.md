# hermes-notify

🤖 Beautiful desktop notifications for AI agents, with audio announcements.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-green.svg)](https://python.org)

## Features

- 🎨 **Beautiful UI** — Dark-themed notification with smooth animations
- 🔊 **Audio announcements** — Text-to-speech when tasks complete
- ⚡ **Lightweight** — Pure Python, no heavy dependencies
- 🎯 **Configurable** — Colors, position, duration, voice
- 🔧 **Easy setup** — Interactive wizard on install
- 🐚 **Shell integration** — Optional prompt hook support

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/paichato/hermes-notify/main/scripts/install.sh | bash
```

Or with pip:

```bash
pip install hermes-notify
```

## Quick Start

```bash
# Show a notification
hermes-notify "Task complete!"

# With custom duration
hermes-notify -d 5 "Working on it..."

# Silent notification
hermes-notify --no-audio "Update"
```

## Configuration

```bash
# Run interactive setup
hermes-notify-setup

# View current config
hermes-notify --status

# Edit config file
hermes-notify --config

# Reset to defaults
hermes-notify --reset
```

### Config Options

| Option | Description | Default |
|--------|-------------|---------|
| `default_message` | Default notification text | "Boss, I'm done!" |
| `voice` | TTS voice name | "Samantha" |
| `duration` | Display time (seconds) | 3 |
| `position` | Screen position | "bottom-center" |
| `mode` | Notification mode | "manual" |
| `audio` | Enable audio | true |
| `show_icon` | Show icon | true |
| `colors.background` | Background color | "#1a1a2e" |
| `colors.accent` | Accent color | "#e94560" |

### Positions

- `top-left`, `top-center`, `top-right`
- `bottom-left`, `bottom-center`, `bottom-right`

## Shell Integration

Install prompt integration to auto-notify after successful commands:

```bash
hermes-notify --install-prompt
```

Then use:

```bash
# Notify after successful command
ntf "deploy done" && ./deploy.sh
```

## Python API

```python
from hermes_notify import notify, Config

# Simple notification
notify("Task complete!")

# With options
notify("Working...", duration=5, audio=False)

# With custom config
config = Config()
config.set('voice', 'Alex')
notify("Hello!", config=config)
```

## Requirements

- Python 3.9+
- macOS (for text-to-speech)
- Pillow (auto-installed)

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please open an issue or PR on GitHub.

## Related

- [Hermes Agent](https://github.com/nousresearch/hermes-agent) — AI assistant framework
