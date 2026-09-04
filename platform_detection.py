"""
Platform Detection and Management

Detects the current platform (Windows/Linux/Android/Termux)
and provides platform-specific utilities.
"""

import sys
import platform
from pathlib import Path


class PlatformDetector:
    """Detect and manage current platform."""

    PLATFORM_WINDOWS = "windows"
    PLATFORM_LINUX = "linux"
    PLATFORM_TERMUX = "termux"
    PLATFORM_ANDROID = "android"
    PLATFORM_UNKNOWN = "unknown"

    @classmethod
    def detect_platform(cls):
        """Detect current platform."""
        system = platform.system()
        
        if system == "Windows":
            return cls.PLATFORM_WINDOWS
        elif system == "Linux":
            # Check if Termux
            if cls._is_termux():
                return cls.PLATFORM_TERMUX
            else:
                return cls.PLATFORM_LINUX
        elif system == "Darwin":
            return "macos"
        else:
            return cls.PLATFORM_UNKNOWN

    @classmethod
    def _is_termux(cls):
        """Check if running in Termux."""
        import os
        import subprocess
        
        # Check 1: TERMUX_VERSION environment variable (most reliable)
        if os.environ.get("TERMUX_VERSION"):
            return True
        
        # Check 2: Check if running Termux shell
        try:
            result = subprocess.run(["which", "termux-setup-storage"], 
                                   capture_output=True, timeout=1)
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Check 3: Home directory check
        home = os.path.expanduser("~")
        if "/data/data/com.termux" in home:
            return True
        
        return False

    @classmethod
    def is_windows(cls):
        """Check if Windows platform."""
        return cls.detect_platform() == cls.PLATFORM_WINDOWS

    @classmethod
    def is_linux(cls):
        """Check if Linux platform."""
        return cls.detect_platform() == cls.PLATFORM_LINUX

    @classmethod
    def is_termux(cls):
        """Check if Termux platform."""
        return cls.detect_platform() == cls.PLATFORM_TERMUX

    @classmethod
    def is_android(cls):
        """Check if Android (via Termux)."""
        return cls.is_termux()

    @classmethod
    def get_platform_name(cls):
        """Get human-readable platform name."""
        platform = cls.detect_platform()
        names = {
            cls.PLATFORM_WINDOWS: "Windows",
            cls.PLATFORM_LINUX: "Linux",
            cls.PLATFORM_TERMUX: "Android (Termux)",
            cls.PLATFORM_UNKNOWN: "Unknown",
        }
        return names.get(platform, "Unknown")

    @classmethod
    def get_config_dir(cls):
        """Get platform-specific config directory."""
        platform = cls.detect_platform()
        
        if platform == cls.PLATFORM_WINDOWS:
            base = Path.home() / "AppData" / "Local" / "RPGBot"
        elif platform == cls.PLATFORM_TERMUX:
            base = Path.home() / ".rpgbot"
        elif platform == cls.PLATFORM_LINUX:
            base = Path.home() / ".config" / "rpgbot"
        else:
            base = Path.home() / ".rpgbot"
        
        base.mkdir(parents=True, exist_ok=True)
        return base

    @classmethod
    def get_logs_dir(cls):
        """Get platform-specific logs directory."""
        logs = cls.get_config_dir() / "logs"
        logs.mkdir(parents=True, exist_ok=True)
        return logs

    @classmethod
    def get_data_dir(cls):
        """Get platform-specific data directory."""
        platform = cls.detect_platform()
        
        if platform == cls.PLATFORM_WINDOWS:
            base = Path.home() / "AppData" / "Local" / "RPGBot" / "data"
        elif platform == cls.PLATFORM_TERMUX:
            base = Path.home() / "rpgbot_data"
        elif platform == cls.PLATFORM_LINUX:
            base = Path.home() / ".local" / "share" / "rpgbot"
        else:
            base = Path.home() / ".rpgbot" / "data"
        
        base.mkdir(parents=True, exist_ok=True)
        return base


class PlatformCapabilities:
    """Check platform capabilities and features."""

    @classmethod
    def supports_gui(cls):
        """Check if platform supports GUI/display."""
        # Windows/Linux can use display
        # Android/Termux limited
        return PlatformDetector.is_windows() or PlatformDetector.is_linux()

    @classmethod
    def supports_native_browser(cls):
        """Check if platform supports launching native browser."""
        return PlatformDetector.is_windows() or PlatformDetector.is_linux()

    @classmethod
    def supports_cdp_remote(cls):
        """Check if platform supports CDP remote debugging."""
        # Android can use CDP
        return PlatformDetector.is_termux()

    @classmethod
    def supports_subprocess(cls):
        """Check if platform supports subprocess for browser launch."""
        return PlatformDetector.is_windows() or PlatformDetector.is_linux()

    @classmethod
    def get_available_browser_modes(cls):
        """Get available browser modes for platform."""
        modes = []
        
        if cls.supports_native_browser():
            modes.append("launch")
        
        if cls.supports_cdp_remote():
            modes.append("cdp_remote")
        
        modes.append("attach")
        
        return modes

    @classmethod
    def get_setup_requirements(cls):
        """Get setup requirements for platform."""
        platform = PlatformDetector.detect_platform()
        
        if platform == PlatformDetector.PLATFORM_WINDOWS:
            return {
                "os": "Windows 10+",
                "python": "3.8+",
                "browsers": ["Brave", "Chrome", "Chromium"],
                "selenium": "4.0+",
                "required_packages": ["selenium", "requests"],
            }
        elif platform == PlatformDetector.PLATFORM_TERMUX:
            return {
                "os": "Android 6.0+",
                "termux": "Required",
                "python": "3.8+",
                "browsers": ["Chrome", "Brave", "Chromium (Termux)"],
                "selenium": "4.0+",
                "required_packages": ["selenium", "requests"],
            }
        elif platform == PlatformDetector.PLATFORM_LINUX:
            return {
                "os": "Linux",
                "python": "3.8+",
                "browsers": ["Brave", "Chrome", "Chromium"],
                "selenium": "4.0+",
                "required_packages": ["selenium", "requests"],
            }
        else:
            return {}

