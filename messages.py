"""
Messages (Private Messages / inbox) module for Eclipse RPG
Automation - Phase 5.

Built directly from the real HTML structure of
https://eclipserpg.com/private_messages?area=inbox

Row structure discovered:

    Sender:
        <a id="PM_Username{id}" href="/user?id={user_id}">
            <span class="username-component">...</span>
        </a>

    Subject / open message:
        <div onclick="view_message({id});">
            <a id="PM_ViewMessage{id}">{subject}</a>
        </div>

    Full body (already present in a hidden tooltip - no need
    to open a separate detail page):
        <div id="MessageTooltip{id}" ...>
            <span id="PM_SubjectContentText{id}">{subject}</span>
            <div id="PM_MessageContentText{id}">{body}</div>
        </div>

    Date:
        <i id="PM_Date{id}">August 20, 2026 (05:32 PM)</i>

    Delete (deletes IMMEDIATELY, no confirmation from the site
    itself - all confirmation safety lives in this bot):
        <a id="PM_Terminate{id}"
           onclick="terminate_read_message({id}, 'terminate');">X</a>

    Pagination:
        https://eclipserpg.com/private_messages?area=inbox&page=N
        <a href="?area=inbox&page=N" class="page-number-link">N</a>
        current page has class "page-number-link disabled"
"""

import re
import time
from datetime import datetime

from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    StaleElementReferenceException,
    WebDriverException,
    NoSuchElementException,
)

from config import BASE_URL
from utils import (
    safe_click,
    normalize,
    wait_for_document_ready,
    sleep_random,
)


INBOX_URL = f"{BASE_URL}/private_messages?area=inbox"

# Matches ids like "PM_ViewMessage6081523"
VIEW_ID_PATTERN = re.compile(r"^PM_ViewMessage(\d+)$")

# Eclipse RPG date format, e.g. "August 20, 2026 (05:32 PM)"
DATE_FORMAT = "%B %d, %Y (%I:%M %p)"


# ============================================================
# NAVIGATION
# ============================================================

def open_inbox(driver, page=1):
    """
    Navigate to a specific inbox page.
    """

    url = f"{INBOX_URL}&page={page}"

    try:

        driver.get(url)

        wait_for_document_ready(driver)

        sleep_random(0.6, 1.2)

        return True

    except WebDriverException:

        return False


# ============================================================
# READING MESSAGES ON THE CURRENT PAGE
# ============================================================

def get_messages_on_page(driver):
    """
    Return the messages visible on the currently loaded inbox
    page as a list of dicts:

        {
            "id": "6081523",
            "subject": "Re: Crystal Riolu",
            "sender": "Snoooom",
            "sender_user_id": "972624",
            "date": "August 20, 2026 (05:32 PM)",
            "body": "I sent the 30m :)",
        }

    Only reads what's already rendered on the page - does not
    navigate anywhere.
    """

    messages = []

    try:

        view_links = driver.find_elements(
            By.CSS_SELECTOR,
            "a[id^='PM_ViewMessage']",
        )

    except WebDriverException:

        return messages

    for link in view_links:

        try:

            element_id = link.get_attribute("id") or ""

            match = VIEW_ID_PATTERN.match(element_id)

            if not match:
                continue

            message_id = match.group(1)

            subject = link.text.strip()

            sender = ""
            sender_user_id = ""

            try:

                username_link = driver.find_element(
                    By.ID,
                    f"PM_Username{message_id}",
                )

                href = username_link.get_attribute("href") or ""

                sender_match = re.search(
                    r"user\?id=(\d+)",
                    href,
                )

                if sender_match:
                    sender_user_id = sender_match.group(1)

                sender = username_link.text.strip()

            except NoSuchElementException:
                pass

            date_text = ""

            try:

                date_element = driver.find_element(
                    By.ID,
                    f"PM_Date{message_id}",
                )

                date_text = date_element.text.strip()

            except NoSuchElementException:
                pass

            body = ""

            try:

                body_element = driver.find_element(
                    By.ID,
                    f"PM_MessageContentText{message_id}",
                )

                body = body_element.get_attribute(
                    "textContent"
                ).strip()

            except NoSuchElementException:
                pass

            messages.append({
                "id": message_id,
                "subject": subject,
                "sender": sender,
                "sender_user_id": sender_user_id,
                "date": date_text,
                "body": body,
            })

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):

            continue

    return messages


