import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from tempfile import TemporaryDirectory
import os

import browser
import settings


class TestNormalizeBrowserName(unittest.TestCase):

    def test_none_and_blank_are_auto(self):
        self.assertEqual(browser.normalize_browser_name(None), "auto")
        self.assertEqual(browser.normalize_browser_name("  "), "auto")

    def test_known_names_lowercased(self):
        self.assertEqual(browser.normalize_browser_name("Brave"), "brave")
        self.assertEqual(browser.normalize_browser_name("CHROME"), "chrome")
        self.assertEqual(browser.normalize_browser_name("chromium"), "chromium")
        self.assertEqual(browser.normalize_browser_name("auto"), "auto")

    def test_invalid_name_is_auto(self):
        self.assertEqual(browser.normalize_browser_name("banana"), "auto")


class TestFindBrowserExecutable(unittest.TestCase):

    def test_returns_first_existing_candidate(self):
        with TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.exe"
            present = Path(tmp) / "brave.exe"
            present.write_bytes(b"")

            with patch.object(
                browser,
                "candidate_paths",
                return_value=[missing, present],
            ), patch.object(
                browser.shutil,
                "which",
                return_value=None,
            ):
                found = browser.find_browser_executable("brave")
                self.assertEqual(found, present)

    def test_returns_none_when_missing(self):
        with patch.object(
            browser,
            "candidate_paths",
            return_value=[Path("Z:\\nope\\brave.exe")],
        ), patch.object(
            browser.shutil,
            "which",
            return_value=None,
        ):
            self.assertIsNone(
                browser.find_browser_executable("brave")
            )


class TestResolveBrowser(unittest.TestCase):

    def test_auto_prefers_brave_then_chrome(self):
        installed = {
            "brave": Path("brave.exe"),
            "chrome": Path("chrome.exe"),
        }

        with patch.object(
            browser,
            "detect_installed_browsers",
            return_value=installed,
        ):
            name, path = browser.resolve_browser(
                "auto",
                allow_fallback=False,
            )
            self.assertEqual(name, "brave")
            self.assertEqual(path, installed["brave"])

    def test_auto_uses_chrome_when_brave_missing(self):
        installed = {
            "chrome": Path("chrome.exe"),
        }

        with patch.object(
            browser,
            "detect_installed_browsers",
            return_value=installed,
        ):
            name, path = browser.resolve_browser("auto")
            self.assertEqual(name, "chrome")

    def test_explicit_missing_without_fallback_raises(self):
        with patch.object(
            browser,
            "detect_installed_browsers",
            return_value={"brave": Path("brave.exe")},
        ):
            with self.assertRaises(FileNotFoundError):
                browser.resolve_browser(
                    "chrome",
                    allow_fallback=False,
                )

    def test_explicit_missing_with_fallback_uses_next(self):
        with patch.object(
            browser,
            "detect_installed_browsers",
            return_value={"brave": Path("brave.exe")},
        ):
            name, path = browser.resolve_browser(
                "chrome",
                allow_fallback=True,
            )
            self.assertEqual(name, "brave")
            self.assertEqual(path, Path("brave.exe"))

    def test_termux_requires_and_returns_chromium(self):
        executable = Path("/data/data/com.termux/files/usr/bin/chromium")
        with patch.object(
            browser,
            "find_browser_executable",
            return_value=executable,
        ):
            self.assertEqual(
                browser.resolve_browser("termux"),
                ("termux", executable),
            )


class TestTermuxBrowserStartup(unittest.TestCase):

    def test_create_uses_termux_driver(self):
        driver = MagicMock()
        with patch.object(browser, "acquire_instance_lock"), patch.object(
            browser,
            "resolve_browser",
            return_value=("termux", Path("chromium")),
        ), patch.object(
            browser,
            "get_profile_path",
            return_value=Path("profile"),
        ), patch.object(
            browser,
            "_create_termux_driver",
            return_value=driver,
        ) as create_termux, patch.object(
            browser.BrowserManager,
            "is_alive",
            return_value=True,
        ), patch.object(browser.time, "sleep"), patch.object(
            browser,
            "_print_header",
        ), patch.object(
            browser,
            "_status",
        ), patch.object(
            browser,
            "_info",
        ), patch.object(
            browser,
            "_success",
        ):
            result = browser.BrowserManager.create(
                "termux-account",
                "termux",
            )

        self.assertIs(result, driver)
        create_termux.assert_called_once_with(
            Path("profile"),
            Path("chromium"),
            "termux-account",
        )


class TestGetProfilePathByBrowser(unittest.TestCase):

    def test_brave_keeps_legacy_profile_folder(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "selenium_profiles"
            with patch.object(browser, "PROFILE_ROOT", root):
                path = browser.get_profile_path(
                    "goldisduck",
                    browser="brave",
                )
                self.assertEqual(
                    path,
                    root / "instance_goldisduck",
                )

    def test_chrome_uses_separate_profile_folder(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp) / "selenium_profiles"
            with patch.object(browser, "PROFILE_ROOT", root):
                path = browser.get_profile_path(
                    "goldisduck",
                    browser="chrome",
                )
                self.assertEqual(
                    path,
                    root / "chrome" / "instance_goldisduck",
                )


class TestBrowserSettingsDefaults(unittest.TestCase):

    def test_missing_browser_keys_use_defaults(self):
        with TemporaryDirectory() as tmp:
            fake = os.path.join(tmp, "settings.json")
            with patch.object(settings, "SETTINGS_FILE", fake):
                loaded = settings.load_settings()
                self.assertEqual(loaded.get("browser_name"), "auto")
                self.assertEqual(
                    loaded.get("browser_allow_fallback"),
                    False,
                )

    def test_set_browser_name_rejects_invalid(self):
        browser.set_browser_name("banana")
        self.assertEqual(browser.get_browser_name(), "auto")
        browser.set_browser_name("chrome")
        self.assertEqual(browser.get_browser_name(), "chrome")
        browser.set_browser_name("auto")


if __name__ == "__main__":
    unittest.main()
