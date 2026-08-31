"""
Messages submenu for Eclipse RPG Automation.

Safety rule:
    Eclipse RPG deletes messages immediately.
    Every destructive operation requires explicit user confirmation.
"""

from datetime import datetime, timedelta
import os
import sys
import platform
import time
import re

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
# ANSI & STYLING
# ============================================================

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
PURPLE = "\033[38;5;141m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
WHITE = "\033[97m"
GRAY = "\033[90m"
GOLD = "\033[38;5;220m"

BORDER_COLOR = PURPLE
CATEGORY_COLOR = f"{BOLD}{CYAN}"
KEY_COLOR = f"{BOLD}{YELLOW}"
NAME_COLOR = f"{BOLD}{WHITE}"
DESC_COLOR = GRAY

ANSI_STRIP_REGEX = re.compile(r"\x1b\[[0-9;]*[mK]")


def _strip_ansi(text: str) -> str:
    return ANSI_STRIP_REGEX.sub("", text)


def _row(content: str, width: int = 71) -> str:
    v_len = len(_strip_ansi(content))
    pad = max(0, width - v_len)
    return f"{BORDER_COLOR}║{RESET}{content}{' ' * pad}{BORDER_COLOR}║{RESET}"


# ============================================================
# DISPLAY HELPERS
# ============================================================

def _print_message_row(index, message):
    subject = message.get("subject") or "(no subject)"
    sender = message.get("sender") or "(unknown sender)"
    date = message.get("date") or "(unknown date)"

    print(
        f"  {KEY_COLOR}[{index:2d}]{RESET} "
        f"{WHITE}{subject:<28}{RESET} "
        f"{CYAN}{sender:<16}{RESET} "
        f"{GRAY}{date}{RESET}"
    )


def _confirm_delete(count, description):
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{RED}│{RESET}{content}{' ' * pad}{RED}│{RESET}"

    print()
    print(f"{RED}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{RED}⚠  CONFIRM DESTRUCTION  ⚠{RESET}"))
    print(f"{RED}├{'─' * w}┤{RESET}")
    print(_drow(f"  Target count: {WHITE}{count}{RESET} message(s)"))
    print(_drow(f"  {GRAY}{description}{RESET}"))
    print(_drow(""))
    print(_drow(f"  {YELLOW}Warning: This cannot be undone! Messages are deleted immediately.{RESET}"))
    print(f"{RED}╰{'─' * w}╯{RESET}")
    print()

    answer = input(
        f"{BOLD}{RED}❯ Type DELETE to confirm deletion, or anything else to cancel:{RESET} "
    ).strip()

    return answer == "DELETE"


# ============================================================
# VIEW INBOX
# ============================================================

