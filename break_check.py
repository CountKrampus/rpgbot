"""
Helper for automation modes to check for and handle breaks.

Call check_and_handle_break() after each major action completes
(hunt, search, battle, etc.). It handles entering break mode,
waiting through the break, and auto-resuming.
"""

import time
from break_timer import (
    should_trigger_break,
    is_in_break_mode,
    enter_break_mode,
    check_break_timer,
    get_break_time_remaining_formatted,
)


def check_and_handle_break():
    """
    Call this after completing an action (hunt, search, battle, etc.)
    in any automation mode.

    If break is due:
      - Enters break mode
      - Waits through the break period (with countdown)
      - Auto-resumes when done

    Returns True if a break just completed and automation should
    resume. Returns False if no break occurred or still waiting.
    """

    # Check if we need to start a break
    if should_trigger_break():
        enter_break_mode()

    # If we're in a break, wait it out
    if is_in_break_mode():
        return wait_through_break()

    # No break happening
    return False


def wait_through_break():
    """
    Block and wait for break to finish, showing countdown.
    Returns True when break ends and automation should resume.
    """

    # Give user a moment to read the break message
    time.sleep(1)

    print("\nWaiting for break to finish...")
    print()

    # Check every 5 seconds for break end
    while is_in_break_mode():

        remaining = get_break_time_remaining_formatted()
        print(f"  Break time remaining: {remaining}", end="\r")

        # Check if break is done
        if check_break_timer():
            print()  # Clear the line
            return True

        time.sleep(5)

    return False
