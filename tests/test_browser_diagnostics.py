import unittest
from unittest.mock import MagicMock, patch

import browser


class FakeElement:
    def __init__(self):
        self.text = "RPGBot"
        self._value = ""

    def click(self):
        return None

    def send_keys(self, text):
        self._value = text

    def get_attribute(self, name):
        if name == "value":
            return self._value
        return None


class FakeSwitchTo:
    def __init__(self, driver):
        self.driver = driver

    def new_window(self, kind):
        self.driver.handles.append("tab-2")
        self.driver.current_window_handle = "tab-2"

    def window(self, handle):
        self.driver.current_window_handle = handle


class FakeDriver:
    def __init__(self):
        self.current_url = "https://eclipserpg.com/"
        self.current_window_handle = "tab-1"
        self.handles = ["tab-1"]
        self.capabilities = {
            "browserName": "chrome",
            "browserVersion": "120.0.0.0",
        }
        self.switch_to = FakeSwitchTo(self)
        self.closed = []
        self.element = FakeElement()

    def execute_script(self, script, *args):
        if "readyState" in script:
            return "complete"
        if "2 + 2" in script:
            return 4
        return None

    def get(self, url):
        self.current_url = url

    def find_element(self, by, value):
        return self.element

    def close(self):
        self.closed.append(self.current_window_handle)
        self.handles = [
            handle
            for handle in self.handles
            if handle != self.current_window_handle
        ]


class TestEnvironmentDiagnostics(unittest.TestCase):

    def test_python_and_selenium_pass(self):
        results = browser.environment_diagnostics()
        labels = [item["label"] for item in results]
        self.assertIn("Python", labels)
        self.assertIn("Selenium", labels)
        python_check = next(
            item for item in results if item["label"] == "Python"
        )
        self.assertTrue(python_check["ok"])

    def test_browser_detected_when_installed(self):
        with patch.object(
            browser,
            "detect_installed_browsers",
            return_value={"brave": "brave.exe"},
        ), patch.object(
            browser,
            "resolve_browser",
            return_value=("brave", "brave.exe"),
        ):
            results = browser.environment_diagnostics()
            detected = next(
                item
                for item in results
                if item["label"] == "Browser detected"
            )
            resolved = next(
                item
                for item in results
                if item["label"] == "Browser resolved"
            )
            self.assertTrue(detected["ok"])
            self.assertTrue(resolved["ok"])
            self.assertEqual(resolved["detail"], "brave")


class TestDriverDiagnostics(unittest.TestCase):

    def test_driver_checks_pass_on_fake_driver(self):
        results = browser.driver_diagnostics(FakeDriver())
        failed = [
            item["label"]
            for item in results
            if not item["ok"]
        ]
        self.assertEqual(failed, [])
        labels = [item["label"] for item in results]
        self.assertIn("Driver connection", labels)
        self.assertIn("Navigation", labels)
        self.assertIn("JavaScript", labels)
        self.assertIn("CSS selector", labels)
        self.assertIn("XPath", labels)
        self.assertIn("WebDriverWait", labels)
        self.assertIn("Browser interaction", labels)


class TestBrowserManagerTestRestoresTab(unittest.TestCase):

    def test_test_closes_probe_tab_and_restores(self):
        driver = FakeDriver()

        with patch.object(
            browser,
            "environment_diagnostics",
            return_value=[],
        ), patch.object(
            browser,
            "_print_diagnostic_report",
        ):
            ok = browser.BrowserManager.test(driver)

        self.assertTrue(ok)
        self.assertEqual(driver.current_window_handle, "tab-1")
        self.assertEqual(driver.closed, ["tab-2"])


if __name__ == "__main__":
    unittest.main()
