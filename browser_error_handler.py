"""
Browser Error Handler & Edge Cases

Comprehensive error handling for browser-related issues.
Provides recovery strategies and helpful error messages.
"""

import time


class BrowserErrorHandler:
    """Handle browser-related errors gracefully."""

    ERROR_STRATEGIES = {
        "browser_not_found": {
            "message": "Browser executable not found",
            "recovery": [
                "Install the browser (Brave/Chrome/Chromium)",
                "Check Settings → Browser Settings",
                "Use auto-detect to find available browsers",
            ],
        },
        "port_in_use": {
            "message": "Chrome DevTools port already in use",
            "recovery": [
                "Kill existing processes: adb shell pkill -f chrome",
                "Try different port: adb forward tcp:9223 localabstract:chrome_devtools_remote",
                "Wait a few seconds and retry",
            ],
        },
        "device_not_found": {
            "message": "Android device not found via ADB",
            "recovery": [
                "Connect device via USB cable",
                "Enable USB debugging: Settings → Developer Options",
                "Run: adb devices (verify device is listed)",
            ],
        },
        "cdp_connection_failed": {
            "message": "Failed to connect via Chrome DevTools Protocol",
            "recovery": [
                "Ensure Chrome/Brave is open on device",
                "Verify CDP forwarding: adb forward tcp:9222 localabstract:chrome_devtools_remote",
                "Check device is not in sleep mode",
            ],
        },
        "profile_corrupted": {
            "message": "Browser profile is corrupted",
            "recovery": [
                "Profile will be restored from backup if available",
                "Or clear profile: Settings → Clear cache",
                "Or use new profile: Settings → Browser Settings",
            ],
        },
        "timeout": {
            "message": "Browser operation timed out",
            "recovery": [
                "Slow network or device issue",
                "Try again with more time",
                "Check device performance",
            ],
        },
    }

    @classmethod
    def handle_error(cls, error_type, details=None):
        """Handle and display browser error with recovery suggestions."""
        
        error_info = cls.ERROR_STRATEGIES.get(
            error_type,
            {"message": str(error_type), "recovery": []},
        )
        
        print()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║                    BROWSER ERROR                             ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
        print(f"Error: {error_info['message']}")
        
        if details:
            print(f"Details: {details}")
        
        print()
        print("Recovery options:")
        print("─" * 63)
        
        for i, strategy in enumerate(error_info["recovery"], 1):
            print(f"  {i}. {strategy}")
        
        print()
        print("═" * 63)
        print()

    @classmethod
    def retry_with_backoff(cls, func, max_retries=3, backoff_factor=2, timeout=30):
        """Retry function with exponential backoff."""
        
        for attempt in range(max_retries):
            try:
                return func()
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                wait_time = backoff_factor ** attempt
                print(f"Attempt {attempt + 1} failed, retrying in {wait_time}s...")
                time.sleep(wait_time)
        
        raise Exception("Max retries exceeded")


class BrowserEdgeCases:
    """Handle edge cases in browser automation."""

    @staticmethod
    def handle_missing_browser(browser_name):
        """Handle when browser is not installed."""
        print()
        print(f"Browser not found: {browser_name}")
        print()
        print("Options:")
        print("  1. Install the browser")
        print("  2. Use Settings → Browser Settings → Auto Detect")
        print("  3. Switch to a different browser")
        print()
        
        return False

    @staticmethod
    def handle_port_conflict(port=9222):
        """Handle when CDP port is in use."""
        print()
        print(f"Port {port} is already in use")
        print()
        print("Try these commands:")
        print(f"  adb shell pkill -f chrome")
        print(f"  adb forward --remove tcp:{port}")
        print(f"  adb forward tcp:{port+1} localabstract:chrome_devtools_remote")
        print()
        
        return False

    @staticmethod
    def handle_no_devices():
        """Handle when no Android devices are connected."""
        print()
        print("No Android devices found via ADB")
        print()
        print("Setup:")
        print("  1. Connect device via USB cable")
        print("  2. Enable USB debugging in Settings → Developer Options")
        print("  3. Run: adb devices (to verify)")
        print()
        
        return False

    @staticmethod
    def handle_slow_browser():
        """Handle when browser is responding slowly."""
        print()
        print("Browser is responding slowly")
        print()
        print("Troubleshooting:")
        print("  • Check device CPU/memory usage")
        print("  • Close other apps")
        print("  • Check network connection")
        print("  • Increase timeouts in Settings")
        print()
        
        return False

    @staticmethod
    def handle_intermittent_failures(operation_name):
        """Handle intermittent failures with retry logic."""
        print()
        print(f"Intermittent failure in: {operation_name}")
        print()
        print("Automatically retrying with backoff...")
        print()
        
        return True

    @staticmethod
    def handle_profile_issues(instance_name):
        """Handle browser profile issues."""
        from session_manager import ProfileRecovery
        
        print()
        print(f"Browser profile issue for: {instance_name}")
        print()
        
        # Try to detect corruption
        profile_path = f"~/.chromium_profile"  # Placeholder
        
        if ProfileRecovery.detect_corruption(profile_path):
            print("Profile appears corrupted (lock files detected)")
            print("Cleaning up lock files...")
            ProfileRecovery.cleanup_locks(profile_path)
            print("✓ Lock files removed, try again")
        
        print()
        
        return True


class BrowserTimeout:
    """Handle browser operation timeouts."""

    DEFAULT_TIMEOUT = 30  # seconds
    LONG_TIMEOUT = 60
    SHORT_TIMEOUT = 10

    @staticmethod
    def get_timeout_for_operation(operation):
        """Get appropriate timeout for operation."""
        timeouts = {
            "launch": 30,
            "navigate": 30,
            "screenshot": 10,
            "find_element": 10,
            "click": 10,
            "type": 10,
            "wait": 60,
        }
        
        return timeouts.get(operation, BrowserTimeout.DEFAULT_TIMEOUT)

    @staticmethod
    def handle_timeout(operation, timeout_seconds):
        """Handle timeout during operation."""
        print()
        print(f"Timeout: {operation} took longer than {timeout_seconds}s")
        print()
        print("Possible causes:")
        print("  • Slow network connection")
        print("  • Device is busy/slow")
        print("  • Website not responding")
        print("  • Browser crashed")
        print()
        
        return False

