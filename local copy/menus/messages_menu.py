"""
Messages submenu for Eclipse RPG Automation.

Safety rule:

Eclipse RPG deletes messages immediately.

Every destructive operation therefore requires the user to
explicitly type DELETE before anything is removed.
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
    delete_messages_older_than,
)


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _print_message_row(index, message):

    subject = (
        message.get("subject")
        or "(no subject)"
    )

    sender = (
        message.get("sender")
        or "(unknown sender)"
    )

    date = (
        message.get("date")
        or "(unknown date)"
    )

    print(
        f"{index:3}. "
        f"{subject}  —  "
        f"{sender}  —  "
        f"{date}"
    )


def _confirm_delete(count, description):

    print()
    print("=" * 60)
    print("CONFIRM DELETION")
    print("=" * 60)
    print()

    print(
        f"You are about to delete {count} message(s)."
    )

    print(description)

    print()

    print(
        "This cannot be undone - Eclipse RPG deletes "
        "messages immediately."
    )

    print()

    answer = input(
        "Type DELETE to confirm, "
        "anything else to cancel: "
    ).strip()

    return answer == "DELETE"


# ============================================================
# VIEW INBOX
# ============================================================

def view_inbox(driver):

    page = 1

    while True:

        if not open_inbox(
            driver,
            page=page,
        ):
            print("✗ Could not open inbox.")
            return

        messages = get_messages_on_page(driver)
        total_pages = get_total_pages(driver)

        print()
        print("=" * 60)
        print(
            f"INBOX  (page {page} of {total_pages})"
        )
        print("=" * 60)
        print()

        if not messages:
            print("No messages on this page.")

        for i, message in enumerate(
            messages,
            1,
        ):
            _print_message_row(
                i,
                message,
            )

        print()
        print("N. Next page")
        print("P. Previous page")
        print("V. View message")
        print("B. Back")

        choice = input(
            "\nChoose: "
        ).strip().lower()

        if choice == "n":

            if page < total_pages:
                page += 1
            else:
                print(
                    "Already on the last page."
                )

        elif choice == "p":

            if page > 1:
                page -= 1
            else:
                print(
                    "Already on the first page."
                )

        elif choice == "v":

            number = input(
                "Message number to view: "
            ).strip()

            try:
                index = int(number) - 1
                message = messages[index]

            except (
                ValueError,
                IndexError,
            ):
                print(
                    "✗ Invalid message number."
                )
                continue

            print()
            print("=" * 60)
            print(
                message["subject"]
                or "(no subject)"
            )
            print("=" * 60)

            print(
                f"From: {message['sender']}"
            )

            print(
                f"Date: {message['date']}"
            )

            print()
            print(
                message["body"]
                or "(no body found)"
            )

            input(
                "\nPress Enter to continue..."
            )

        elif choice == "b":
            return

        else:
            print("✗ Invalid choice.")


# ============================================================
# DELETE MENU
# ============================================================

def delete_messages_menu(driver):

    while True:

        print()
        print("=" * 60)
        print("DELETE MESSAGES")
        print("=" * 60)
        print()

        print("1. Delete ALL messages")
        print("2. Delete messages older than X days")
        print("3. Delete current page")
        print("4. Delete selected messages")
        print("5. Back")

        choice = input(
            "\nChoose: "
        ).strip()

        if choice == "1":

            _delete_all(driver)

        elif choice == "2":

            _delete_older_than(driver)

        elif choice == "3":

            _delete_current_page(driver)

        elif choice == "4":

            _delete_selected(driver)

        elif choice == "5":

            return

        else:

            print("✗ Invalid choice.")


# ============================================================
# DELETE ALL
# ============================================================

def _delete_all(driver):

    if not open_inbox(
        driver,
        page=1,
    ):
        print(
            "\n✗ Could not open inbox."
        )
        return

    total_count = get_total_message_count(
        driver
    )

    if total_count == 0:

        print(
            "\nInbox is already empty."
        )

        input(
            "\nPress Enter to continue..."
        )

        return

    print()
    print(
        f"Messages detected: {total_count}"
    )

    if not _confirm_delete(
        total_count,
        "This deletes every message in your inbox.",
    ):

        print("\nCancelled.")
        return

    print()
    print(
        "Deleting all messages..."
    )

    def progress(
        deleted,
        page_count,
        found,
    ):

        print(
            f"  ✓ Deleted {deleted} "
            f"message(s) so far..."
        )

    deleted = delete_all_messages(
        driver,
        progress_callback=progress,
    )

    print()
    print(
        f"✓ Finished. Deleted "
        f"{deleted} message(s)."
    )

    input(
        "\nPress Enter to continue..."
    )


# ============================================================
# DELETE OLDER THAN X DAYS
# ============================================================

def _delete_older_than(driver):

    answer = input(
        "\nDelete messages older than how many days? "
    ).strip()

    try:

        days = int(answer)

    except ValueError:

        print(
            "✗ Invalid number."
        )

        return

    if days < 0:

        print(
            "✗ Number of days cannot be negative."
        )

        return

    cutoff = (
        datetime.now()
        - timedelta(days=days)
    )

    print()
    print("=" * 60)
    print("OLD MESSAGE CLEANUP")
    print("=" * 60)
    print()

    print(
        f"Delete messages older than: "
        f"{days} day(s)"
    )

    print(
        f"Cutoff date: "
        f"{cutoff.strftime('%B %d, %Y %I:%M %p')}"
    )

    print()
    print(
        "The inbox will be scanned dynamically."
    )

    print(
        "Messages will be deleted in batches."
    )

    print(
        "Pagination will be rechecked after "
        "each deletion batch."
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    print()
    print(
        "Scanning inbox for a preview..."
    )

    total_pages = get_total_pages(
        driver
    )

    preview_matches = []
    preview_count = 0

    for page in range(
        1,
        total_pages + 1,
    ):

        if not open_inbox(
            driver,
            page=page,
        ):
            continue

        messages = get_messages_on_page(
            driver
        )

        for message in messages:

            message_date = get_message_date(
                message
            )

            if (
                message_date is not None
                and message_date < cutoff
            ):

                preview_count += 1

                if len(preview_matches) < 25:
                    preview_matches.append(
                        message
                    )

    if preview_count == 0:

        print()
        print(
            f"✓ No messages older than "
            f"{days} day(s) were found."
        )

        input(
            "\nPress Enter to continue..."
        )

        return

    print()
    print(
        f"Found at least "
        f"{preview_count} message(s) "
        f"eligible for deletion."
    )

    print()

    for index, message in enumerate(
        preview_matches,
        1,
    ):

        _print_message_row(
            index,
            message,
        )

    if preview_count > 25:

        print()
        print(
            f"... and "
            f"{preview_count - 25} "
            f"more."
        )

    print()

    if not _confirm_delete(
        preview_count,
        (
            f"This deletes every message "
            f"older than {days} day(s), "
            "across all inbox pages."
        ),
    ):

        print("\nCancelled.")
        return

    # --------------------------------------------------------
    # ACTUAL CLEANUP
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("STARTING CLEANUP")
    print("=" * 60)
    print()

    print(
        "The bot will continuously re-check "
        "the inbox after deletions."
    )

    print()

    def progress(
        deleted,
        page,
        found,
        succeeded,
        failed,
    ):

        print(
            f"Page {page}: "
            f"found {found} old message(s) | "
            f"deleted {succeeded} | "
            f"failed {failed} | "
            f"total deleted {deleted}"
        )

    deleted = delete_messages_older_than(
        driver,
        cutoff,
        progress_callback=progress,
    )

    print()
    print("=" * 60)
    print("CLEANUP COMPLETE")
    print("=" * 60)
    print()

    print(
        f"✓ Messages deleted: {deleted}"
    )

    input(
        "\nPress Enter to continue..."
    )


# ============================================================
# DELETE CURRENT PAGE
# ============================================================

def _delete_current_page(driver):

    if not open_inbox(
        driver,
        page=1,
    ):
        print(
            "\n✗ Could not open inbox."
        )
        return

    messages = get_messages_on_page(
        driver
    )

    if not messages:

        print(
            "\nNo messages on this page."
        )

        input(
            "\nPress Enter to continue..."
        )

        return

    print()

    for index, message in enumerate(
        messages,
        1,
    ):

        _print_message_row(
            index,
            message,
        )

    print()

    if not _confirm_delete(
        len(messages),
        "This deletes every message shown above.",
    ):

        print("\nCancelled.")
        return

    ids = [
        message["id"]
        for message in messages
    ]

    succeeded, failed = delete_messages(
        driver,
        ids,
    )

    print()

    print(
        f"✓ Deleted {succeeded} message(s).",
        end="",
    )

    if failed:

        print(
            f" {failed} failed."
        )

    else:

        print()

    input(
        "\nPress Enter to continue..."
    )


# ============================================================
# DELETE SELECTED
# ============================================================

def _delete_selected(driver):

    if not open_inbox(
        driver,
        page=1,
    ):
        print(
            "\n✗ Could not open inbox."
        )
        return

    messages = get_messages_on_page(
        driver
    )

    if not messages:

        print(
            "\nNo messages on this page."
        )

        input(
            "\nPress Enter to continue..."
        )

        return

    print()

    for index, message in enumerate(
        messages,
        1,
    ):

        _print_message_row(
            index,
            message,
        )

    answer = input(
        "\nEnter message numbers to delete "
        "(comma-separated, e.g. 1,3,5): "
    ).strip()

    if not answer:

        print(
            "✗ Nothing entered."
        )

        return

    indexes = []

    for part in answer.split(","):

        part = part.strip()

        if not part.isdigit():

            print(
                f"✗ Invalid entry: '{part}'"
            )

            return

        indexes.append(
            int(part)
        )

    selected = []

    for index in indexes:

        if 1 <= index <= len(messages):

            selected.append(
                messages[index - 1]
            )

        else:

            print(
                f"✗ {index} is out of range."
            )

            return

    if not selected:

        print(
            "✗ No valid messages selected."
        )

        return

    print()
    print("Messages selected:")

    for index, message in enumerate(
        selected,
        1,
    ):

        _print_message_row(
            index,
            message,
        )

    if not _confirm_delete(
        len(selected),
        "This deletes exactly the messages listed above.",
    ):

        print("\nCancelled.")
        return

    ids = [
        message["id"]
        for message in selected
    ]

    succeeded, failed = delete_messages(
        driver,
        ids,
    )

    print()

    print(
        f"✓ Deleted {succeeded} message(s).",
        end="",
    )

    if failed:

        print(
            f" {failed} failed."
        )

    else:

        print()

    input(
        "\nPress Enter to continue..."
    )


# ============================================================
# MESSAGE STATISTICS
# ============================================================

def message_statistics(driver):

    print()
    print("=" * 60)
    print("MESSAGE STATISTICS")
    print("=" * 60)
    print()

    print(
        "Scanning inbox..."
    )

    total_count = get_total_message_count(
        driver
    )

    if not open_inbox(
        driver,
        page=1,
    ):
        print(
            "✗ Could not return to inbox."
        )

        return

    total_pages = get_total_pages(
        driver
    )

    print()
    print(
        f"Total messages: {total_count}"
    )

    print(
        f"Total pages:    {total_pages}"
    )

    input(
        "\nPress Enter to return to "
        "the messages menu..."
    )


# ============================================================
# MAIN MESSAGES MENU
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

        choice = input(
            "\nChoose: "
        ).strip()

        if choice == "1":

            view_inbox(driver)

        elif choice == "2":

            delete_messages_menu(driver)

        elif choice == "3":

            message_statistics(driver)

        elif choice == "4":

            return

        else:

            print(
                "✗ Invalid choice."
        )
