"""
Box (Your Box / PC storage) module for Eclipse RPG Automation.

Built from the real HTML of https://eclipserpg.com/your_box

Row structure discovered:

    <tr id="YB_Pokemon{id}">
      <td class="tnav_left">
        <img src="/images/icons/{Species}.png" ...>
      </td>
      <td class="tnav_left" ...>
        <div id="BoxTooltip{id}" ...>
          ... HP/MP/ATK/DEF/SPLATK/SPLDEF/SPD stats ...
        </div>
        <a href="/pokemon?id={id}">
          <span>{Name} Lv. {level}</span>
          <img src=".../gender-male.png">  (or gender-female, or absent)
        </a>
      </td>
      <td class="tnav">
        <button onclick="from_box({id}, 1);">1</button>
        ... slot buttons 1-6 ...
      </td>
    </tr>

The box page also has the site's own search built in - a GET
form:

    <form method="get">
      <input type="hidden" name="user" value="1102725">
      <input type="hidden" name="special_eid" value="">
      <input type="text" name="input_search"
             placeholder="Search (e.g. ShinyMudkip)">
      <button type="submit">Search</button>
    </form>

Since it's method="get" with no action, submitting it just
navigates to the current page URL with those three as query
params. That means search_box() can build the URL directly
instead of clicking anything - and it uses the site's own
search/filtering, so there's no pagination problem to work
around on our end.
"""

import re
from urllib.parse import urlencode

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
)

from config import BASE_URL
from utils import wait_for_document_ready, sleep_random


BOX_URL = f"{BASE_URL}/your_box"

ROW_ID_PATTERN = re.compile(r"^YB_Pokemon(\d+)$")
NAME_LEVEL_PATTERN = re.compile(r"^(.*)\s+Lv\.\s*([\d,]+)$")


def open_box(driver):
    """
    Navigate to the plain box page (no search filter applied).
    """

    try:

        driver.get(BOX_URL)

        wait_for_document_ready(driver)

        sleep_random(0.6, 1.2)

        return True

    except WebDriverException:

        return False


def get_account_user_id(driver):
    """
    Read the account's user id from the hidden 'user' field of
    the box search form on the currently loaded page. Falls
    back to the window.UserID JS global if the form isn't
    present for some reason.
    """

    try:

        field = driver.find_element(
            By.CSS_SELECTOR,
            "input[name='user']",
        )

        value = field.get_attribute("value")

        if value:
            return value

    except (NoSuchElementException, WebDriverException):

        pass

    try:

        return driver.execute_script(
            "return window.UserID ? "
            "String(window.UserID) : null;"
        )

    except WebDriverException:

        return None


def get_box_pokemon(driver):
    """
    Scrape the Pokémon listed on the CURRENTLY LOADED box page
    (whether that's the full box or a filtered search result).

    Returns a list of dicts:

        {
            "id": "38976414",
            "name": "Basculin",
            "level": 27,
            "gender": "male",   # "male" / "female" / None
        }
    """

    results = []

    try:

        rows = driver.find_elements(
            By.CSS_SELECTOR,
            "tr[id^='YB_Pokemon']",
        )

    except WebDriverException:

        return results

    for row in rows:

        try:

            row_id = row.get_attribute("id") or ""

            match = ROW_ID_PATTERN.match(row_id)

            if not match:
                continue

            pokemon_id = match.group(1)

            try:

                link = row.find_element(
                    By.CSS_SELECTOR,
                    f"a[href='/pokemon?id={pokemon_id}']",
                )

            except NoSuchElementException:

                continue

            text = link.find_element(
                By.TAG_NAME,
                "span",
            ).text.strip()

            name = text
            level = None

            level_match = NAME_LEVEL_PATTERN.match(text)

            if level_match:

                name = level_match.group(1).strip()

                level = int(
                    level_match.group(2).replace(",", "")
                )

            gender = None

            try:

                gender_image = link.find_element(
                    By.TAG_NAME,
                    "img",
                )

                src = gender_image.get_attribute("src") or ""

                if "gender-male" in src:
                    gender = "male"
                elif "gender-female" in src:
                    gender = "female"

            except NoSuchElementException:

                pass

            results.append({
                "id": pokemon_id,
                "name": name,
                "level": level,
                "gender": gender,
            })

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):

            continue

    return results


def search_box(driver, query):
    """
    Search the box using the site's own search form (GET
    request with user/special_eid/input_search params), then
    scrape whatever it returns.

    This uses the site's own filtering rather than scraping
    page by page, so it isn't limited to whatever page happens
    to be loaded first.
    """

    if not open_box(driver):
        return []

    user_id = get_account_user_id(driver)

    params = {
        "user": user_id or "",
        "special_eid": "",
        "input_search": query,
    }

    url = f"{BOX_URL}?{urlencode(params)}"

    try:

        driver.get(url)

        wait_for_document_ready(driver)

        sleep_random(0.6, 1.2)

    except WebDriverException:

        return []

    return get_box_pokemon(driver)
