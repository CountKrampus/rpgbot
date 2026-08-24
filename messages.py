"""
Messages (Private Messages / inbox) module for Eclipse RPG
Automation - Phase 5.

Built from the Eclipse RPG private message HTML structure.

Important:
    Eclipse RPG deletes messages immediately when the delete
    control is activated. There is no site-side confirmation.

    Destructive confirmation is therefore handled by the menu
    layer before any deletion begins.
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
    wait_for_document_ready,
    sleep_random,
)


INBOX_URL = f"{BASE_URL}/private_messages?area=inbox"

VIEW_ID_PATTERN = re.compile(r"^PM_ViewMessage(\d+)$")

DATE_FORMAT = "%B %d, %Y (%I:%M %p)"


# ============================================================
# NAVIGATION
# ============================================================

def open_inbox(driver, page=1):
    """
    Navigate to a specific inbox page.

    Returns True on success and False if navigation fails.
    """

    try:
        if page <= 1:
            url = INBOX_URL
        else:
            url = f"{INBOX_URL}&page={page}"

        driver.get(url)

        wait_for_document_ready(driver)

        sleep_random(0.5, 1.0)

        return True

    except WebDriverException:
        return False


def reload_current_inbox_page(driver, page=1):
    """
    Reload the requested inbox page.

    Kept separate from open_inbox() so bulk operations can
    clearly indicate that they are intentionally refreshing
    the live pagination.
    """

    return open_inbox(driver, page=page)


# ============================================================
# READING MESSAGES
# ============================================================

def get_messages_on_page(driver):
    """
    Read all messages currently rendered on the page.

    Returns:

        [
            {
                "id": "...",
                "subject": "...",
                "sender": "...",
                "sender_user_id": "...",
                "date": "...",
                "body": "..."
            }
        ]
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

                body = (
                    body_element
                    .get_attribute("textContent")
                    .strip()
                )

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
    Convert Eclipse RPG's message date into datetime.

    Returns None when the date cannot be parsed.
    """

    date_text = message.get("date", "")

    if not date_text:
        return None

    try:
        return datetime.strptime(
            date_text,
            DATE_FORMAT,
        )

    except ValueError:
        return None


# ============================================================
# PAGINATION
# ============================================================

def get_total_pages(driver):
    """
    Return the highest visible page number.

    Returns 1 if no pagination is present.
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
                highest = max(
                    highest,
                    int(text),
                )

        except (
            StaleElementReferenceException,
            WebDriverException,
        ):
            continue

    return highest


def get_total_message_count(driver):
    """
    Calculate the actual total number of messages.

    This walks through the current pagination instead of
    assuming every page contains exactly the same number of
    messages.
    """

    if not open_inbox(driver, page=1):
        return 0

    total_pages = get_total_pages(driver)

    total = 0

    for page in range(1, total_pages + 1):

        if not open_inbox(driver, page=page):
            continue

        total += len(
            get_messages_on_page(driver)
        )

    return total


# ============================================================
# DELETING ONE MESSAGE
# ============================================================

def delete_message(driver, message_id):
    """
    Delete one message from the currently loaded page.

    The message must exist on the current page.
    """

    try:
        delete_link = driver.find_element(
            By.ID,
            f"PM_Terminate{message_id}",
        )

    except NoSuchElementException:
        return False

    except WebDriverException:
        return False

    try:
        if not safe_click(driver, delete_link):
            return False

    except (
        StaleElementReferenceException,
        WebDriverException,
    ):
        return False

    time.sleep(0.25)

    return True


def delete_messages(driver, message_ids):
    """
    Delete multiple messages currently visible on the page.

    Returns:

        (succeeded, failed)
    """

    succeeded = 0
    failed = 0

    for message_id in message_ids:

        if delete_message(driver, message_id):
            succeeded += 1
        else:
            failed += 1

    return succeeded, failed


# ============================================================
# DELETE EVERYTHING
# ============================================================

def delete_all_messages(driver, progress_callback=None):
    """
    Delete every message in the inbox.

    IMPORTANT:

    This intentionally works from page 1 repeatedly.

    When messages are deleted, later pages shift forward.
    Reloading page 1 ensures that shifted messages are never
    skipped.

    This is slower than trying to delete from a static list,
    but it is dramatically safer for a changing paginated
    inbox.
    """

    total_deleted = 0

    max_passes = 10000
    passes = 0

    while passes < max_passes:

        passes += 1

        if not open_inbox(driver, page=1):
            time.sleep(1)
            continue

        messages = get_messages_on_page(driver)

        if not messages:
            break

        ids = [
            message["id"]
            for message in messages
        ]

        succeeded, _failed = delete_messages(
            driver,
            ids,
        )

        total_deleted += succeeded

        if progress_callback:
            progress_callback(
                total_deleted,
                len(messages),
                succeeded,
            )

        if succeeded == 0:
            break

        time.sleep(0.4)

    return total_deleted


# ============================================================
# DELETE MESSAGES OLDER THAN CUTOFF
# ============================================================

def delete_messages_older_than(
    driver,
    cutoff,
    progress_callback=None,
):
    """
    Delete every message older than `cutoff`.

    This is the important replacement for the old
    page-number-based implementation.

    The inbox is treated as dynamic:

        1. Open page 1.
        2. Find old messages.
        3. Delete them.
        4. Reload page 1.
        5. Repeat until page 1 has no old messages.
        6. Move to page 2.
        7. Repeat.

    If deleting messages causes pagination to collapse,
    we return to page 1 rather than trusting stale page
    numbers.

    This prevents messages from being skipped.
    """

    total_deleted = 0

    current_page = 1
    passes = 0
    max_passes = 10000

    while passes < max_passes:

        passes += 1

        if not open_inbox(
            driver,
            page=current_page,
        ):
            time.sleep(1)
            continue

        messages = get_messages_on_page(driver)

        # Empty page means we have gone past the inbox.
        if not messages:

            if current_page <= 1:
                break

            current_page -= 1
            continue

        old_messages = []

        for message in messages:

            message_date = get_message_date(message)

            if message_date is None:
                continue

            if message_date < cutoff:
                old_messages.append(message)

        # ----------------------------------------------------
        # OLD MESSAGES FOUND
        # ----------------------------------------------------

        if old_messages:

            ids = [
                message["id"]
                for message in old_messages
            ]

            succeeded, failed = delete_messages(
                driver,
                ids,
            )

            total_deleted += succeeded

            if progress_callback:
                progress_callback(
                    total_deleted,
                    current_page,
                    len(old_messages),
                    succeeded,
                    failed,
                )

            # ------------------------------------------------
            # VERY IMPORTANT
            #
            # Deletion changes pagination.
            #
            # Always return to page 1 after deleting so
            # messages that shifted from later pages cannot
            # be skipped.
            # ------------------------------------------------

            current_page = 1

            time.sleep(0.5)

            if succeeded == 0:
                # Nothing was successfully deleted. Continuing
                # forever would accomplish nothing.
                break

            continue

        # ----------------------------------------------------
        # NO OLD MESSAGES ON THIS PAGE
        # ----------------------------------------------------

        total_pages = get_total_pages(driver)

        if current_page >= total_pages:
            break

        current_page += 1

    return total_deleted


# ============================================================
# END
# ============================================================
