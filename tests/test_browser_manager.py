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


class TestBrowserManagerWrappers(unittest.TestCase):

    def test_setup_driver_delegates_to_create(self):
        with patch.object(
            browser.BrowserManager,
            "create",
            return_value="driver",
        ) as mock_create:
            result = browser.setup_driver("goldisduck")
            mock_create.assert_called_once_with("goldisduck")
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
