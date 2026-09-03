"""
Android/Termux Browser Backend

Provides browser control for Android via Termux and CDP (Chrome DevTools Protocol).
Supports remote debugging and browser automation on Android devices.
"""

from pathlib import Path
from selenium.webdriver.chrome.options import Options as ChromeOptions
import subprocess
import time


class AndroidBrowserManager:
    """Manage browser instances on Android via Termux."""

    @staticmethod
    def find_termux_chromium():
        """Find Chromium installed via Termux package manager."""
        termux_chromium = Path("/data/data/com.termux/files/usr/bin/chromium")
        
        if termux_chromium.exists():
            return termux_chromium
        
        # Check alternative paths
        alt_paths = [
            Path("/data/data/com.termux/files/usr/bin/chrome"),
            Path("/data/data/com.termux/files/home/chromium"),
        ]
        
        for path in alt_paths:
            if path.exists():
                return path
        
        return None

    @staticmethod
    def find_device_chrome():
        """Find Chrome installed on Android device."""
        chrome_paths = [
            "/data/app/com.android.chrome-*/lib/arm64/libchrome.so",
            "/data/data/com.android.chrome/",
            "/system/app/Chrome/",
            "/system/app/Chrome/Chrome.apk",
        ]
        
        for path in chrome_paths:
            p = Path(path)
            if p.exists():
                return p
        
        return None

    @staticmethod
    def find_device_brave():
        """Find Brave installed on Android device."""
        brave_paths = [
            "/data/app/com.brave.browser-*/lib/arm64/libchrome.so",
            "/data/data/com.brave.browser/",
            "/system/app/Brave/",
            "/system/app/Brave/Brave.apk",
        ]
        
        for path in brave_paths:
            p = Path(path)
            if p.exists():
                return p
        
        return None

    @staticmethod
    def setup_cdp_forwarding(device_port=9222, local_port=9222):
        """
        Setup Chrome DevTools Protocol forwarding via ADB.
        
        Requires:
        - Android device with Chrome/Brave
        - USB debugging enabled
        - ADB installed
        - Device connected via USB
        """
        try:
            # Forward device port to local
            subprocess.run(
                ["adb", "forward", 
                 f"tcp:{local_port}", 
                 f"localabstract:chrome_devtools_remote"],
                timeout=10,
                check=True,
            )
            
            return {
                "success": True,
                "url": f"http://127.0.0.1:{local_port}",
            }
        
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            return {
                "success": False,
                "error": str(e),
                "help": "Install ADB and enable USB debugging on device",
            }

    @staticmethod
    def create_cdp_driver(remote_url):
        """
        Create Selenium WebDriver via Chrome DevTools Protocol.
        
        Used to connect to running Chrome/Brave on Android device.
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
            
            caps = DesiredCapabilities.CHROME.copy()
            
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
                "help": "Ensure Chrome on device is running and accessible",
            }

    @staticmethod
    def start_chrome_debugging_mode():
        """
        Instructions to start Chrome in debugging mode on Android.
        
        For use with CDP remote debugging.
        """
        return """
STARTING CHROME IN DEBUGGING MODE ON ANDROID
═══════════════════════════════════════════════════════════════

1. Enable Developer Options
   • Go to Settings → About Phone
   • Tap "Build Number" 7 times
   • Back to Settings, find "Developer Options"

2. Enable USB Debugging
   • Settings → Developer Options → USB Debugging
   • Toggle ON
   • Connect to computer via USB

3. Start Chrome with debugging
   • Open Chrome on device
   • Or use ADB: adb shell am start -n com.android.chrome/.MainActivity

4. Verify connection
   $ adb forward tcp:9222 localabstract:chrome_devtools_remote
   $ curl http://127.0.0.1:9222/json
   (Should return list of open pages)

5. Connect via Selenium
   driver = webdriver.Remote(
       command_executor="http://127.0.0.1:9222",
       desired_capabilities=DesiredCapabilities.CHROME,
   )

═══════════════════════════════════════════════════════════════
"""


class AndroidBrowserOptions:
    """Chrome options optimized for Android."""

    @staticmethod
    def get_cdp_options():
        """Get Chrome options for CDP remote debugging."""
        options = ChromeOptions()
        
        # Disable headless (device browser is GUI)
        # options.add_argument("--headless")  # NOT for Android
        
        # Mobile user agent
        options.add_argument(
            "user-agent=Mozilla/5.0 (Linux; Android 11) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/91.0.4472.77 Mobile Safari/537.36"
        )
        
        # Optimize for mobile
        options.add_argument("--disable-gpu")
        options.add_argument("--no-first-run")
        options.add_argument("--no-default-browser-check")
        
        # Performance
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        
        return options

    @staticmethod
    def get_termux_chromium_options():
        """Get Chrome options for Termux Chromium."""
        options = ChromeOptions()
        
        # Termux Chromium options
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        
        options.add_argument(
            f"--user-data-dir={Path.home() / '.chromium_profile'}"
        )
        
        # Display settings for Termux X11
        options.add_argument("--disable-gpu")
        
        return options


class AndroidSetup:
    """Android/Termux setup utilities."""

    @staticmethod
    def get_cdp_setup_guide():
        """Get complete CDP remote debugging setup guide."""
        return """
ANDROID CHROMIUM + CDP REMOTE DEBUGGING SETUP
═══════════════════════════════════════════════════════════════

REQUIREMENTS
───────────────────────────────────────────────────────────────
• Android 6.0+
• Chrome or Brave installed on device
• USB cable or same-network connection
• ADB installed on computer
• Termux (optional, for local Chromium)

SETUP STEPS
───────────────────────────────────────────────────────────────

Option A: Device Chrome via USB Debugging
───────────────────────────────────────────
1. Connect device via USB
2. Enable USB debugging on device
3. Run: adb forward tcp:9222 localabstract:chrome_devtools_remote
4. Open Chrome on device
5. RPGBot uses: BrowserManager.create(account, browser="android-cdp")

Option B: Device Chrome via Network (Same Wi-Fi)
────────────────────────────────────────────────
1. Device and computer on same Wi-Fi
2. Get device IP: Settings → Wi-Fi → [connected] → IP
3. Start Chrome on device with debugging
4. Forward: adb connect <device-ip>:5555
5. Forward: adb forward tcp:9222 localabstract:chrome_devtools_remote
6. RPGBot uses: BrowserManager.create(account, browser="android-cdp")

Option C: Termux Chromium (Local)
─────────────────────────────────
1. Install Termux
2. pkg install chromium
3. RPGBot uses: BrowserManager.create(account, browser="termux")

TROUBLESHOOTING
───────────────────────────────────────────────────────────────
Q: "adb: device not found"
A: • Check USB cable connection
  • Enable USB debugging in Settings
  • Install ADB drivers if needed

Q: "Chrome not responding"
A: • Ensure Chrome is open on device
  • Try restarting Chrome
  • Check network connection for Wi-Fi mode

Q: "CDP port 9222 not accessible"
A: • Verify forward command succeeded
  • Check firewall settings
  • Try different port: adb forward tcp:9223 localabstract:chrome_devtools_remote

═══════════════════════════════════════════════════════════════
"""

