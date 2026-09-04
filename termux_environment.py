"""
Termux Environment Detection and Setup

Detects and validates Termux/Android environment for bot deployment.
Provides tools for environment configuration and validation.
"""

import sys
import os
import subprocess
import platform
from pathlib import Path


class TermuxEnvironment:
    """Manage Termux environment detection and validation."""

    @staticmethod
    def is_termux():
        """Check if running in Termux environment."""
        return os.path.exists("/data/data/com.termux")

    @staticmethod
    def is_android():
        """Check if running on Android."""
        return platform.system() == "Linux" and TermuxEnvironment.is_termux()

    @staticmethod
    def get_termux_home():
        """Get Termux home directory."""
        if TermuxEnvironment.is_termux():
            return os.path.expanduser("~")
        return None

    @staticmethod
    def get_termux_storage():
        """Get Termux storage directory (shared with device)."""
        if TermuxEnvironment.is_termux():
            return os.path.expanduser("~/storage/shared")
        return None

    @staticmethod
    def get_termux_downloads():
        """Get Termux downloads directory."""
        if TermuxEnvironment.is_termux():
            return os.path.expanduser("~/storage/downloads")
        return None

    @staticmethod
    def check_termux_packages():
        """Check which required packages are installed."""
        if not TermuxEnvironment.is_termux():
            return {
                "status": "not_termux",
                "packages": {}
            }

        required = ["python", "chromium", "curl", "git"]
        packages = {}

        for pkg in required:
            try:
                result = subprocess.run(
                    ["dpkg", "-l", pkg],
                    capture_output=True,
                    timeout=5,
                )
                packages[pkg] = result.returncode == 0
            except Exception:
                packages[pkg] = False

        return {
            "status": "ok",
            "packages": packages,
        }

    @staticmethod
    def check_python():
        """Check Python installation and version."""
        return {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "executable": sys.executable,
            "path": sys.executable,
        }

    @staticmethod
    def check_chromium():
        """Check Chromium availability on Termux/Android."""
        if not TermuxEnvironment.is_termux():
            return {"found": False, "reason": "Not in Termux"}

        chromium_paths = [
            Path("/system/app/Chromium"),
            Path("/system/app/Chrome"),
            Path("/data/app/*/com.android.chrome"),
            Path("/data/data/com.android.chrome"),
        ]

        for path in chromium_paths:
            if path.exists() or str(path).startswith("/data/app"):
                try:
                    if "*" in str(path):
                        # Handle wildcard path
                        base = str(path).split("*")[0]
                        if Path(base).parent.exists():
                            return {
                                "found": True,
                                "path": str(path),
                                "type": "android_chrome"
                            }
                    elif path.exists():
                        return {
                            "found": True,
                            "path": str(path),
                            "type": "system_chrome"
                        }
                except Exception:
                    pass

        return {"found": False, "reason": "Chromium not found"}

    @staticmethod
    def check_brave_android():
        """Check for Brave browser on Android."""
        if not TermuxEnvironment.is_termux():
            return {"found": False, "reason": "Not in Termux"}

        brave_paths = [
            Path("/system/app/Brave"),
            Path("/data/app/*/com.brave.browser"),
            Path("/data/data/com.brave.browser"),
        ]

        for path in brave_paths:
            if path.exists() or str(path).startswith("/data/app"):
                try:
                    if "*" in str(path):
                        base = str(path).split("*")[0]
                        if Path(base).parent.exists():
                            return {
                                "found": True,
                                "path": str(path),
                                "type": "android_brave"
                            }
                    elif path.exists():
                        return {
                            "found": True,
                            "path": str(path),
                            "type": "system_brave"
                        }
                except Exception:
                    pass

        return {"found": False, "reason": "Brave not found"}

    @staticmethod
    def validate_environment():
        """Complete environment validation."""
        return {
            "is_termux": TermuxEnvironment.is_termux(),
            "is_android": TermuxEnvironment.is_android(),
            "python": TermuxEnvironment.check_python(),
            "packages": TermuxEnvironment.check_termux_packages(),
            "chromium": TermuxEnvironment.check_chromium(),
            "brave": TermuxEnvironment.check_brave_android(),
            "home": TermuxEnvironment.get_termux_home(),
            "storage": TermuxEnvironment.get_termux_storage(),
        }


class TermuxSetup:
    """Termux setup and configuration utilities."""

    @staticmethod
    def get_setup_instructions():
        """Get Termux setup instructions."""
        return """
TERMUX SETUP INSTRUCTIONS
═════════════════════════════════════════════════════════════════

1. Install Termux
   • Download from F-Droid or GitHub
   • Install on your Android device

2. Update packages
   $ pkg update
   $ pkg upgrade

3. Install Python
   $ pkg install python

4. Install Selenium dependencies
   $ pkg install python-pip
   $ pip install selenium

5. Clone RPGBot repository
   $ cd ~
   $ git clone https://github.com/CountKrampus/rpgbot.git
   $ cd rpgbot

6. Install RPGBot dependencies
   $ pip install -r requirements.txt

7. Setup browser (choose one):
   Option A: Install Termux-based headless Chromium
     $ pkg install chromium
     # RPGBot starts Chromium with DevTools and connects Selenium
     # automatically; no Android GUI or X11 session is required.

   Option B: Use device's Chrome/Brave via CDP
     • Requires device to have Chrome or Brave installed
     • Requires USB debugging or same-network debugging

8. Configure and run
   $ python main.py

TROUBLESHOOTING
───────────────────────────────────────────────────────────────
• Permission denied: Use 'chmod +x' on scripts
• Storage access: Grant storage permissions when prompted
• Browser not found: Run 'pkg install chromium' and select
  'Termux Chromium (headless)' in System Settings
• CDP connection: Enable USB debugging and use 'adb'

═════════════════════════════════════════════════════════════════
"""

    @staticmethod
    def get_requirements_txt():
        """Get requirements.txt for Termux."""
        return """
# RPGBot Requirements for Termux/Android

selenium>=4.0.0
requests>=2.25.0
beautifulsoup4>=4.9.0
lxml>=4.6.0

# Optional but recommended
pyautogui>=0.9.50
Pillow>=8.0.0
"""

    @staticmethod
    def create_setup_script():
        """Generate setup script for Termux."""
        script = """#!/bin/bash
# RPGBot Termux Setup Script

echo "RPGBot Termux Setup"
echo "===================="
echo ""

# Update packages
echo "Updating packages..."
pkg update -y
pkg upgrade -y

# Install Python
echo "Installing Python..."
pkg install python -y

# Install pip
echo "Installing pip..."
pkg install python-pip -y

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Optional: Install Chromium
read -p "Install Termux-based Chromium? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing Chromium..."
    pkg install chromium -y
fi

# Setup storage access
echo "Setting up storage access..."
mkdir -p ~/storage/shared
mkdir -p ~/storage/downloads

echo ""
echo "Setup complete!"
echo "Run: python ~/rpgbot/main.py"
"""
        return script


def get_termux_diagnostics():
    """Run Termux environment diagnostics."""
    return TermuxEnvironment.validate_environment()