def get_message_date(message):
    """
    Parse a message's date string into a datetime, or None if
    it can't be parsed (format changed, empty, etc).
    """

    date_text = message.get("date", "")

    if not date_text:
        return None

    try:
        return datetime.strptime(date_text, DATE_FORMAT)
    except ValueError:
        return None


# ============================================================
# PAGINATION
# ============================================================

def get_total_pages(driver):
    """
    Read the highest page number from the pagination controls
    on the currently loaded inbox page. Returns 1 if pagination
    isn't present (i.e. everything fits on one page).
    """

    try:

        links = driver.find_elements(
            By.CSS_SELECTOR,
            "a.page-number-link",
        )

    except WebDriverException:

        return 1

    highest = 1

    for link in links:

        try:

            text = link.text.strip()

            if text.isdigit():
                highest = max(highest, int(text))

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):

            continue

    return highest


def get_total_message_count(driver):
    """
    Estimate the total number of messages across the whole
    inbox without scanning every page:

        count on page 1 * (total_pages - 1) + count on last page

    This assumes every page except possibly the last holds the
    same number of messages, which matches how this kind of
    pagination normally works.
    """

    open_inbox(driver, page=1)

    first_page_messages = get_messages_on_page(driver)
    per_page = len(first_page_messages)

    total_pages = get_total_pages(driver)

    if total_pages <= 1:
        return per_page

    open_inbox(driver, page=total_pages)

    last_page_messages = get_messages_on_page(driver)

    total = per_page * (total_pages - 1) + len(last_page_messages)

    return total


# ============================================================
# DELETING MESSAGES
# ============================================================

def delete_message(driver, message_id):
    """
    Delete a single message by id. The message must already be
    present on the currently loaded page (delete ids are only
    rendered for messages shown on that page).

    IMPORTANT: Eclipse RPG deletes immediately with no
    confirmation dialog of its own. Any "are you sure" step
    must happen in the calling code BEFORE this is called.
    """

    try:

        delete_link = driver.find_element(
            By.ID,
            f"PM_Terminate{message_id}",
        )

    except NoSuchElementException:

        return False

    if not safe_click(driver, delete_link):
        return False

    # Give the page a moment to process the deletion before
    # the caller looks at the page again.
    time.sleep(0.4)

    return True


def delete_messages(driver, message_ids):
    """
    Delete a list of message ids that are all present on the
    CURRENTLY LOADED page. Returns (succeeded, failed) counts.

    Does not navigate between pages - if you need to delete
    messages spread across multiple pages, open each page and
    call this once per page with just that page's ids.
    """

    succeeded = 0
    failed = 0

    for message_id in message_ids:

        if delete_message(driver, message_id):
            succeeded += 1
        else:
            failed += 1

    return succeeded, failed


def delete_all_messages(driver, progress_callback=None):
    """
    Delete every message in the inbox.

    Repeatedly reloads inbox page 1 and deletes whatever is
    currently showing there. This handles inboxes where later
    pages shift forward as earlier messages are removed,
    without assuming a specific re-numbering behavior - it just
    keeps clearing page 1 until it comes back empty.

    progress_callback(deleted_so_far), if given, is called after
    each page's batch so the caller can show live progress.
    """

    total_deleted = 0

    # Safety cap so a site quirk can't cause an infinite loop.
    max_iterations = 500

    for _ in range(max_iterations):

        open_inbox(driver, page=1)

        messages = get_messages_on_page(driver)

        if not messages:
            break

        for message in messages:

            if delete_message(driver, message["id"]):
                total_deleted += 1

        if progress_callback:
            progress_callback(total_deleted)

    return total_deleted
