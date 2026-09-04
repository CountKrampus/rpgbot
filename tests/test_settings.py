import json
import os
import tempfile
import unittest
from unittest.mock import patch

import settings


class TestSettingsPersistence(unittest.TestCase):
    def test_corrupt_file_recovers_to_defaults_and_preserves_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "settings.json")
            with open(path, "w", encoding="utf-8") as stream:
                stream.write("{not json")
            with patch.object(settings, "SETTINGS_FILE", path):
                loaded = settings.load_settings()
            self.assertEqual(loaded["cancellation_hotkey"], "Q")
            self.assertTrue(os.path.exists(path + ".corrupt"))

    def test_export_and_import_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "portable.json")
            destination = os.path.join(directory, "settings.json")
            with patch.object(settings, "SETTINGS_FILE", destination), \
                 patch.object(settings, "gather_current_settings",
                              return_value={"cancellation_hotkey": "X"}), \
                 patch.object(settings, "apply_settings") as apply:
                self.assertTrue(settings.export_settings(path))
                self.assertTrue(settings.import_settings(path))
                self.assertEqual(apply.call_args.args[0]["cancellation_hotkey"], "X")
            with open(path, encoding="utf-8") as stream:
                self.assertEqual(json.load(stream)["cancellation_hotkey"], "X")


if __name__ == "__main__":
    unittest.main()