def view_inbox(driver):
    page = 1
    w = 71

    while True:
        if not open_inbox(driver, page=page):
            print(f"{RED}✗ Could not open inbox.{RESET}")
            time.sleep(1.0)
            return

        messages = get_messages_on_page(driver)
        total_pages = get_total_pages(driver)
        total_count = get_total_message_count(driver)

        top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
        mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
        bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

        hud = f"  {GRAY}INBOX:{RESET} {CYAN}Page {page} of {total_pages}{RESET}  │  {GRAY}TOTAL MESSAGES:{RESET} {CYAN}{total_count}{RESET}"

        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}📬  PRIVATE MESSAGE INBOX{RESET}", w))
        print(mid_border)
        print(_row(hud, w))
        print(mid_border)
        print(_row("", w))

        if not messages:
            print(_row(f"    {GRAY}No messages on this page.{RESET}", w))
        else:
            for i, message in enumerate(messages, 1):
                subject = message.get("subject") or "(no subject)"
                sender = message.get("sender") or "(unknown)"
                date = message.get("date") or ""
                line = f"    {KEY_COLOR}[{i:2d}]{RESET} {WHITE}{subject[:24]:<24}{RESET} {CYAN}{sender[:14]:<14}{RESET} {GRAY}{date[:20]}{RESET}"
                print(_row(line, w))

        print(_row("", w))
        print(mid_border)
        print(_row(f"  {KEY_COLOR}[N]{RESET} {WHITE}Next Page{RESET}   {KEY_COLOR}[P]{RESET} {WHITE}Prev Page{RESET}   {KEY_COLOR}[V]{RESET} {WHITE}View Message Detail{RESET}   {RED}[B]{RESET} {WHITE}Back{RESET}", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Option / Message # {GRAY}[N/P/V/B]:{RESET} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "n":
            if page < total_pages:
                page += 1
            else:
                print(f"{YELLOW}Already on the last page.{RESET}")
                time.sleep(0.8)

        elif choice == "p":
            if page > 1:
                page -= 1
            else:
                print(f"{YELLOW}Already on the first page.{RESET}")
                time.sleep(0.8)

        elif choice == "v" or choice.isdigit():
            if choice == "v":
                number = input(f"{BOLD}{CYAN}❯ Message number to view {GRAY}[1-{len(messages)}]{CYAN}:{RESET} ").strip()
            else:
                number = choice

            try:
                index = int(number) - 1
                message = messages[index]
            except (ValueError, IndexError):
                print(f"{RED}✗ Invalid message number.{RESET}")
                time.sleep(0.8)
                continue

            dw = 60
            def _drow(content):
                vlen = len(_strip_ansi(content))
                pad = max(0, dw - vlen)
                return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

            print()
            print(f"{BORDER_COLOR}╭{'─' * dw}╮{RESET}")
            print(_drow(f"  {BOLD}{MAGENTA}MESSAGE DETAIL{RESET}"))
            print(f"{BORDER_COLOR}├{'─' * dw}┤{RESET}")
            print(_drow(f"  {GRAY}Subject:{RESET} {WHITE}{message.get('subject') or '(no subject)'}{RESET}"))
            print(_drow(f"  {GRAY}From:   {RESET} {CYAN}{message.get('sender') or '(unknown)'}{RESET}"))
            print(_drow(f"  {GRAY}Date:   {RESET} {GRAY}{message.get('date') or ''}{RESET}"))
            print(f"{BORDER_COLOR}├{'─' * dw}┤{RESET}")
            body = message.get("body") or "(no message body)"
            for line in body.split("\n"):
                print(_drow(f"  {WHITE}{line}{RESET}"))
            print(f"{BORDER_COLOR}╰{'─' * dw}╯{RESET}")
            print()
            input(f"{GRAY}Press Enter to continue...{RESET}")

        elif choice == "b":
            return
        else:
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(0.8)


# ============================================================
# DELETE MENU
# ============================================================

def delete_messages_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        print()
        print(top_border)
        print(_row(f"  {BOLD}{RED}🗑️  DELETE & CLEANUP MESSAGES{RESET}", w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}Delete ALL Messages{RESET}         {DESC_COLOR}— Purge every message across all inbox pages{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Delete Messages Older Than X{RESET} {DESC_COLOR}— Bulk remove messages by age / days{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Delete Current Page{RESET}          {DESC_COLOR}— Remove all messages on the current page{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 4]{RESET} {NAME_COLOR}Delete Selected Messages{RESET}     {DESC_COLOR}— Pick specific messages by list numbers{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 5]{RESET} {RED}Back{RESET}                         {DESC_COLOR}— Return to messages menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-5]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

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
            print(f"{RED}✗ Invalid choice.{RESET}")
            time.sleep(1.0)


def _delete_all(driver):
    if not open_inbox(driver, page=1):
        print(f"{RED}\n✗ Could not open inbox.{RESET}")
        time.sleep(1.0)
        return

    total_count = get_total_message_count(driver)

    if total_count == 0:
        print(f"{GREEN}\n✓ Inbox is already empty.{RESET}")
        input(f"\n{GRAY}Press Enter to continue...{RESET}")
        return

    print(f"\n{CYAN}⚡ Messages detected:{RESET} {WHITE}{total_count}{RESET}")

    if not _confirm_delete(total_count, "This will delete every message in your inbox permanently."):
        print(f"\n{GRAY}Deletion cancelled.{RESET}")
        time.sleep(0.8)
        return

    print(f"\n{CYAN}⚡ Deleting all messages...{RESET}")

    def progress(deleted, page_count, found):
        print(f"  {GREEN}✓{RESET} Deleted {deleted} message(s) so far...")

    deleted = delete_all_messages(driver, progress_callback=progress)

    print(f"\n{GREEN}✓ Finished. Successfully deleted {deleted} message(s).{RESET}")
    input(f"\n{GRAY}Press Enter to continue...{RESET}")


def _delete_older_than(driver):
    answer = input(f"\n{BOLD}{CYAN}❯ Delete messages older than how many days?:{RESET} ").strip()

    try:
        days = int(answer)
    except ValueError:
        print(f"{RED}✗ Invalid number.{RESET}")
        time.sleep(1.0)
        return

    if days < 0:
        print(f"{RED}✗ Number of days cannot be negative.{RESET}")
        time.sleep(1.0)
        return

    cutoff = datetime.now() - timedelta(days=days)

    print(f"\n{CYAN}⚡ Scanning inbox for messages older than {days} day(s) (Cutoff: {cutoff.strftime('%B %d, %Y')})...{RESET}")

    total_pages = get_total_pages(driver)
    preview_matches = []
    preview_count = 0

    for page in range(1, total_pages + 1):
        if not open_inbox(driver, page=page):
            continue

        messages = get_messages_on_page(driver)
        for message in messages:
            message_date = get_message_date(message)
            if message_date is not None and message_date < cutoff:
                preview_count += 1
                if len(preview_matches) < 20:
                    preview_matches.append(message)

    if preview_count == 0:
        print(f"\n{GREEN}✓ No messages older than {days} day(s) were found.{RESET}")
        input(f"\n{GRAY}Press Enter to continue...{RESET}")
        return

    print(f"\n{GOLD}Found {preview_count} message(s) eligible for deletion:{RESET}\n")
    for index, message in enumerate(preview_matches, 1):
        _print_message_row(index, message)

    if preview_count > 20:
        print(f"  {GRAY}... and {preview_count - 20} more.{RESET}")

    if not _confirm_delete(preview_count, f"This deletes every message older than {days} day(s) across all inbox pages."):
        print(f"\n{GRAY}Deletion cancelled.{RESET}")
        time.sleep(0.8)
        return

    print(f"\n{CYAN}⚡ Executing cleanup...{RESET}")

    def progress(deleted, page, found, succeeded, failed):
        print(f"  {GRAY}Page {page}:{RESET} found {found} | deleted {succeeded} | total: {deleted}")

    deleted = delete_messages_older_than(driver, cutoff, progress_callback=progress)

    print(f"\n{GREEN}✓ Cleanup complete! Deleted {deleted} message(s).{RESET}")
    input(f"\n{GRAY}Press Enter to continue...{RESET}")


def _delete_current_page(driver):
    if not open_inbox(driver, page=1):
        print(f"{RED}\n✗ Could not open inbox.{RESET}")
        return

    messages = get_messages_on_page(driver)
    if not messages:
        print(f"{GREEN}\n✓ No messages on this page.{RESET}")
        input(f"\n{GRAY}Press Enter to continue...{RESET}")
        return

    print(f"\n{GOLD}Messages on current page:{RESET}\n")
    for index, message in enumerate(messages, 1):
        _print_message_row(index, message)

    if not _confirm_delete(len(messages), "This deletes all messages listed above."):
        print(f"\n{GRAY}Deletion cancelled.{RESET}")
        time.sleep(0.8)
        return

    ids = [message["id"] for message in messages]
    succeeded, failed = delete_messages(driver, ids)

    print(f"\n{GREEN}✓ Deleted {succeeded} message(s).{RESET}", end="")
    if failed:
        print(f" {RED}({failed} failed){RESET}")
    else:
        print()

    input(f"\n{GRAY}Press Enter to continue...{RESET}")


def _delete_selected(driver):
    if not open_inbox(driver, page=1):
        print(f"{RED}\n✗ Could not open inbox.{RESET}")
        return

    messages = get_messages_on_page(driver)
    if not messages:
        print(f"{GREEN}\n✓ No messages on this page.{RESET}")
        input(f"\n{GRAY}Press Enter to continue...{RESET}")
        return

    print(f"\n{GOLD}Messages on current page:{RESET}\n")
    for index, message in enumerate(messages, 1):
        _print_message_row(index, message)

    answer = input(f"\n{BOLD}{CYAN}❯ Enter message numbers to delete {GRAY}(comma-separated, e.g. 1,3,5){CYAN}:{RESET} ").strip()
    if not answer:
        print(f"{YELLOW}✗ Nothing entered.{RESET}")
        time.sleep(0.8)
        return

    indexes = []
    for part in answer.split(","):
        part = part.strip()
        if not part.isdigit():
            print(f"{RED}✗ Invalid entry: '{part}'{RESET}")
            time.sleep(1.0)
            return
        indexes.append(int(part))

    selected = []
    for index in indexes:
        if 1 <= index <= len(messages):
            selected.append(messages[index - 1])
        else:
            print(f"{RED}✗ {index} is out of range.{RESET}")
            time.sleep(1.0)
            return

    if not selected:
        print(f"{YELLOW}✗ No valid messages selected.{RESET}")
        time.sleep(1.0)
        return

    print(f"\n{GOLD}Selected for deletion:{RESET}\n")
    for index, message in enumerate(selected, 1):
        _print_message_row(index, message)

    if not _confirm_delete(len(selected), "This deletes exactly the selected messages listed above."):
        print(f"\n{GRAY}Deletion cancelled.{RESET}")
        time.sleep(0.8)
        return

    ids = [message["id"] for message in selected]
    succeeded, failed = delete_messages(driver, ids)

    print(f"\n{GREEN}✓ Deleted {succeeded} message(s).{RESET}", end="")
    if failed:
        print(f" {RED}({failed} failed){RESET}")
    else:
        print()

    input(f"\n{GRAY}Press Enter to continue...{RESET}")


def message_statistics(driver):
    w = 60
    def _drow(content):
        vlen = len(_strip_ansi(content))
        pad = max(0, w - vlen)
        return f"{BORDER_COLOR}│{RESET}{content}{' ' * pad}{BORDER_COLOR}│{RESET}"

    print(f"\n{CYAN}⚡ Scanning inbox statistics...{RESET}")
    total_count = get_total_message_count(driver)

    if not open_inbox(driver, page=1):
        print(f"{RED}✗ Could not open inbox.{RESET}")
        return

    total_pages = get_total_pages(driver)

    print()
    print(f"{BORDER_COLOR}╭{'─' * w}╮{RESET}")
    print(_drow(f"  {BOLD}{MAGENTA}📊  INBOX STATISTICS{RESET}"))
    print(f"{BORDER_COLOR}├{'─' * w}┤{RESET}")
    print(_drow(f"  {GRAY}Total Messages in Inbox:{RESET} {CYAN}{total_count:,}{RESET}"))
    print(_drow(f"  {GRAY}Total Inbox Pages:      {RESET} {CYAN}{total_pages:,}{RESET}"))
    print(f"{BORDER_COLOR}╰{'─' * w}╯{RESET}")
    print()
    input(f"{GRAY}Press Enter to return to messages menu...{RESET}")


def messages_menu(driver):
    w = 71
    top_border = f"{BORDER_COLOR}╔{'═' * w}╗{RESET}"
    mid_border = f"{BORDER_COLOR}╠{'═' * w}╣{RESET}"
    bot_border = f"{BORDER_COLOR}╚{'═' * w}╝{RESET}"

    while True:
        print()
        print(top_border)
        print(_row(f"  {BOLD}{MAGENTA}📫  PRIVATE MESSAGES & INBOX{RESET}", w))
        print(mid_border)
        print(_row("", w))
        print(_row(f"    {KEY_COLOR}[ 1]{RESET} {NAME_COLOR}View Inbox{RESET}          {DESC_COLOR}— Read messages, view pages & open details{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 2]{RESET} {NAME_COLOR}Delete Messages{RESET}     {DESC_COLOR}— Bulk deletion tools & date-based filters{RESET}", w))
        print(_row(f"    {KEY_COLOR}[ 3]{RESET} {NAME_COLOR}Message Statistics{RESET}  {DESC_COLOR}— Total message count and pagination stats{RESET}", w))
        print(_row("", w))
        print(_row(f"    {RED}{BOLD}[ 4]{RESET} {RED}Back{RESET}                {DESC_COLOR}— Return to main menu{RESET}", w))
        print(_row("", w))
        print(bot_border)

        try:
            choice = input(f"\n{BOLD}{CYAN}❯ Select Option {GRAY}[1-4]{CYAN}:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "1":
            view_inbox(driver)
        elif choice == "2":
            delete_messages_menu(driver)
        elif choice == "3":
            message_statistics(driver)
        elif choice == "4":
            return
        else:
            print(f"\n{RED}✗ Invalid choice '{choice}'. Please choose 1-4.{RESET}")
            time.sleep(1.0)
