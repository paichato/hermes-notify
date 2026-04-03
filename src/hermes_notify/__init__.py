"""
Hermes Notify - Desktop notifications for Hermes AI Agent

Display beautiful notifications with audio announcements when tasks complete.
"""

__version__ = "1.0.0"
__author__ = "Mister Strong"

from hermes_notify.config import Config
from hermes_notify.overlay import NotificationOverlay

__all__ = ["Config", "NotificationOverlay", "__version__"]
