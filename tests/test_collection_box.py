import unittest

from unittest.mock import patch

from menus.collection_menu import (
    _box_collection_key,
    _build_box_summary,
    _compare_box_summaries,
    _filter_box_pokemon,
    _collection_export_data,
)


class TestBoxCollectionMapping(unittest.TestCase):
    def test_normal_variant_matches_manual_default(self):
        self.assertEqual(
            _box_collection_key("Pikachu", "Normal"),
            _box_collection_key("pikachu", "Default"),
        )

    def test_box_duplicates_are_aggregated(self):
        summary = _build_box_summary(
            [
                {"species": "Gastly", "display_category": "Normal"},
                {"species": "Gastly", "display_category": "Normal"},
                {"species": "Gastly", "display_category": "Shiny"},
            ]
        )

        self.assertEqual(summary[("gastly", "default")]["quantity"], 2)
        self.assertEqual(summary[("gastly", "shiny")]["quantity"], 1)

    def test_missing_species_is_ignored(self):
        self.assertEqual(
            _build_box_summary([{"name": "", "variant": "Normal"}]),
            {},
        )

    def test_filter_by_box_metadata(self):
        records = [
            {"species": "Pikachu", "box_number": 1},
            {"species": "Eevee", "box_number": 2},
        ]
        self.assertEqual(
            [row["species"] for row in _filter_box_pokemon(records, "1")],
            ["Pikachu"],
        )

    def test_compare_boxes_reports_differences(self):
        left = _build_box_summary([{"species": "Pikachu"}])
        right = _build_box_summary([{"species": "Eevee"}])
        result = _compare_box_summaries(left, right)
        self.assertEqual(len(result["left_only"]), 1)
        self.assertEqual(len(result["right_only"]), 1)
        self.assertEqual(result["shared"], [])

    def test_export_data_preserves_newly_obtained_metadata(self):
        with patch(
            "menus.collection_menu._get_collection_entries",
            return_value=[(1, "Pikachu", "Default", 1, "1", "2026-01-01")],
        ):
            data = _collection_export_data(1, "Living Dex")
        self.assertEqual(data[0]["box"], "1")
        self.assertEqual(data[0]["obtained_at"], "2026-01-01")


if __name__ == "__main__":
    unittest.main()
