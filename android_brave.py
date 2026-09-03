"""
Brave Browser on Android Support

Provides specific support for Brave browser on Android devices
via CDP (Chrome DevTools Protocol) remote debugging.
"""

from pathlib import Path
import subprocess


class AndroidBraveManager:
    """Manage Brave browser instances on Android."""

    BRAVE_PACKAGE = "com.brave.browser"
    BRAVE_DEBUG_SOCKET = "localabstract:chrome_devtools_remote"

    @staticmethod
    def is_brave_installed():
        """Check if Brave is installed on Android device."""
        try:
            result = subprocess.run(
                ["adb", "shell", "pm", "list", "packages"],
                capture_output=True,
                timeout=10,
                text=True,
            )
            return AndroidBraveManager.BRAVE_PACKAGE in result.stdout
        except Exception:
            return False

    @staticmethod
    def start_brave_debug_mode():
        """Start Brave in debug mode via ADB."""
        try:
            # Start Brave with debugging enabled
            subprocess.run(
                ["adb", "shell", "am", "start", 
                 "-n", f"{AndroidBraveManager.BRAVE_PACKAGE}/com.brave.browser.BraveActivity"],
                capture_output=True,
                timeout=10,
            )
            
            # Wait for Brave to start
            import time
            time.sleep(3)
            
            return {
                "success": True,
                "message": "Brave started in debug mode",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def setup_brave_cdp_forwarding(local_port=9222):
        """Setup CDP forwarding for Brave on Android."""
        try:
            # Kill existing processes
            subprocess.run(
                ["adb", "shell", "pkill", "-f", "Brave"],
                capture_output=True,
                timeout=5,
            )
            
            # Start Brave in debug mode
            start_result = AndroidBraveManager.start_brave_debug_mode()
            if not start_result["success"]:
                return start_result
            
            # Forward CDP port
            subprocess.run(
                ["adb", "forward",
                 f"tcp:{local_port}",
                 f"localabstract:chrome_devtools_remote"],
                check=True,
                timeout=10,
            )
            
            return {
                "success": True,
                "url": f"http://127.0.0.1:{local_port}",
                "message": "Brave CDP forwarding ready",
            }
        
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "help": "Ensure ADB is installed and device is connected",
            }

    @staticmethod
    def create_brave_cdp_driver(remote_url):
        """Create Selenium WebDriver for Brave on Android via CDP."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            
            # Brave uses same Chrome protocol
            caps = DesiredCapabilities.CHROME.copy()
            caps["browserName"] = "brave"
            
            driver = webdriver.Remote(
                command_executor=remote_url,
                desired_capabilities=caps,
            )
            
            return {
                "success": True,
                "driver": driver,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "help": "Ensure Brave is running on device and accessible via CDP",
            }

    @staticmethod
    def get_brave_cdp_setup_guide():
        """Get Brave-specific CDP setup guide."""
        return """
BRAVE BROWSER ON ANDROID - CDP SETUP
════════════════════════════════════════════════════════════════

REQUIREMENTS
────────────────────────────────────────────────────────────────
• Android 6.0+
• Brave browser installed on device
• USB cable for debugging
• ADB installed on computer
• RPGBot installed on computer

SETUP STEPS
────────────────────────────────────────────────────────────────

1. ENABLE USB DEBUGGING ON DEVICE
   • Settings → About Phone
   • Tap "Build Number" 7 times
   • Settings → Developer Options
   • Enable "USB Debugging"
   • Connect device via USB

2. INSTALL BRAVE ON DEVICE
   • Open Google Play Store on device
   • Search for "Brave"
   • Install "Brave Browser by Brave Software"

3. SET UP ADB FORWARDING
   $ adb devices  (verify device is listed)
   $ adb forward tcp:9222 localabstract:chrome_devtools_remote

4. CONFIGURE RPGBOT
   • Settings → Browser Settings
   • Select "Browser": android-brave
   • Select "Platform": android
   • Select "Mode": cdp-remote

5. RUN RPGBOT
   $ python main.py
   • Select account
   • Bot will:
     - Start Brave on device
     - Connect via CDP
     - Perform automation

TROUBLESHOOTING
────────────────────────────────────────────────────────────────

Q: "adb: device not found"
A: • Ensure USB debugging is enabled
  • Try: adb kill-server && adb start-server
  • Reconnect USB cable
  • Install Android SDK platform tools

Q: "Brave not found"
A: • Download and install Brave from Play Store
  • Verify: adb shell pm list packages | grep brave

Q: "CDP port 9222 not accessible"
A: • Verify forward: adb forward --list
  • Clear: adb forward --remove tcp:9222
  • Retry: adb forward tcp:9222 localabstract:chrome_devtools_remote
  • Kill Brave: adb shell pkill -f Brave
  • Restart Brave manually on device

Q: "Connection refused"
A: • Ensure Brave is open on device
  • Try: adb shell am start -n com.brave.browser/com.brave.browser.BraveActivity
  • Wait 5 seconds for Brave to fully start
  • Retry connection

ADVANCED
────────────────────────────────────────────────────────────────

Use Network Debugging (No USB Cable):
1. Enable network debugging in Brave developer options
2. Get device IP: Settings → Wi-Fi → [connected network] → IP
3. Connect: adb connect <device-ip>:5555
4. Forward: adb forward tcp:9222 localabstract:chrome_devtools_remote

Persistent CDP Connection:
• Keep Brave running in background
• No need to restart for each bot run
• Multiple accounts can use same Brave instance

════════════════════════════════════════════════════════════════
"""


class BraveAndroidOptions:
    """Chrome options optimized for Brave on Android."""

    @staticmethod
    def get_options():
        """Get Chrome options for Brave on Android."""
        from selenium.webdriver.chrome.options import Options
        
        options = Options()
        
        # Mobile user agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 11) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Brave/1.43.93 Chrome/106.0.0.0 Mobile Safari/537.36"
        )
        
        # Disable headless (mobile browser is GUI)
        # Mobile-specific options
        options.add_argument("--disable-gpu")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        
        # Performance optimization
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        return options

