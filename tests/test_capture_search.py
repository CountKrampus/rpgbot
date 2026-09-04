import unittest
import io
from unittest.mock import patch
from contextlib import redirect_stdout

import capture
import config
import search
from selenium.webdriver.common.by import By


class FakeBody:
    def __init__(self, text):
        self.text = text


class FakeDriver:
    def __init__(self, text):
        self.current_url = "https://eclipserpg.com/battle"
        self.body = FakeBody(text)

    def find_element(self, by, value):
        return self.body


class TestCaptureResultDetection(unittest.TestCase):
    def test_successful_capture_variants_are_detected(self):
        for message in (
            "The Pokemon was successfully caught!",
            "You have obtained a new Pokemon.",
            "The Pokemon has been sent to your box.",
        ):
            with self.subTest(message=message):
                self.assertTrue(
                    capture.capture_succeeded(FakeDriver(message))
                )

    def test_failed_capture_is_detected(self):
        self.assertTrue(
            capture.capture_failed(
                FakeDriver("The Pokemon broke free! Use Another")
            )
        )

    def test_unrelated_battle_text_is_neither_result(self):
        driver = FakeDriver("Choose your next action.")
        self.assertFalse(capture.capture_succeeded(driver))
        self.assertFalse(capture.capture_failed(driver))


class TestSearchConfiguration(unittest.TestCase):
    def test_search_uses_shared_default(self):
        self.assertEqual(search.get_search_delay(), config.SEARCH_DELAY)

    def test_search_delay_rejects_reversed_ranges(self):
        original = search.get_search_delay()
        try:
            self.assertFalse(search.set_search_delay(2, 1))
            self.assertEqual(search.get_search_delay(), original)
        finally:
            search.set_search_delay(*original)


class TestSearchCancellationFinalization(unittest.TestCase):
    def test_cancelled_search_finishes_current_request_summary(self):
        with patch.object(search, "click_search", return_value=True), \
                patch.object(search, "interruptible_wait", return_value=True), \
                patch.object(search, "get_search_progress", return_value=(None, None)), \
                patch.object(search, "find_encounter_fight", return_value=None), \
                patch.object(search, "_record_search_session") as record, \
                redirect_stdout(io.StringIO()) as output:
            result = search.run_searches(
                object(),
                "Jirachi's Park",
                searches=10,
            )

        self.assertFalse(result)
        record.assert_called_once_with("Jirachi's Park", 1)
        self.assertIn("1 completed request", output.getvalue())

    def test_cancelled_search_still_starts_detected_encounter(self):
        fight = object()
        with patch.object(search, "click_search", return_value=True), \
                patch.object(search, "interruptible_wait", return_value=True), \
                patch.object(search, "get_search_progress", return_value=(None, None)), \
                patch.object(search, "find_encounter_fight", return_value=None), \
                patch.object(search, "click_encounter_fight", return_value=True), \
                patch.object(search, "handle_search_encounter", return_value=True) as handle, \
                patch.object(search, "_record_search_session"), \
                redirect_stdout(io.StringIO()):
            search.run_searches(
                object(),
                "Jirachi's Park",
                searches=10,
            )

        handle.assert_called_once_with(
            unittest.mock.ANY,
            target_pokemon=None,
            fight_clicked=True,
        )


class TestWildPokemonParsing(unittest.TestCase):
    def test_current_map_special_pokemon_markup_is_detected(self):
        class MapDriver:
            page_source = (
                '<div id="map-box">'
                '<a class="image-link" '
                'href="/amount_viewer?pokemon=GalaxyOriginKyogre">'
                '<img alt="Astral Galaxy Origin Kyogre">'
                '</a></div>'
            )

            def find_elements(self, by, selector):
                return []

        entries = search.get_wild_pokemon(MapDriver())

        self.assertEqual(
            entries,
            [{
                "name": "Astral Galaxy Origin Kyogre",
                "species_param": "GalaxyOriginKyogre",
                "dexed": False,
            }],
        )


class TestCaptureContinueSelectors(unittest.TestCase):
    def test_eclipse_continue_selector_targets_area_navigation(self):
        class ContinueButton:
            text = "Continue"

            def is_displayed(self):
                return True

            def is_enabled(self):
                return True

            def get_attribute(self, name):
                if name == "onclick":
                    return (
                        "this.disabled=true; "
                        'document.location="legendary_areas?area_id=4#search";'
                    )
                if name == "value":
                    return ""
                return ""

        class ResultDriver:
            def find_elements(self, by, selector):
                if by == By.CSS_SELECTOR:
                    return [ContinueButton()]
                return []

        self.assertIsNotNone(
            capture.find_capture_continue(ResultDriver())
        )

    def test_result_arriving_during_retry_is_finished(self):
        original_limit = capture.get_capture_retry_limit()
        original_stats = capture.get_capture_stats()

        try:
            capture.set_capture_retry_limit(2)
            capture.reset_capture_stats()

            with patch.object(
                capture,
                "capture_attempt",
                return_value=False,
            ), patch.object(
                capture,
                "capture_succeeded",
                side_effect=[False, False, True],
            ), patch.object(
                capture,
                "click_use_another",
                return_value=True,
            ), patch.object(
                capture,
                "click_capture_continue",
                return_value=True,
            ):
                with redirect_stdout(io.StringIO()):
                    self.assertTrue(
                        capture.capture_encounter(object())
                    )

            self.assertEqual(
                capture.get_capture_stats()["captured"],
                1,
            )
        finally:
            capture.set_capture_retry_limit(original_limit)
            capture._capture_stats.clear()
            capture._capture_stats.update(original_stats)


if __name__ == "__main__":
    unittest.main()
