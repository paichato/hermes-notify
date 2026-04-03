"""
Configuration management for hermes-notify.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

# Default configuration
DEFAULT_CONFIG = {
    "default_message": "Boss, I'm done!",
    "voice": "Samantha",
    "duration": 3,
    "position": "bottom-center",  # top-left, top-center, top-right, bottom-left, bottom-center, bottom-right
    "mode": "manual",  # manual, auto, prompt
    "colors": {
        "background": "#1a1a2e",
        "accent": "#e94560",
        "text": "#ffffff",
        "subtitle": "#888888"
    },
    "audio": True,
    "show_icon": True,
    "font_size": 42,
    "width": 480,
    "height": 160,
    "auto_dismiss_click": True,
    "history": []
}

# Config file locations (in order of preference)
CONFIG_LOCATIONS = [
    os.path.expanduser("~/.config/hermes-notify/config.json"),
    os.path.expanduser("~/.hermes-notify.json"),
]


class Config:
    """Manage hermes-notify configuration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._find_config()
        self.data = DEFAULT_CONFIG.copy()
        self.load()
    
    def _find_config(self) -> str:
        """Find existing config file or return default location."""
        for path in CONFIG_LOCATIONS:
            if os.path.exists(path):
                return path
        return CONFIG_LOCATIONS[0]
    
    def load(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    self._merge(self.data, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Could not load config: {e}")
    
    def save(self) -> None:
        """Save configuration to file."""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def _merge(self, base: Dict, override: Dict) -> None:
        """Recursively merge override into base."""
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        data = self.data
        for k in keys[:-1]:
            if k not in data:
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
    
    def reset(self) -> None:
        """Reset configuration to defaults."""
        self.data = DEFAULT_CONFIG.copy()
        self.save()
    
    def add_to_history(self, message: str) -> None:
        """Add a notification to history."""
        history = self.data.get('history', [])
        history.append({
            'message': message,
            'timestamp': self._get_timestamp()
        })
        # Keep only last 100 entries
        self.data['history'] = history[-100:]
    
    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    @staticmethod
    def get_default_config_path() -> str:
        """Return the default config path."""
        return CONFIG_LOCATIONS[0]
