"""
Messages submenu for Eclipse RPG Automation (Phase 5).

Safety rule for this whole file: the site itself deletes
messages IMMEDIATELY with no confirmation. Every destructive
path here shows a preview of exactly what will be deleted and
requires the user to type DELETE before anything happens.
"""

from datetime import datetime, timedelta

from messages import (
    open_inbox,
    get_messages_on_page,
    get_total_pages,
    get_total_message_count,
    get_message_date,
    delete_messages,
    delete_all_messages,
)


def _print_message_row(index, message):

    subject = message["subject"] or "(no subject)"
    sender = message["sender"] or "(unknown sender)"
    date = message["date"] or "(unknown date)"

    print(f"{index:3}. {subject}  —  {sender}  —  {date}")


def _confirm_delete(count, description):
    """
    Shared confirmation gate for every destructive path.

    Returns True only if the user types DELETE exactly.
    """

    print()
    print("=" * 60)
    print("CONFIRM DELETION")
    print("=" * 60)
    print()
    print(f"You are about to delete {count} message(s).")
    print(description)
    print()
    print("This cannot be undone - Eclipse RPG deletes messages")
    print("immediately, with no site-side confirmation.")
    print()

    answer = input("Type DELETE to confirm, anything else to cancel: ").strip()

    return answer == "DELETE"


# ============================================================
# VIEW INBOX
# ============================================================

def view_inbox(driver):

    page = 1

    while True:

        open_inbox(driver, page=page)

        messages = get_messages_on_page(driver)
        total_pages = get_total_pages(driver)

        print()
        print("=" * 60)
        print(f"INBOX  (page {page} of {total_pages})")
        print("=" * 60)
        print()

        if not messages:
            print("No messages on this page.")

        for i, message in enumerate(messages, 1):
            _print_message_row(i, message)

        print()
        print("N. Next page")
        print("P. Previous page")
        print("V. View a message's full text")
        print("B. Back")

        choice = input("\nChoose: ").strip().lower()

        if choice == "n":

            if page < total_pages:
                page += 1
            else:
                print("Already on the last page.")

        elif choice == "p":

            if page > 1:
                page -= 1
            else:
                print("Already on the first page.")

        elif choice == "v":

            number = input("Message number to view: ").strip()

            try:
                index = int(number) - 1
                message = messages[index]

            except (ValueError, IndexError):
                print("✗ Invalid message number.")
                continue

            print()
            print("=" * 60)
            print(message["subject"] or "(no subject)")
            print("=" * 60)
            print(f"From: {message['sender']}")
            print(f"Date: {message['date']}")
            print()
            print(message["body"] or "(no body found)")
            input("\nPress Enter to continue...")

        elif choice == "b":
            return

        else:
            print("✗ Invalid choice.")


# ============================================================
# DELETE MESSAGES
# ============================================================

