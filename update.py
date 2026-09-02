#!/usr/bin/env python3
"""
RPGBot Auto-Update System

Safe GitHub updater for RPGBot.

The updater protects the local bot when the local version is newer
than GitHub, and refuses to overwrite uncommitted or diverged work.

Usage:
    python update.py
    python update.py --check
    python update.py --status
    python update.py --no-restart
    python update.py --help
"""

import subprocess
import os
import sys
import json
from datetime import datetime


# ============================================================
# CONFIGURATION
# ============================================================

GITHUB_REMOTE = "origin"
GITHUB_BRANCH = "main"

BOT_SCRIPT = "main.py"
UPDATE_LOG_FILE = ".update_log"


# ============================================================
# WINDOWS CONSOLE SAFETY
# ============================================================

def setup_console():
    """
    Make stdout/stderr safe for Windows consoles.

    Some Windows console environments cannot print Unicode
    emoji characters. The updater therefore uses plain ASCII
    status messages.
    """

    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(
                encoding="utf-8",
                errors="replace"
            )

        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(
                encoding="utf-8",
                errors="replace"
            )

    except Exception:
        pass


setup_console()


# ============================================================
# GIT HELPERS
# ============================================================

def run_git(args, timeout=30):
    """
    Run a Git command.
    """

    return subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout
    )


def is_git_repo():
    """
    Check whether the current directory is a Git repository.
    """

    try:
        result = run_git(
            ["rev-parse", "--is-inside-work-tree"],
            timeout=5
        )

        return (
            result.returncode == 0
            and result.stdout.strip().lower() == "true"
        )

    except Exception:
        return False


