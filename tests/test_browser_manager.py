import unittest
from pathlib import Path
from unittest.mock import patch
from tempfile import TemporaryDirectory

import browser


class TestSanitizeInstanceName(unittest.TestCase):

    def test_none_becomes_default(self):
        self.assertEqual(
            browser.sanitize_instance_name(None),
            "default",
        )

    def test_empty_becomes_default(self):
        self.assertEqual(
            browser.sanitize_instance_name("   "),
            "default",
        )

    def test_unsafe_characters_replaced(self):
        self.assertEqual(
            browser.sanitize_instance_name('gold:is/duck'),
            "gold_is_duck",
        )

    def test_plain_account_unchanged(self):
        self.assertEqual(
            browser.sanitize_instance_name("goldisduck"),
            "goldisduck",
        )


class TestGetProfilePath(unittest.TestCase):

    def test_profile_uses_instance_prefix(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "selenium_profiles"
            with patch.object(browser, "PROFILE_ROOT", root):
                path = browser.get_profile_path("goldisduck")
                self.assertEqual(
                    path,
                    root / "instance_goldisduck",
                )
                self.assertTrue(path.is_dir())


class TestBrowserManagerIsAlive(unittest.TestCase):

    def test_none_driver_is_not_alive(self):
        self.assertFalse(
            browser.BrowserManager.is_alive(None)
        )

    def test_is_driver_alive_delegates(self):
        with patch.object(
            browser.BrowserManager,
            "is_alive",
            return_value=True,
        ) as mock_alive:
            result = browser.is_driver_alive("driver")
            mock_alive.assert_called_once_with("driver")
            self.assertTrue(result)


class TestBrowserDetection(unittest.TestCase):

    def test_find_brave_raises_if_not_found(self):
        with patch.object(browser, "BRAVE_PATHS", []):
            with self.assertRaises(FileNotFoundError):
                browser.find_brave()

    def test_find_chrome_raises_if_not_found(self):
        with patch.object(browser, "CHROME_PATHS", []):
            with self.assertRaises(FileNotFoundError):
                browser.find_chrome()

    def test_find_chromium_raises_if_not_found(self):
        with patch.object(browser, "CHROMIUM_PATHS", []):
            with self.assertRaises(FileNotFoundError):
                browser.find_chromium()

    def test_find_browser_brave(self):
        with patch.object(
            browser,
            "find_brave",
            return_value=Path("C:/brave.exe"),
        ) as mock_find:
            result = browser.find_browser("brave")
            mock_find.assert_called_once()
            self.assertEqual(result, Path("C:/brave.exe"))

    def test_find_browser_chrome(self):
        with patch.object(
            browser,
            "find_chrome",
            return_value=Path("C:/chrome.exe"),
        ) as mock_find:
            result = browser.find_browser("chrome")
            mock_find.assert_called_once()
            self.assertEqual(result, Path("C:/chrome.exe"))

    def test_find_browser_chromium(self):
        with patch.object(
            browser,
            "find_chromium",
            return_value=Path("C:/chromium.exe"),
        ) as mock_find:
            result = browser.find_browser("chromium")
            mock_find.assert_called_once()
            self.assertEqual(result, Path("C:/chromium.exe"))

    def test_find_browser_auto_tries_brave_first(self):
        with patch.object(
            browser,
            "find_brave",
            return_value=Path("C:/brave.exe"),
        ) as mock_brave:
            result = browser.find_browser("auto")
            mock_brave.assert_called_once()
            self.assertEqual(result, Path("C:/brave.exe"))

    def test_find_browser_auto_falls_back_to_chrome(self):
        with patch.object(
            browser,
            "find_brave",
            side_effect=FileNotFoundError(),
        ), patch.object(
            browser,
            "find_chrome",
            return_value=Path("C:/chrome.exe"),
        ) as mock_chrome:
            result = browser.find_browser("auto")
            mock_chrome.assert_called_once()
            self.assertEqual(result, Path("C:/chrome.exe"))

    def test_find_browser_auto_falls_back_to_chromium(self):
        with patch.object(
            browser,
            "find_brave",
            side_effect=FileNotFoundError(),
        ), patch.object(
            browser,
            "find_chrome",
            side_effect=FileNotFoundError(),
        ), patch.object(
            browser,
            "find_chromium",
            return_value=Path("C:/chromium.exe"),
        ) as mock_chromium:
            result = browser.find_browser("auto")
            mock_chromium.assert_called_once()
            self.assertEqual(result, Path("C:/chromium.exe"))

    def test_find_browser_auto_fails_if_none_found(self):
        with patch.object(
            browser,
            "find_brave",
            side_effect=FileNotFoundError(),
        ), patch.object(
            browser,
            "find_chrome",
            side_effect=FileNotFoundError(),
        ), patch.object(
            browser,
            "find_chromium",
            side_effect=FileNotFoundError(),
        ):
            with self.assertRaises(FileNotFoundError):
                browser.find_browser("auto")

    def test_find_browser_invalid_browser_raises(self):
        with self.assertRaises(ValueError):
            browser.find_browser("firefox")


class TestBrowserManagerWrappers(unittest.TestCase):

    def test_setup_driver_delegates_to_create(self):
        with patch.object(
            browser.BrowserManager,
            "create",
            return_value="driver",
        ) as mock_create:
            result = browser.setup_driver("goldisduck")
            mock_create.assert_called_once_with("goldisduck", "auto")
            self.assertEqual(result, "driver")

    def test_setup_driver_with_browser(self):
        with patch.object(
            browser.BrowserManager,
            "create",
            return_value="driver",
        ) as mock_create:
            result = browser.setup_driver("goldisduck", "chrome")
            mock_create.assert_called_once_with("goldisduck", "chrome")
            self.assertEqual(result, "driver")

    def test_close_driver_delegates_to_close(self):
        with patch.object(
            browser.BrowserManager,
            "close",
        ) as mock_close:
            browser.close_driver("driver", "goldisduck")
            mock_close.assert_called_once_with(
                "driver",
                "goldisduck",
            )

    def test_restart_driver_delegates_to_restart(self):
        with patch.object(
            browser.BrowserManager,
            "restart",
            return_value="new-driver",
        ) as mock_restart:
            result = browser.restart_driver(
                "driver",
                "goldisduck",
            )
            mock_restart.assert_called_once_with(
                "driver",
                "goldisduck",
            )
            self.assertEqual(result, "new-driver")


class TestBrowserManagerRestartUsesCreateAndClose(unittest.TestCase):

    def test_restart_calls_close_then_create(self):
        with patch.object(
            browser.BrowserManager,
            "close",
        ) as mock_close, patch.object(
            browser.BrowserManager,
            "create",
            return_value="new-driver",
        ) as mock_create, patch.object(
            browser.time,
            "sleep",
        ), patch.object(
            browser,
            "_section",
        ), patch.object(
            browser,
            "_warning",
        ), patch.object(
            browser,
            "_success",
        ):
            result = browser.BrowserManager.restart(
                "driver",
                "goldisduck",
            )
            mock_close.assert_called_once_with(
                "driver",
                "goldisduck",
            )
            mock_create.assert_called_once_with(
                "goldisduck",
            )
            self.assertEqual(result, "new-driver")


if __name__ == "__main__":
    unittest.main()
