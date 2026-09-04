import unittest
from unittest.mock import patch

import queue_mode


class TestQueueControls(unittest.TestCase):
    def test_named_presets_round_trip_and_delete(self):
        queue = [{
            "type": "mine",
            "minutes": 2,
            "catch": False,
        }]
        with patch.object(queue_mode, "QUEUE_PRESETS_FILE", "queue-presets-test.json"):
            try:
                self.assertTrue(queue_mode.save_queue_preset("daily", queue))
                self.assertEqual(queue_mode.load_queue_preset("daily"), queue)
                self.assertTrue(queue_mode.delete_queue_preset("daily"))
                self.assertIsNone(queue_mode.load_queue_preset("daily"))
            finally:
                import os
                if os.path.exists("queue-presets-test.json"):
                    os.remove("queue-presets-test.json")

    def test_run_queue_repeats_steps(self):
        queue = [{"type": "train", "minutes": 1}]
        with patch.object(queue_mode, "train_mode") as train, \
                patch.object(queue_mode, "is_cancel_requested", return_value=False):
            queue_mode._run_queue(object(), queue, repeats=2)
        self.assertEqual(train.call_count, 2)

    def test_failed_step_can_be_skipped(self):
        queue = [{"type": "train", "minutes": 1}]
        with patch.object(queue_mode, "train_mode", side_effect=RuntimeError("boom")), \
                patch.object(queue_mode, "_failure_action", return_value="skip"), \
                patch.object(queue_mode, "is_cancel_requested", return_value=False), \
                patch("builtins.print"):
            queue_mode._run_queue(object(), queue)

    def test_choose_map_includes_unlocked_exclusive_maps(self):
        area = {"name": "Great Volcano", "id": 7}
        with patch.object(queue_mode, "get_exclusive_maps", return_value=[area]), \
                patch(
                    "builtins.input",
                    return_value=str(len(queue_mode.MAPS) + 1),
                ):
            selected = queue_mode._choose_map(object())

        self.assertEqual(
            selected,
            {
                "name": "Great Volcano",
                "is_exclusive": True,
                "area": area,
            },
        )

    def test_move_step_reorders_queue(self):
        queue = [
            {"type": "train", "minutes": 1},
            {"type": "mine", "minutes": 2, "catch": False},
        ]
        with patch("builtins.input", return_value="2"):
            queue_mode._move_step(queue, "up")

        self.assertEqual([step["type"] for step in queue], ["mine", "train"])

    def test_exclusive_search_opens_area_and_passes_area_details(self):
        area = {"name": "Great Volcano", "id": 7}
        class Driver:
            def get(self, url):
                self.url = url

        driver = Driver()
        queue = [{
            "type": "search",
            "minutes": 1,
            "map": {
                "name": area["name"],
                "is_exclusive": True,
                "area": area,
            },
        }]

        with patch.object(queue_mode, "_build_queue", return_value=queue), \
                patch("builtins.input", return_value="y"), \
                patch.object(queue_mode, "wait_for_document_ready"), \
                patch.object(queue_mode, "open_exclusive_area", return_value=True) as open_area, \
                patch.object(queue_mode, "run_searches") as run_searches:
            queue_mode.queue_mode(driver)

        open_area.assert_called_once_with(driver, area)
        run_searches.assert_called_once_with(
            driver,
            "Great Volcano",
            searches=10**9,
            is_exclusive=True,
            area=area,
            duration_seconds=60,
        )


if __name__ == "__main__":
    unittest.main()
