import unittest

import browser
from headless_mode import HeadlessDriver, MockElement


class TestHeadlessMode(unittest.TestCase):
    def test_headless_driver_records_browser_actions(self):
        driver = HeadlessDriver("demo")
        driver.get("https://example.test")
        element = driver.find_element("id", "search")
        element.click()

        self.assertEqual(driver.current_url, "https://example.test")
        self.assertTrue(element.clicked)
        self.assertEqual(driver.actions[0], ("get", "https://example.test"))

    def test_headless_browser_resolves_without_executable(self):
        self.assertEqual(
            browser.resolve_browser("headless"),
            ("headless", None),
        )

    def test_headless_driver_can_be_closed(self):
        driver = HeadlessDriver("demo")
        driver.quit()
        self.assertTrue(driver.closed)


if __name__ == "__main__":
    unittest.main()
