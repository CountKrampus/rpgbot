import unittest
from unittest.mock import ANY, patch

import mining
import search


class TestSearchImprovements(unittest.TestCase):
    def test_map_rotation_normalizes_and_deduplicates(self):
        maps = search.normalize_map_rotation(
            ["  Jirachi's Park ", "jirachis park", {"name": "Sky Pillar"}]
        )
        self.assertEqual([item["name"] for item in maps],
                         ["Jirachi's Park", "Sky Pillar"])

    def test_rotation_skips_unopenable_maps(self):
        with patch.object(search, "open_map",
                          side_effect=[False, True]) as open_map, \
                patch.object(search, "run_searches") as run:
            result = search.run_search_rotation(
                object(), ["First", "Second"], 3
            )
        self.assertEqual(result["completed_maps"], 1)
        open_map.assert_any_call(ANY, "First")
        run.assert_called_once()


class TestMiningImprovements(unittest.TestCase):
    def test_resource_target(self):
        stats = mining.create_mining_stats()
        stats["resources"]["Sapphire"] = 2
        self.assertFalse(mining.mining_resource_target_reached(
            stats, {"Sapphire": 3}
        ))
        stats["resources"]["Sapphire"] = 3
        self.assertTrue(mining.mining_resource_target_reached(
            stats, {"Sapphire": 3}
        ))

    def test_attention_detection_is_non_destructive(self):
        class Driver:
            def find_element(self, by, value):
                return type("Body", (), {"text": "Your inventory is full"})()

        self.assertTrue(mining.mining_needs_attention(Driver()))


if __name__ == "__main__":
    unittest.main()
