import unittest
import threading
import time

import cancellation


class TestCancellation(unittest.TestCase):
    def test_cancel_key_accepts_single_alphanumeric_character(self):
        original = cancellation.get_cancel_key()
        try:
            self.assertTrue(cancellation.set_cancel_key("x"))
            self.assertEqual(cancellation.get_cancel_key(), "X")
            self.assertFalse(cancellation.set_cancel_key("F1"))
            self.assertFalse(cancellation.set_cancel_key(""))
        finally:
            cancellation.set_cancel_key(original)
    def setUp(self):
        cancellation.reset_cancel()

    def tearDown(self):
        cancellation.reset_cancel()

    def test_request_cancel_sets_shared_flag(self):
        self.assertFalse(cancellation.is_cancel_requested())
        cancellation.request_cancel()
        self.assertTrue(cancellation.is_cancel_requested())

    def test_wait_returns_promptly_when_cancelled(self):
        started = time.monotonic()
        threading.Timer(0.02, cancellation.request_cancel).start()
        self.assertTrue(cancellation.wait(2))
        self.assertLess(time.monotonic() - started, 0.5)

    def test_status_reports_configured_state(self):
        self.assertEqual(cancellation.get_cancel_key(), "Q")
        self.assertEqual(cancellation.get_cancel_status(), "READY")
        cancellation.request_cancel()
        self.assertEqual(cancellation.get_cancel_status(), "REQUESTED")

    def test_automation_task_clears_state_after_exit(self):
        with cancellation.automation_task():
            cancellation.request_cancel()
            self.assertTrue(cancellation.is_cancel_requested())

        self.assertFalse(cancellation.is_cancel_requested())


if __name__ == "__main__":
    unittest.main()
