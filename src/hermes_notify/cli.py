"""
Command-line interface for hermes-notify.
"""

import argparse
import sys
import subprocess
from typing import List, Optional

from hermes_notify import __version__
from hermes_notify.config import Config
from hermes_notify.overlay import NotificationOverlay


def main(args: Optional[List[str]] = None):
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='hermes-notify',
        description='Desktop notifications for Hermes AI Agent',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  hermes-notify "Task complete!"
  hermes-notify -d 5 "Working on it..."
  hermes-notify --no-audio "Silent update"
  hermes-notify --config           # Edit configuration
  hermes-notify --status           # Show current config
  hermes-notify --reset            # Reset to defaults
        """
    )
    
    parser.add_argument(
        'message',
        nargs='?',
        help='Notification message (default: configured default message)'
    )
    
    parser.add_argument(
        '-d', '--duration',
        type=int,
        help='Display duration in seconds'
    )
    
    parser.add_argument(
        '-v', '--voice',
        type=str,
        help='TTS voice name'
    )
    
    parser.add_argument(
        '--no-audio',
        action='store_true',
        help='Disable audio announcement'
    )
    
    parser.add_argument(
        '--no-icon',
        action='store_true',
        help='Hide icon'
    )
    
    parser.add_argument(
        '--position',
        choices=['top-left', 'top-center', 'top-right', 
                 'bottom-left', 'bottom-center', 'bottom-right'],
        help='Notification position on screen'
    )
    
    parser.add_argument(
        '--config',
        action='store_true',
        help='Open configuration editor'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current configuration'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reset configuration to defaults'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )
    
    parser.add_argument(
        '--install-prompt',
        action='store_true',
        help='Install shell prompt integration'
    )
    
    parsed = parser.parse_args(args)
    
    # Load config
    config = Config()
    
    # Handle special commands
    if parsed.status:
        show_status(config)
        return
    
    if parsed.reset:
        config.reset()
        print("✓ Configuration reset to defaults.")
        return
    
    if parsed.config:
        edit_config(config)
        return
    
    if parsed.install_prompt:
        install_prompt_integration()
        return
    
    # Show notification
    notification = NotificationOverlay(
        message=parsed.message,
        config=config,
        duration=parsed.duration,
        audio=not parsed.no_audio
    )
    
    # Override config values with CLI args
    if parsed.voice:
        notification.voice = parsed.voice
    if parsed.position:
        notification.config.set('position', parsed.position)
    if parsed.no_icon:
        notification.config.set('show_icon', False)
    
    # Save to history
    config.add_to_history(notification.message)
    config.save()
    
    notification.show()


def show_status(config: Config) -> None:
    """Display current configuration."""
    print("\n🔧 hermes-notify configuration:")
    print("=" * 40)
    print(f"  Config file: {config.config_path}")
    print(f"  Default message: {config.get('default_message')}")
    print(f"  Voice: {config.get('voice')}")
    print(f"  Duration: {config.get('duration')}s")
    print(f"  Position: {config.get('position')}")
    print(f"  Mode: {config.get('mode')}")
    print(f"  Audio: {'✓' if config.get('audio') else '✗'}")
    print(f"  Show icon: {'✓' if config.get('show_icon') else '✗'}")
    print(f"  Colors:")
    print(f"    Background: {config.get('colors.background')}")
    print(f"    Accent: {config.get('colors.accent')}")
    print(f"    Text: {config.get('colors.text')}")
    print("=" * 40)
    print()


def edit_config(config: Config) -> None:
    """Open config file in default editor."""
    import os
    editor = os.environ.get('EDITOR', 'nano')
    try:
        subprocess.run([editor, config.config_path])
        print("✓ Configuration updated.")
    except FileNotFoundError:
        print(f"Editor '{editor}' not found. Edit manually: {config.config_path}")


def install_prompt_integration() -> None:
    """Install shell prompt integration."""
    shell_config = None
    for path in ['~/.zshrc', '~/.bashrc', '~/.bash_profile']:
        expanded = os.path.expanduser(path)
        if os.path.exists(expanded):
            shell_config = expanded
            break
    
    if not shell_config:
        print("✗ Could not find shell configuration file.")
        return
    
    integration_code = '''
# hermes-notify prompt integration
# Add /ntf at end of command to show notification
ntf_wrapper() {
    local exit_code=$?
    if [[ "$_ntf_pending" == "1" ]]; then
        if [[ $exit_code -eq 0 ]]; then
            hermes-notify "${_ntf_message:-Task complete!}" 2>/dev/null &
        fi
        _ntf_pending=0
    fi
    return $exit_code
}

# Alias for quick notification
alias ntf='_ntf_pending=1; _ntf_message='

# Preexec hook for zsh
if [[ -n "$ZSH_VERSION" ]]; then
    autoload -Uz add-zsh-hook
    add-zsh-hook precmd ntf_wrapper
fi

# For bash
if [[ -n "$BASH_VERSION" ]]; then
    PROMPT_COMMAND="ntf_wrapper;$PROMPT_COMMAND"
fi
'''
    
    with open(os.path.expanduser(shell_config), 'a') as f:
        f.write(integration_code)
    
    print(f"✓ Prompt integration added to {shell_config}")
    print("  Usage: ntf \"my task\" && <your command>")
    print("  Notification will show if command succeeds.")


if __name__ == '__main__':
    main()
