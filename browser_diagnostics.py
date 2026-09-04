"""
Browser Diagnostics Module

Tests browser environment and WebDriver connectivity.
Helps users troubleshoot browser-related issues.
"""

import sys
import platform

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"
GRAY = "\033[90m"


class DiagnosticsManager:
    """Manage and run browser diagnostics."""

    @classmethod
    def run_full_diagnostics(cls):
        """Run all diagnostics and display results."""
        
        results = {
            "python": cls.check_python(),
            "selenium": cls.check_selenium(),
            "browser_detection": cls.check_browser_detection(),
            "webdriver": cls.check_webdriver(),
        }
        
        cls.format_and_display_results(results)

    @classmethod
    def check_python(cls):
        """Check Python version and environment."""
        
        result = {
            "version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "platform": platform.platform(),
            "executable": sys.executable,
            "status": "ok",
        }
        
        # Check if Python 3.x
        if sys.version_info.major < 3:
            result["status"] = "error"
            result["error"] = "Python 3.x required"
        
        return result

    @classmethod
    def check_selenium(cls):
        """Check Selenium installation and availability."""
        
        result = {
            "installed": False,
            "version": None,
            "status": "error",
            "error": "Selenium not installed",
        }
        
        try:
            import selenium
            from selenium import webdriver
            
            result["installed"] = True
            result["version"] = selenium.__version__
            result["status"] = "ok"
            result["error"] = None
            
            # Check WebDriver availability
            try:
                from selenium.webdriver.chrome.options import Options
                result["options_available"] = True
            except ImportError:
                result["options_available"] = False
                result["status"] = "warning"
                result["error"] = "Chrome options not available"
        
        except ImportError:
            pass
        
        return result

    @classmethod
    def check_browser_detection(cls):
        """Check which browsers can be detected."""
        
        result = {
            "brave": {"found": False, "path": None},
            "chrome": {"found": False, "path": None},
            "chromium": {"found": False, "path": None},
            "auto": {"found": False, "which": None},
            "status": "ok",
        }
        
        try:
            from browser import (
                find_brave,
                find_chrome,
                find_chromium,
                find_browser,
            )
            
            # Test Brave
            try:
                path = find_brave()
                result["brave"]["found"] = True
                result["brave"]["path"] = str(path)
            except FileNotFoundError:
                pass
            
            # Test Chrome
            try:
                path = find_chrome()
                result["chrome"]["found"] = True
                result["chrome"]["path"] = str(path)
            except FileNotFoundError:
                pass
            
            # Test Chromium
            try:
                path = find_chromium()
                result["chromium"]["found"] = True
                result["chromium"]["path"] = str(path)
            except FileNotFoundError:
                pass
            
            # Test auto-detect
            try:
                path = find_browser("auto")
                result["auto"]["found"] = True
                # Determine which browser was found
                if result["brave"]["found"] and result["brave"]["path"] == str(path):
                    result["auto"]["which"] = "brave"
                elif result["chrome"]["found"] and result["chrome"]["path"] == str(path):
                    result["auto"]["which"] = "chrome"
                elif result["chromium"]["found"] and result["chromium"]["path"] == str(path):
                    result["auto"]["which"] = "chromium"
            except FileNotFoundError:
                result["auto"]["found"] = False
                result["auto"]["error"] = "No browsers found"
                result["status"] = "error"
        
        except ImportError as e:
            result["status"] = "error"
            result["error"] = f"Failed to import browser module: {e}"
        
        return result

    @classmethod
    def check_webdriver(cls):
        """Check WebDriver creation (mock, no actual launch)."""
        
        result = {
            "brave": {"ok": False, "error": None},
            "chrome": {"ok": False, "error": None},
            "chromium": {"ok": False, "error": None},
            "status": "ok",
        }
        
        try:
            from selenium.webdriver.chrome.options import Options
            from browser import find_brave, find_chrome, find_chromium
            
            # Test Brave
            try:
                find_brave()
                options = Options()
                result["brave"]["ok"] = True
            except FileNotFoundError:
                result["brave"]["error"] = "Brave not found"
            except Exception as e:
                result["brave"]["error"] = str(e)
            
            # Test Chrome
            try:
                find_chrome()
                options = Options()
                result["chrome"]["ok"] = True
            except FileNotFoundError:
                result["chrome"]["error"] = "Chrome not found"
            except Exception as e:
                result["chrome"]["error"] = str(e)
            
            # Test Chromium
            try:
                find_chromium()
                options = Options()
                result["chromium"]["ok"] = True
            except FileNotFoundError:
                result["chromium"]["error"] = "Chromium not found"
            except Exception as e:
                result["chromium"]["error"] = str(e)
        
        except ImportError as e:
            result["status"] = "error"
            result["error"] = f"Failed to import: {e}"
        
        return result

    @classmethod
    def format_and_display_results(cls, results):
        """Format and display diagnostic results."""
        
        # Header
        print()
        print(f"{BOLD}╔{'═' * 73}╗{RESET}")
        print(f"{BOLD}║ {' ' * 20}BROWSER DIAGNOSTICS{' ' * 32}║{RESET}")
        print(f"{BOLD}╚{'═' * 73}╝{RESET}")
        print()
        
        # Python Environment
        cls._display_section("PYTHON ENVIRONMENT", results["python"])
        
        # Selenium
        cls._display_section("SELENIUM", results["selenium"])
        
        # Browser Detection
        cls._display_section("BROWSER DETECTION", results["browser_detection"])
        
        # WebDriver
        cls._display_section("WEBDRIVER TESTING (No Launch)", results["webdriver"])
        
        # Summary
        cls._display_summary(results)
        
        print()

    @classmethod
    def _display_section(cls, title, data):
        """Display a section of results."""
        
        print(f"{BOLD}{title}{RESET}")
        print(f"{GRAY}{'─' * 75}{RESET}")
        
        if isinstance(data, dict):
            for key, value in data.items():
                if key == "status":
                    continue
                if key == "error" and value:
                    print(f"  {RED}✗ {value}{RESET}")
                elif isinstance(value, dict):
                    # Nested dictionary
                    if "found" in value:  # Browser detection
                        status = "✓" if value.get("found") else "✗"
                        color = GREEN if value.get("found") else RED
                        browser_name = key.title()
                        if status == "✓":
                            path = value.get("path", "").split("\\")[-1]
                            print(f"  {color}{status} {browser_name}{RESET}")
                        else:
                            print(f"  {color}{status} {browser_name} not found{RESET}")
                    elif "ok" in value:  # WebDriver
                        status = "✓" if value.get("ok") else "✗"
                        color = GREEN if value.get("ok") else RED
                        browser_name = key.title()
                        if status == "✓":
                            print(f"  {color}{status} {browser_name}: WebDriver ready{RESET}")
                        else:
                            error = value.get("error", "Unknown error")
                            print(f"  {color}{status} {browser_name}: {error}{RESET}")
                elif value and key != "version":
                    print(f"  {GREEN}✓ {key.title()}: {value}{RESET}")
                elif key == "version" and value:
                    print(f"  {GREEN}✓ Version {value}{RESET}")
        
        print()

    @classmethod
    def _display_summary(cls, results):
        """Display summary and recommendations."""
        
        print(f"{BOLD}SUMMARY{RESET}")
        print(f"{GRAY}{'─' * 75}{RESET}")
        
        # Count available browsers
        browser_detection = results["browser_detection"]
        available = sum(
            1 for key in ["brave", "chrome", "chromium"]
            if browser_detection.get(key, {}).get("found", False)
        )
        
        print(f"  Available browsers: {available} of 3")
        
        if not browser_detection.get("auto", {}).get("found", False):
            print(f"  {RED}✗ Auto-detect found no browsers{RESET}")
        else:
            which = browser_detection.get("auto", {}).get("which", "unknown")
            print(f"  {GREEN}✓ Auto-detect would use: {which.title()}{RESET}")
        
        print()
        print(f"{BOLD}RECOMMENDATIONS{RESET}")
        print(f"{GRAY}{'─' * 75}{RESET}")
        
        if available == 0:
            print(f"  {RED}✗ No browsers found! Install at least one of:{RESET}")
            print(f"    • Brave: https://brave.com/")
            print(f"    • Chrome: https://google.com/chrome/")
            print(f"    • Chromium: https://www.chromium.org/")
        elif available == 1:
            print(f"  {YELLOW}⚠ Only 1 browser available. Consider installing others for backup.{RESET}")
        else:
            print(f"  {GREEN}✓ Multiple browsers available. You're good to go!{RESET}")
        
        print(f"  → Use Settings → Browser Settings to select which browser to use")
        print()
        print(f"{BOLD}{'═' * 75}{RESET}")
        print()


def run_diagnostics():
    """Run full browser diagnostics."""
    DiagnosticsManager.run_full_diagnostics()


if __name__ == "__main__":
    run_diagnostics()

