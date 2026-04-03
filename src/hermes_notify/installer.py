"""
Interactive installer for hermes-notify.
"""

import json
import os
import sys
from typing import Dict

from hermes_notify.config import Config, DEFAULT_CONFIG


# ANSI colors for terminal
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'


def cprint(color: str, text: str) -> None:
    """Print colored text."""
    print(f"{color}{text}{Colors.END}")


def print_header() -> None:
    """Print installer header."""
    print()
    cprint(Colors.CYAN, "╔══════════════════════════════════════════════╗")
    cprint(Colors.CYAN, "║                                              ║")
    cprint(Colors.CYAN, "║     🤖 hermes-notify setup wizard 🤖        ║")
    cprint(Colors.CYAN, "║                                              ║")
    cprint(Colors.CYAN, "╚══════════════════════════════════════════════╝")
    print()


def ask(prompt: str, default: str = None) -> str:
    """Ask user for input with default."""
    if default:
        response = input(f"  {prompt} [{default}]: ").strip()
        return response if response else default
    else:
        response = input(f"  {prompt}: ").strip()
        return response


def ask_choice(prompt: str, choices: list, default: str = None) -> str:
    """Ask user to choose from options."""
    print(f"\n  {prompt}")
    for i, choice in enumerate(choices, 1):
        marker = f" {Colors.GREEN}← default{Colors.END}" if choice == default else ""
        print(f"    {Colors.BOLD}{i}{Colors.END}) {choice}{marker}")
    
    while True:
        response = input(f"\n  Your choice [1-{len(choices)}]: ").strip()
        if not response and default:
            return default
        try:
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        cprint(Colors.RED, "  Invalid choice, try again.")


def ask_yesno(prompt: str, default: bool = True) -> bool:
    """Ask yes/no question."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"  {prompt} [{default_str}]: ").strip().lower()
    if not response:
        return default
    return response in ('y', 'yes')


def print_separator() -> None:
    """Print section separator."""
    cprint(Colors.DIM, "  " + "─" * 44)


def run_setup() -> Dict:
    """Run interactive setup wizard."""
    print_header()
    
    config = {}
    
    # Step 1: Default message
    print_separator()
    cprint(Colors.HEADER, "📋 Step 1: Default Notification Message")
    print()
    config['default_message'] = ask(
        "What should I say when notifying you?",
        DEFAULT_CONFIG['default_message']
    )
    
    # Step 2: Voice
    print_separator()
    cprint(Colors.HEADER, "🎙️  Step 2: Voice for Audio")
    print()
    cprint(Colors.DIM, "  Common voices: Samantha, Alex, Daniel (UK), Victoria")
    config['voice'] = ask(
        "Which voice should I use?",
        DEFAULT_CONFIG['voice']
    )
    
    # Step 3: Duration
    print_separator()
    cprint(Colors.HEADER, "⏱️  Step 3: Display Duration")
    print()
    duration_str = ask(
        "How long to show notification? (seconds)",
        str(DEFAULT_CONFIG['duration'])
    )
    try:
        config['duration'] = int(duration_str)
    except ValueError:
        config['duration'] = DEFAULT_CONFIG['duration']
    
    # Step 4: Position
    print_separator()
    cprint(Colors.HEADER, "📍 Step 4: Screen Position")
    print()
    positions = [
        'bottom-center', 'bottom-right', 'bottom-left',
        'top-center', 'top-right', 'top-left'
    ]
    config['position'] = ask_choice(
        "Where should notifications appear?",
        positions,
        DEFAULT_CONFIG['position']
    )
    
    # Step 5: Audio
    print_separator()
    cprint(Colors.HEADER, "🔊 Step 5: Audio Announcements")
    print()
    config['audio'] = ask_yesno(
        "Play audio when notifying?",
        DEFAULT_CONFIG['audio']
    )
    
    # Step 6: Mode
    print_separator()
    cprint(Colors.HEADER, "⚙️  Step 6: Notification Mode")
    print()
    cprint(Colors.DIM, "  Choose when you want me to pop up with a notification:\n")
    modes = [
        'manual  - You explicitly ask me to notify (e.g., hermes-notify "done")',
        'auto    - I notify automatically after running any command for you',
        'prompt  - I hook into your shell prompt to notify when commands succeed'
    ]
    mode_choice = ask_choice(
        "When should I notify you?",
        modes,
        modes[0]
    )
    config['mode'] = mode_choice.split()[0]
    
    # Step 7: Colors (optional)
    print_separator()
    cprint(Colors.HEADER, "🎨 Step 7: Customization")
    print()
    if ask_yesno("Use custom colors?", False):
        config['colors'] = {
            'background': ask("Background color (hex)", DEFAULT_CONFIG['colors']['background']),
            'accent': ask("Accent color (hex)", DEFAULT_CONFIG['colors']['accent']),
            'text': ask("Text color (hex)", DEFAULT_CONFIG['colors']['text']),
        }
    
    return config


def save_config(config: Dict) -> str:
    """Save configuration to file."""
    config_path = Config.get_default_config_path()
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # Merge with defaults
    full_config = DEFAULT_CONFIG.copy()
    full_config.update(config)
    if 'colors' in config:
        full_config['colors'].update(config['colors'])
    
    with open(config_path, 'w') as f:
        json.dump(full_config, f, indent=2)
    
    return config_path


def main():
    """Main installer entry point."""
    try:
        config = run_setup()
        
        print_separator()
        print()
        
        config_path = save_config(config)
        
        cprint(Colors.GREEN, "✅ Setup complete!")
        print()
        cprint(Colors.DIM, f"  Config saved to: {config_path}")
        print()
        cprint(Colors.BOLD, "  Quick start:")
        cprint(Colors.DIM, '    hermes-notify "Hello!"')
        cprint(Colors.DIM, '    hermes-notify --status')
        cprint(Colors.DIM, '    hermes-notify --config')
        print()
        
    except KeyboardInterrupt:
        print()
        cprint(Colors.YELLOW, "Setup cancelled.")
        sys.exit(1)


if __name__ == '__main__':
    main()