def delete_messages_menu(driver):

    while True:

        open_inbox(driver, page=1)

        total_count = get_total_message_count(driver)
        total_pages = get_total_pages(driver)

        print()
        print("=" * 60)
        print("DELETE MESSAGES")
        print("=" * 60)
        print()
        print(f"Messages detected: {total_count}")
        print(f"Pages: {total_pages}")
        print()
        print("1. Delete ALL messages")
        print("2. Delete current page")
        print("3. Delete messages older than X days")
        print("4. Delete selected messages (from current page)")
        print("5. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            _delete_all(driver, total_count)

        elif choice == "2":
            _delete_current_page(driver)

        elif choice == "3":
            _delete_older_than(driver)

        elif choice == "4":
            _delete_selected(driver)

        elif choice == "5":
            return

        else:
            print("✗ Invalid choice.")


def _delete_all(driver, total_count):

    if total_count == 0:
        print("\nInbox is already empty.")
        input("\nPress Enter to continue...")
        return

    if not _confirm_delete(
        total_count,
        "This deletes every message in your inbox, across all pages.",
    ):
        print("\nCancelled.")
        return

    print("\nDeleting... this may take a while for a large inbox.")

    def progress(deleted_so_far):
        print(f"  Deleted {deleted_so_far} so far...")

    deleted = delete_all_messages(driver, progress_callback=progress)

    print(f"\n✓ Deleted {deleted} message(s).")
    input("\nPress Enter to continue...")


def _delete_current_page(driver):

    open_inbox(driver, page=1)
    messages = get_messages_on_page(driver)

    if not messages:
        print("\nNo messages on this page.")
        input("\nPress Enter to continue...")
        return

    print()
    for i, message in enumerate(messages, 1):
        _print_message_row(i, message)

    if not _confirm_delete(
        len(messages),
        "This deletes every message shown above (page 1).",
    ):
        print("\nCancelled.")
        return

    ids = [m["id"] for m in messages]
    succeeded, failed = delete_messages(driver, ids)

    print(f"\n✓ Deleted {succeeded} message(s).", end="")

    if failed:
        print(f" ({failed} failed.)")
    else:
        print()

    input("\nPress Enter to continue...")


def _delete_older_than(driver):

    answer = input("\nDelete messages older than how many days? ").strip()

    try:
        days = int(answer)
    except ValueError:
        print("✗ Invalid number.")
        return

    cutoff = datetime.now() - timedelta(days=days)

    print(f"\nScanning inbox for messages before {cutoff.date()}...")

    total_pages = get_total_pages(driver)

    # Collect matching ids grouped by the page they were found
    # on, since a message can only be deleted while its page
    # is the one currently loaded.
    matches_by_page = {}
    total_matches = 0

    for page in range(1, total_pages + 1):

        open_inbox(driver, page=page)
        messages = get_messages_on_page(driver)

        page_matches = []

        for message in messages:

            message_date = get_message_date(message)

            if message_date is not None and message_date < cutoff:
                page_matches.append(message)

        if page_matches:
            matches_by_page[page] = page_matches
            total_matches += len(page_matches)

    if total_matches == 0:
        print(f"\nNo messages older than {days} day(s) found.")
        input("\nPress Enter to continue...")
        return

    print(f"\nFound {total_matches} message(s) older than {days} day(s):")
    print()

    shown = 0

    for page, page_matches in matches_by_page.items():

        for message in page_matches:

            shown += 1
            _print_message_row(shown, message)

            if shown >= 25:
                break

        if shown >= 25:
            break

    if total_matches > 25:
        print(f"  ... and {total_matches - 25} more.")

    if not _confirm_delete(
        total_matches,
        f"This deletes every message older than {days} day(s), across all pages.",
    ):
        print("\nCancelled.")
        return

    total_deleted = 0

    for page, page_matches in matches_by_page.items():

        open_inbox(driver, page=page)

        ids = [m["id"] for m in page_matches]
        succeeded, _failed = delete_messages(driver, ids)

        total_deleted += succeeded

    print(f"\n✓ Deleted {total_deleted} message(s).")
    input("\nPress Enter to continue...")


def _delete_selected(driver):

    open_inbox(driver, page=1)
    messages = get_messages_on_page(driver)

    if not messages:
        print("\nNo messages on this page.")
        input("\nPress Enter to continue...")
        return

    print()
    for i, message in enumerate(messages, 1):
        _print_message_row(i, message)

    answer = input(
        "\nEnter message numbers to delete "
        "(comma-separated, e.g. 1,3,5): "
    ).strip()

    if not answer:
        print("✗ Nothing entered.")
        return

    indexes = []

    for part in answer.split(","):

        part = part.strip()

        if not part.isdigit():
            print(f"✗ Invalid entry: '{part}'")
            return

        indexes.append(int(part))

    selected = []

    for index in indexes:

        if 1 <= index <= len(messages):
            selected.append(messages[index - 1])
        else:
            print(f"✗ {index} is out of range.")
            return

    if not selected:
        print("✗ No valid messages selected.")
        return

    print()
    for i, message in enumerate(selected, 1):
        _print_message_row(i, message)

    if not _confirm_delete(
        len(selected),
        "This deletes exactly the message(s) listed above.",
    ):
        print("\nCancelled.")
        return

    ids = [m["id"] for m in selected]
    succeeded, failed = delete_messages(driver, ids)

    print(f"\n✓ Deleted {succeeded} message(s).", end="")

    if failed:
        print(f" ({failed} failed.)")
    else:
        print()

    input("\nPress Enter to continue...")


# ============================================================
# MESSAGE STATISTICS
# ============================================================

def message_statistics(driver):

    open_inbox(driver, page=1)

    total_count = get_total_message_count(driver)
    total_pages = get_total_pages(driver)

    print()
    print("=" * 60)
    print("MESSAGE STATISTICS")
    print("=" * 60)
    print()
    print(f"Total messages: {total_count}")
    print(f"Total pages:    {total_pages}")

    input("\nPress Enter to return to the messages menu...")


# ============================================================
# MESSAGES MENU
# ============================================================

def messages_menu(driver):
    while True:

        print()
        print("=" * 60)
        print("MESSAGES")
        print("=" * 60)
        print()
        print("1. View Inbox")
        print("2. Delete Messages")
        print("3. Message Statistics")
        print("4. Back")

        choice = input("\nChoose: ").strip()

        if choice == "1":
            view_inbox(driver)

        elif choice == "2":
            delete_messages_menu(driver)

        elif choice == "3":
            message_statistics(driver)

        elif choice == "4":
            return

        else:
            print("✗ Invalid choice.")