def get_current_branch():
    """
    Return the current Git branch.
    """

    try:
        result = run_git(
            ["rev-parse", "--abbrev-ref", "HEAD"],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


def get_current_commit():
    """
    Return the full local commit SHA.
    """

    try:
        result = run_git(
            ["rev-parse", "HEAD"],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


def get_current_commit_short():
    """
    Return the shortened local commit SHA.
    """

    commit = get_current_commit()

    if commit:
        return commit[:7]

    return None


def get_latest_commit():
    """
    Return the GitHub main commit SHA.
    """

    try:
        result = run_git(
            [
                "rev-parse",
                f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
            ],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


def get_latest_commit_short():
    """
    Return the shortened GitHub commit SHA.
    """

    commit = get_latest_commit()

    if commit:
        return commit[:7]

    return None


def get_merge_base():
    """
    Return the common ancestor between local HEAD and GitHub.

    Returns None when the histories are unrelated.
    """

    try:
        result = run_git(
            [
                "merge-base",
                "HEAD",
                f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
            ],
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


# ============================================================
# COMMIT RELATIONSHIP
# ============================================================

def get_commit_relationship():
    """
    Determine how the local version relates to GitHub.

    Returns:

        same
        local_newer
        github_newer
        diverged
        unrelated
        unknown
    """

    local = get_current_commit()
    remote = get_latest_commit()

    if not local or not remote:
        return "unknown"

    if local == remote:
        return "same"

    merge_base = get_merge_base()

    # The local repository and GitHub repository have no
    # common ancestor.
    if not merge_base:
        return "unrelated"

    # GitHub is an ancestor of the local version.
    result = run_git(
        [
            "merge-base",
            "--is-ancestor",
            f"{GITHUB_REMOTE}/{GITHUB_BRANCH}",
            "HEAD"
        ],
        timeout=10
    )

    if result.returncode == 0:
        return "local_newer"

    # Local is an ancestor of GitHub.
    result = run_git(
        [
            "merge-base",
            "--is-ancestor",
            "HEAD",
            f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
        ],
        timeout=10
    )

    if result.returncode == 0:
        return "github_newer"

    return "diverged"


# ============================================================
# LOCAL CHANGE DETECTION
# ============================================================

def has_local_changes():
    """
    Check for uncommitted changes.
    """

    try:
        result = run_git(
            ["status", "--porcelain"],
            timeout=10
        )

        if result.returncode != 0:
            return False

        return bool(result.stdout.strip())

    except Exception:
        return False


def get_local_changes():
    """
    Return local Git changes.
    """

    try:
        result = run_git(
            ["status", "--short"],
            timeout=10
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return ""


# ============================================================
# GITHUB FETCH
# ============================================================

def fetch_github():
    """
    Fetch GitHub's main branch.

    This does NOT modify bot files.
    """

    try:

        print()
        print("[INFO] Fetching latest version from GitHub...")

        result = run_git(
            [
                "fetch",
                GITHUB_REMOTE,
                GITHUB_BRANCH
            ],
            timeout=60
        )

        if result.returncode != 0:

            print()
            print("[ERROR] GitHub fetch failed.")

            error = (
                result.stderr.strip()
                or result.stdout.strip()
                or "Unknown Git error."
            )

            print()
            print(f"Error: {error}")

            return False

        print("[OK] GitHub connection successful")

        return True

    except subprocess.TimeoutExpired:

        print()
        print("[ERROR] GitHub fetch timed out.")

        return False

    except Exception as e:

        print()
        print("[ERROR] Error contacting GitHub:")
        print(f"        {type(e).__name__}: {e}")

        return False


# ============================================================
# STATUS SUMMARY
# ============================================================

def print_status_summary(relationship):
    """
    Display the relationship between local and GitHub.
    """

    print()

    if relationship == "same":

        print("[OK] LOCAL AND GITHUB ARE THE SAME")
        print()
        print("Your bot is already synchronized with GitHub.")

    elif relationship == "local_newer":

        print("[LOCAL NEWER]")
        print()
        print("Your local bot contains newer commits than GitHub.")
        print()
        print("Your local version will NOT be overwritten.")

    elif relationship == "github_newer":

        print("[UPDATE AVAILABLE]")
        print()
        print("GitHub contains commits that your local version does not.")

    elif relationship == "diverged":

        print("[WARNING] LOCAL AND GITHUB HAVE DIVERGED")
        print()
        print("Both versions contain unique changes.")
        print()
        print("The updater will NOT automatically overwrite either version.")

    elif relationship == "unrelated":

        print("[PROTECTED] LOCAL AND GITHUB HAVE UNRELATED HISTORIES")
        print()
        print("Your local bot was initialized separately from GitHub.")
        print()
        print("Your local version remains protected.")
        print()
        print("The older GitHub version will NOT overwrite it.")

    else:

        print("[ERROR] VERSION RELATIONSHIP UNKNOWN")
        print()
        print("Git could not determine how the versions relate.")


# ============================================================
# FILE DIFFERENCES
# ============================================================

def get_file_difference():
    """
    Show informational differences between local HEAD and GitHub.
    """

    try:

        result = run_git(
            [
                "diff",
                "--stat",
                "HEAD",
                f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
            ],
            timeout=15
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return ""


# ============================================================
# CHECK FOR UPDATES
# ============================================================

def check_for_updates():
    """
    Check for a safe GitHub update.

    Returns True only when GitHub is newer and the update
    relationship can be safely handled.
    """

    print()
    print("=" * 60)
    print("CHECKING FOR UPDATES")
    print("=" * 60)

    # --------------------------------------------------------
    # Git repository
    # --------------------------------------------------------

    if not is_git_repo():

        print()
        print("[ERROR] This directory is not a Git repository.")

        return False

    # --------------------------------------------------------
    # Fetch
    # --------------------------------------------------------

    if not fetch_github():
        return False

    # --------------------------------------------------------
    # Commits
    # --------------------------------------------------------

    current = get_current_commit()
    latest = get_latest_commit()

    if current is None:

        print()
        print("[ERROR] Could not determine local Git version.")

        return False

    if latest is None:

        print()
        print("[ERROR] Could not determine GitHub version.")

        return False

    print()
    print(f"Local commit:  {current[:7]}")
    print(f"GitHub commit: {latest[:7]}")

    # --------------------------------------------------------
    # Local changes
    # --------------------------------------------------------

    local_changes = has_local_changes()

    if local_changes:

        print()
        print("[WARNING] Local uncommitted changes detected.")

        changes = get_local_changes()

        if changes:

            print()
            print("Local changes:")

            for line in changes.splitlines():
                print(f"  {line}")

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    relationship = get_commit_relationship()

    print_status_summary(relationship)

    # --------------------------------------------------------
    # Same
    # --------------------------------------------------------

    if relationship == "same":
        return False

    # --------------------------------------------------------
    # Local newer
    # --------------------------------------------------------

    if relationship == "local_newer":

        print()
        print("[PROTECTED] Your local version is newer.")
        print()
        print("No update will be performed.")

        return False

    # --------------------------------------------------------
    # Unrelated
    # --------------------------------------------------------

    if relationship == "unrelated":

        print()
        print("[PROTECTED] Local version remains authoritative.")
        print()
        print("No automatic update will be performed.")

        return False

    # --------------------------------------------------------
    # Diverged
    # --------------------------------------------------------

    if relationship == "diverged":

        print()
        print("[WARNING] Automatic updating is disabled.")
        print()
        print("The local and GitHub versions contain different histories.")
        print()
        print("Nothing will be overwritten.")

        diff = get_file_difference()

        if diff:

            print()
            print("Differences:")
            print()
            print(diff)

        return False

    # --------------------------------------------------------
    # GitHub newer
    # --------------------------------------------------------

    if relationship == "github_newer":

        print()
        print("[UPDATE AVAILABLE]")

        try:

            result = run_git(
                [
                    "log",
                    "--oneline",
                    f"HEAD..{GITHUB_REMOTE}/{GITHUB_BRANCH}"
                ],
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():

                print()
                print("New GitHub commits:")

                for line in result.stdout.strip().splitlines():
                    print(f"  - {line}")

        except Exception:
            pass

        if local_changes:

            print()
            print("[WARNING] Local changes detected.")
            print()
            print("The updater will NOT overwrite them.")

        return True

    # --------------------------------------------------------
    # Unknown
    # --------------------------------------------------------

    print()
    print("[ERROR] Could not safely determine update status.")

    return False


# ============================================================
# SAFE UPDATE
# ============================================================

def pull_updates():
    """
    Perform a safe fast-forward update.

    This function never uses:

        git reset --hard
        git checkout -- .
        git clean -fd
    """

    print()
    print("=" * 60)
    print("UPDATING BOT")
    print("=" * 60)

    if not is_git_repo():

        print()
        print("[ERROR] Not a Git repository.")

        return False

    # --------------------------------------------------------
    # Protect uncommitted changes
    # --------------------------------------------------------

    if has_local_changes():

        print()
        print("[BLOCKED] Local changes detected.")
        print()
        print("The updater will not overwrite your local changes.")

        changes = get_local_changes()

        if changes:

            print()
            print("Changes found:")

            for line in changes.splitlines():
                print(f"  {line}")

        print()
        print("Commit your changes before updating.")

        return False

    # --------------------------------------------------------
    # Fetch
    # --------------------------------------------------------

    if not fetch_github():
        return False

    # --------------------------------------------------------
    # Relationship
    # --------------------------------------------------------

    relationship = get_commit_relationship()

    if relationship == "same":

        print()
        print("[OK] Already up to date.")

        return False

    if relationship == "local_newer":

        print()
        print("[BLOCKED] Local version is newer than GitHub.")
        print()
        print("Your local bot will not be overwritten.")

        return False

    if relationship == "unrelated":

        print()
        print("[BLOCKED] Local and GitHub histories are unrelated.")
        print()
        print("Your local bot remains protected.")

        return False

    if relationship == "diverged":

        print()
        print("[BLOCKED] Local and GitHub histories have diverged.")
        print()
        print("Automatic merging is disabled for safety.")

        return False

    if relationship != "github_newer":

        print()
        print("[ERROR] GitHub cannot be safely applied.")

        return False

    # --------------------------------------------------------
    # Fast-forward update
    # --------------------------------------------------------

    print()
    print("GitHub is newer.")
    print()
    print("Performing safe fast-forward update...")

    try:

        result = run_git(
            [
                "pull",
                "--ff-only",
                GITHUB_REMOTE,
                GITHUB_BRANCH
            ],
            timeout=60
        )

        if result.returncode == 0:

            print()
            print("[OK] Update successful!")

            if result.stdout.strip():

                print()

                for line in result.stdout.strip().splitlines():

                    if line.strip():
                        print(f"  {line}")

            return True

        print()
        print("[ERROR] Update failed.")

        error = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Unknown Git error."
        )

        print()
        print(f"Error: {error}")

        return False

    except subprocess.TimeoutExpired:

        print()
        print("[ERROR] Update timed out.")

        return False

    except Exception as e:

        print()
        print("[ERROR] Error during update:")
        print(f"        {type(e).__name__}: {e}")

        return False


# ============================================================
# RESTART BOT
# ============================================================

def restart_bot():
    """
    Restart main.py using the current Python interpreter.
    """

    print()
    print("=" * 60)
    print("RESTARTING BOT")
    print("=" * 60)

    print()
    print("Starting bot...")

    try:

        subprocess.run(
            [sys.executable, BOT_SCRIPT],
            check=False
        )

    except KeyboardInterrupt:

        print()
        print("[WARNING] Bot interrupted by user.")

        sys.exit(0)

    except Exception as e:

        print()
        print("[ERROR] Could not start bot:")
        print(f"        {type(e).__name__}: {e}")

        sys.exit(1)


# ============================================================
# STATUS
# ============================================================

def show_status():
    """
    Display detailed update status.
    """

    print()
    print("=" * 60)
    print("RPGBOT UPDATE STATUS")
    print("=" * 60)

    if not is_git_repo():

        print()
        print("[ERROR] Git repository not initialized.")

        return 1

    local = get_current_commit()
    branch = get_current_branch()

    print()
    print(f"Local branch:  {branch or 'Unknown'}")
    print(
        f"Local commit:  "
        f"{local[:7] if local else 'Unknown'}"
    )

    if fetch_github():

        remote = get_latest_commit()

        print(
            f"GitHub commit: "
            f"{remote[:7] if remote else 'Unknown'}"
        )

        relationship = get_commit_relationship()

        print_status_summary(relationship)

    print()

    if has_local_changes():

        print("[WARNING] Working directory has uncommitted changes.")

        changes = get_local_changes()

        if changes:

            print()

            for line in changes.splitlines():
                print(f"  {line}")

    else:

        print("[OK] Working directory is clean.")

    print()

    return 0


# ============================================================
# HELP
# ============================================================

def show_help():

    print(__doc__)

    print()
    print("=" * 60)
    print("COMMANDS")
    print("=" * 60)

    print()
    print("python update.py")
    print("    Check for updates and safely update.")

    print()
    print("python update.py --check")
    print("    Check for updates only.")

    print()
    print("python update.py --status")
    print("    Show Git/update status.")

    print()
    print("python update.py --no-restart")
    print("    Update without restarting main.py.")

    print()
    print("python update.py --help")
    print("    Show this help.")

    print()
    print("=" * 60)
    print("SAFETY")
    print("=" * 60)

    print()
    print("The updater will NOT automatically overwrite:")

    print("  - A newer local version")
    print("  - Uncommitted local changes")
    print("  - Diverged histories")
    print("  - Unrelated histories")

    print()
    print("No 'git reset --hard' is used.")


# ============================================================
# UPDATE LOG
# ============================================================

def log_update(success, relationship=None):

    try:

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "relationship": relationship,
            "commit": get_current_commit_short(),
            "branch": get_current_branch()
        }

        log_data = []

        if os.path.exists(UPDATE_LOG_FILE):

            try:

                with open(
                    UPDATE_LOG_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    log_data = json.load(f)

                if not isinstance(log_data, list):
                    log_data = []

            except Exception:

                log_data = []

        log_data.append(log_entry)

        # Keep only the last 20 entries.
        log_data = log_data[-20:]

        with open(
            UPDATE_LOG_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                log_data,
                f,
                indent=2
            )

    except Exception:
        pass


# ============================================================
# MAIN
# ============================================================

def main():

    check_only = "--check" in sys.argv
    status_only = "--status" in sys.argv

    show_help_msg = (
        "--help" in sys.argv
        or "-h" in sys.argv
    )

    no_restart = "--no-restart" in sys.argv

    # --------------------------------------------------------
    # Help
    # --------------------------------------------------------

    if show_help_msg:

        show_help()

        return 0

    # --------------------------------------------------------
    # Status
    # --------------------------------------------------------

    if status_only:

        return show_status()

    # --------------------------------------------------------
    # Check only
    # --------------------------------------------------------

    if check_only:

        has_updates = check_for_updates()

        return 0 if not has_updates else 1

    # --------------------------------------------------------
    # Main updater
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RPGBOT AUTO-UPDATE SYSTEM")
    print("=" * 60)

    if not is_git_repo():

        print()
        print("[ERROR] Git repository not initialized.")

        return 1

    # --------------------------------------------------------
    # Check
    # --------------------------------------------------------

    has_updates = check_for_updates()

    if not has_updates:

        print()
        print("[OK] No safe update available.")
        print()
        print("Your local bot has been left untouched.")

        return 0

    # --------------------------------------------------------
    # Ask
    # --------------------------------------------------------

    print()
    print("-" * 60)

    response = input(
        "Update now? (yes/no): "
    ).strip().lower()

    if response not in ["yes", "y"]:

        print()
        print("Update cancelled.")

        return 0

    # --------------------------------------------------------
    # Update
    # --------------------------------------------------------

    relationship = get_commit_relationship()

    if not pull_updates():

        print()
        print("[ERROR] Update failed or was blocked.")
        print()
        print("Bot was NOT restarted.")

        log_update(
            False,
            relationship
        )

        return 1

    # --------------------------------------------------------
    # Log
    # --------------------------------------------------------

    log_update(
        True,
        relationship
    )

    # --------------------------------------------------------
    # No restart
    # --------------------------------------------------------

    if no_restart:

        print()
        print("[OK] Update complete!")
        print()
        print("Bot will start on the next run.")
        print()
        print(f"Run: python {BOT_SCRIPT}")

        return 0

    # --------------------------------------------------------
    # Restart
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("UPDATE COMPLETE!")
    print("=" * 60)

    print()
    print("Starting updated bot...")

    restart_bot()

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        sys.exit(main())

    except KeyboardInterrupt:

        print()
        print("[WARNING] Update interrupted by user.")

        sys.exit(1)

    except Exception as e:

        print()
        print("[ERROR] Unexpected error:")
        print(f"        {type(e).__name__}: {e}")

        sys.exit(1)