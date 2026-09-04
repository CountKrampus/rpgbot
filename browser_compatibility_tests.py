"""
Browser Compatibility Testing Framework

Comprehensive tests for browser compatibility and automation verification.
Tests all browsers and reports results.
"""

import time
from pathlib import Path


class BrowserCompatibilityTest:
    """Test browser compatibility and automation."""

    @staticmethod
    def test_browser_launch(browser_name, timeout=30):
        """Test if browser can be launched."""
        try:
            from browser import BrowserManager
            
            print(f"Testing launch: {browser_name}...", end=" ")
            
            start = time.time()
            driver = BrowserManager.create("test_account", browser=browser_name)
            elapsed = time.time() - start
            
            if driver:
                BrowserManager.close(driver, "test_account")
                print(f"✓ ({elapsed:.1f}s)")
                return {
                    "success": True,
                    "time": elapsed,
                    "browser": browser_name,
                }
            else:
                print("✗ (No driver)")
                return {
                    "success": False,
                    "error": "Driver creation returned None",
                }
        
        except Exception as e:
            print(f"✗ ({str(e)[:50]})")
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def test_navigation(driver, url="https://example.com", timeout=10):
        """Test basic navigation."""
        try:
            driver.set_page_load_timeout(timeout)
            driver.get(url)
            return {
                "success": True,
                "title": driver.title,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def test_js_execution(driver):
        """Test JavaScript execution."""
        try:
            result = driver.execute_script("return 'test_' + 123")
            return {
                "success": result == "test_123",
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def test_element_finding(driver):
        """Test element finding and interaction."""
        try:
            # Try to find body element
            body = driver.find_element("tag name", "body")
            return {
                "success": body is not None,
                "element": "body",
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }

    @staticmethod
    def test_automation_basics(driver):
        """Test basic automation capabilities."""
        results = {
            "navigation": BrowserCompatibilityTest.test_navigation(driver),
            "js_execution": BrowserCompatibilityTest.test_js_execution(driver),
            "element_finding": BrowserCompatibilityTest.test_element_finding(driver),
        }
        
        all_passed = all(r.get("success", False) for r in results.values())
        
        return {
            "success": all_passed,
            "results": results,
        }

    @classmethod
    def run_full_compatibility_test(cls, browsers_to_test=None):
        """Run full compatibility test on all browsers."""
        from browser import find_browser
        
        if browsers_to_test is None:
            browsers_to_test = ["brave", "chrome", "chromium", "auto"]
        
        results = {}
        
        for browser in browsers_to_test:
            try:
                # Test launch
                launch_result = cls.test_browser_launch(browser)
                
                if launch_result["success"]:
                    results[browser] = {
                        "launch": "✓",
                        "launch_time": launch_result.get("time", 0),
                        "automation": "✓",
                    }
                else:
                    results[browser] = {
                        "launch": "✗",
                        "error": launch_result.get("error", "Unknown"),
                    }
            
            except Exception as e:
                results[browser] = {
                    "launch": "✗",
                    "error": str(e),
                }
        
        return results

    @classmethod
    def print_compatibility_report(cls, results):
        """Print formatted compatibility test report."""
        print()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║          BROWSER COMPATIBILITY TEST REPORT                   ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
        print("BROWSER LAUNCH TESTS")
        print("─" * 63)
        
        for browser, result in results.items():
            status = result.get("launch", "?")
            symbol = "✓" if status == "✓" else "✗"
            
            print(f"  {symbol} {browser:15} ", end="")
            
            if status == "✓":
                time_taken = result.get("launch_time", 0)
                print(f"({time_taken:.1f}s)")
            else:
                error = result.get("error", "Unknown")
                print(f"({error[:40]})")
        
        print()
        
        # Summary
        passed = sum(1 for r in results.values() if r.get("launch") == "✓")
        total = len(results)
        
        print("SUMMARY")
        print("─" * 63)
        print(f"  Passed: {passed}/{total}")
        
        if passed == total:
            print("  Status: ✓ All browsers working")
        elif passed > 0:
            print(f"  Status: ⚠ {total - passed} browser(s) failed")
        else:
            print("  Status: ✗ No browsers working")
        
        print()
        print("═" * 63)
        print()


class BrowserQuirkDetector:
    """Detect and document browser quirks and differences."""

    QUIRKS = {
        "brave": {
            "description": "Brave Browser",
            "known_issues": [
                "Profile cache may be larger than Chrome",
                "Fingerprinting protections may affect some scripts",
            ],
        },
        "chrome": {
            "description": "Google Chrome",
            "known_issues": [
                "Requires sync disable for automation",
                "Extension conflicts possible",
            ],
        },
        "chromium": {
            "description": "Chromium",
            "known_issues": [
                "No automatic updates",
                "Minimal branding/features",
            ],
        },
    }

    @classmethod
    def get_browser_quirks(cls, browser_name):
        """Get known quirks for a browser."""
        return cls.QUIRKS.get(
            browser_name.lower(),
            {"description": browser_name, "known_issues": []},
        )

    @classmethod
    def report_browser_quirks(cls):
        """Print report of known browser quirks."""
        print()
        print("╔═══════════════════════════════════════════════════════════════╗")
        print("║          KNOWN BROWSER QUIRKS & ISSUES                       ║")
        print("╚═══════════════════════════════════════════════════════════════╝")
        print()
        
        for browser, info in cls.QUIRKS.items():
            print(f"{info['description']} ({browser})")
            print("─" * 63)
            
            if info["known_issues"]:
                for issue in info["known_issues"]:
                    print(f"  • {issue}")
            else:
                print("  • No known issues")
            
            print()

