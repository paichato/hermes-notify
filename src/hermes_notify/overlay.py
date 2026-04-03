"""
Notification overlay display for hermes-notify.
"""

import os
import sys
import tempfile
import subprocess
import tkinter as tk
from typing import Optional

from PIL import Image, ImageDraw

from hermes_notify.config import Config


def create_checkmark_image(size: tuple = (100, 100), accent_color: str = "#64ff96") -> Image.Image:
    """Create a checkmark icon with transparent background."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size[0] // 2, size[1] // 2
    radius = min(cx, cy) - 10
    
    # Parse hex color
    r = int(accent_color[1:3], 16) if accent_color.startswith('#') else 100
    g = int(accent_color[3:5], 16) if accent_color.startswith('#') else 255
    b = int(accent_color[5:7], 16) if accent_color.startswith('#') else 150
    
    # Draw circle background
    for i in range(radius, 0, -1):
        alpha = int(180 * (i / radius))
        draw.ellipse([cx - i, cy - i, cx + i, cy + i], fill=(30, 30, 50, alpha))
    
    # Outer ring
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], 
                 outline=(r, g, b, 200), width=3)
    
    # Checkmark
    points = [(cx - 25, cy + 5), (cx - 8, cy + 25), (cx + 30, cy - 18)]
    for w in range(6, 0, -1):
        draw.line(points, fill=(r, g, b, 255), width=w)
    
    return img


def create_agent_image(size: tuple = (100, 100)) -> Image.Image:
    """Create a cute robot agent icon."""
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    cx, cy = size[0] // 2, size[1] // 2
    
    # Head
    draw.rounded_rectangle([cx - 45, cy - 50, cx + 45, cy + 20], 
                           radius=15, fill=(30, 30, 50, 230), 
                           outline=(100, 100, 255, 255), width=2)
    
    # Eyes
    draw.ellipse([cx - 30, cy - 30, cx - 10, cy - 10], fill=(100, 255, 200, 255))
    draw.ellipse([cx + 10, cy - 30, cx + 30, cy - 10], fill=(100, 255, 200, 255))
    
    # Smile
    draw.arc([cx - 18, cy, cx + 18, cy + 20], 0, 180, fill=(100, 255, 200, 255), width=2)
    
    # Antenna
    draw.line([cx, cy - 50, cx, cy - 65], fill=(100, 100, 255, 255), width=2)
    draw.ellipse([cx - 6, cy - 73, cx + 6, cy - 61], fill=(233, 69, 96, 255))
    
    return img


class NotificationOverlay:
    """Display notification overlay on screen."""
    
    def __init__(self, message: Optional[str] = None, config: Optional[Config] = None, 
                 duration: Optional[int] = None, audio: Optional[bool] = None):
        self.config = config or Config()
        self.message = message or self.config.get('default_message')
        self.duration = duration or self.config.get('duration', 3)
        self.audio = audio if audio is not None else self.config.get('audio', True)
        self.voice = self.config.get('voice', 'Samantha')
        
        # Get colors from config
        self.bg_color = self.config.get('colors.background', '#1a1a2e')
        self.accent_color = self.config.get('colors.accent', '#e94560')
        self.text_color = self.config.get('colors.text', '#ffffff')
        self.subtitle_color = self.config.get('colors.subtitle', '#888888')
        
        # Get dimensions
        self.width = self.config.get('width', 480)
        self.height = self.config.get('height', 160)
        self.font_size = self.config.get('font_size', 42)
        
        self._temp_files = []
        self.root = None
        
    def show(self) -> None:
        """Display the notification."""
        self._create_window()
        self._setup_ui()
        self._schedule_animations()
        self._run_mainloop()
    
    def _create_window(self) -> None:
        """Create the overlay window."""
        self.root = tk.Tk()
        self.root.title("hermes-notify")
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.0)
        
        # Position based on config
        position = self.config.get('position', 'bottom-center')
        x, y = self._calculate_position(position)
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")
        self.root.configure(bg=self.bg_color)
        
        # Bind close events
        self.root.bind('<Button-1>', lambda e: self._fade_out())
        self.root.bind('<Escape>', lambda e: self._fade_out())
    
    def _calculate_position(self, position: str) -> tuple:
        """Calculate x, y coordinates based on position string."""
        self.root.update_idletasks()  # Force geometry update
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        margin = 30
        
        positions = {
            'top-left': (margin, margin),
            'top-center': ((screen_w - self.width) // 2, margin),
            'top-right': (screen_w - self.width - margin, margin),
            'bottom-left': (margin, screen_h - self.height - margin),
            'bottom-center': ((screen_w - self.width) // 2, screen_h - self.height - margin),
            'bottom-right': (screen_w - self.width - margin, screen_h - self.height - margin),
        }
        return positions.get(position, positions['bottom-center'])
    
    def _setup_ui(self) -> None:
        """Set up notification UI elements."""
        # Main container with padding
        container = tk.Frame(self.root, bg=self.bg_color)
        container.pack(fill='both', expand=True, padx=3, pady=3)
        
        # Border frame
        border = tk.Frame(container, bg=self.accent_color)
        border.pack(fill='both', expand=True)
        
        inner = tk.Frame(border, bg=self.bg_color)
        inner.pack(fill='both', expand=True, padx=2, pady=2)
        
        # Content frame
        content = tk.Frame(inner, bg=self.bg_color)
        content.pack(fill='both', expand=True, padx=20, pady=12)
        
        # Icon
        if self.config.get('show_icon', True):
            self._add_icon(content)
        
        # Text content
        self._add_text(content)
    
    def _add_icon(self, parent: tk.Frame) -> None:
        """Add icon to notification."""
        icon_frame = tk.Frame(parent, bg=self.bg_color)
        icon_frame.pack(side='left', padx=(0, 15))
        
        img = create_checkmark_image((90, 90), self.accent_color)
        self._icon_path = os.path.join(tempfile.gettempdir(), 'hermes_notify_icon.png')
        img.save(self._icon_path)
        self._temp_files.append(self._icon_path)
        
        self._icon_photo = tk.PhotoImage(file=self._icon_path)
        icon_label = tk.Label(icon_frame, image=self._icon_photo, bg=self.bg_color)
        icon_label.pack()
    
    def _add_text(self, parent: tk.Frame) -> None:
        """Add text content to notification."""
        text_frame = tk.Frame(parent, bg=self.bg_color)
        text_frame.pack(side='left', fill='both', expand=True)
        
        # Main message
        msg_label = tk.Label(
            text_frame, 
            text=self.message,
            fg=self.text_color,
            bg=self.bg_color,
            font=('Helvetica', self.font_size, 'bold'),
            wraplength=self.width - 150,
            justify='left'
        )
        msg_label.pack(anchor='w', pady=(2, 0))
        
        # Subtitle
        sub_label = tk.Label(
            text_frame,
            text="— your AI assistant",
            fg=self.subtitle_color,
            bg=self.bg_color,
            font=('Helvetica', 11, 'italic')
        )
        sub_label.pack(anchor='w')
    
    def _schedule_animations(self) -> None:
        """Schedule fade in/out animations."""
        self.root.after(50, self._fade_in)
        
        if self.audio:
            self.root.after(300, self._play_audio)
        
        self.root.after(int(self.duration * 1000), self._fade_out)
    
    def _fade_in(self) -> None:
        """Fade in animation."""
        try:
            alpha = float(self.root.attributes('-alpha'))
            if alpha < 0.95:
                self.root.attributes('-alpha', min(alpha + 0.08, 0.95))
                self.root.after(20, self._fade_in)
        except tk.TclError:
            pass
    
    def _fade_out(self) -> None:
        """Fade out animation."""
        try:
            alpha = float(self.root.attributes('-alpha'))
            if alpha > 0.05:
                self.root.attributes('-alpha', max(alpha - 0.1, 0.0))
                self.root.after(15, self._fade_out)
            else:
                self._cleanup()
        except tk.TclError:
            self._cleanup()
    
    def _play_audio(self) -> None:
        """Play audio announcement using system TTS."""
        try:
            subprocess.Popen(
                ['say', '-v', self.voice, self.message],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception:
            pass
    
    def _cleanup(self) -> None:
        """Clean up temp files and destroy window."""
        for path in self._temp_files:
            try:
                os.remove(path)
            except OSError:
                pass
        try:
            self.root.destroy()
        except tk.TclError:
            pass
        sys.exit(0)
    
    def _run_mainloop(self) -> None:
        """Start the Tkinter main loop."""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self._cleanup()


def notify(message: Optional[str] = None, **kwargs) -> None:
    """Quick function to show a notification."""
    config = kwargs.pop('config', None)
    notification = NotificationOverlay(message=message, config=config, **kwargs)
    notification.show()
