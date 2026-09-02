#!/usr/bin/env python3
"""
RPGBot Auto-Update Script
Pulls latest changes from GitHub and restarts the bot.

Usage:
    python update.py              # Check, update, and restart
    python update.py --check      # Check for updates without updating
    python update.py --no-restart # Update without restarting
    python update.py --help       # Show help
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
# GIT HELPERS
# ============================================================

def run_git(args, timeout=30):
    """
    Run a git command and return the completed process.

    args should NOT include the word 'git'.
    """

    return subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        timeout=timeout
    )


def is_git_repo():
    """Check if the current directory is a git repository."""

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
    """Get the current git branch name."""

    try:
        result = run_git(
            [
                "rev-parse",
                "--abbrev-ref",
                "HEAD"
            ],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()

    except Exception:
        pass

    return None


def get_current_commit():
    """Get the current local commit SHA."""

    try:
        result = run_git(
            ["rev-parse", "HEAD"],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()[:7]

    except Exception:
        pass

    return None


def get_latest_commit():
    """Get the latest commit SHA from origin/main."""

    try:
        result = run_git(
            [
                "rev-parse",
                f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
            ],
            timeout=5
        )

        if result.returncode == 0:
            return result.stdout.strip()[:7]

    except Exception:
        pass

    return None


def has_local_changes():
    """
    Check whether the working directory contains
    uncommitted changes.
    """

    try:
        result = run_git(
            [
                "status",
                "--porcelain"
            ],
            timeout=10
        )

        if result.returncode != 0:
            return False

        return bool(result.stdout.strip())

    except Exception:
        return False


def get_local_changes():
    """Return a list of local uncommitted changes."""

    try:
        result = run_git(
            [
                "status",
                "--short"
            ],
            timeout=10
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
    Check whether origin/main contains commits that
    are not currently installed locally.

    Returns:

        True  = update available
        False = no update / check failed
    """

    print()
    print("=" * 60)
    print("CHECKING FOR UPDATES")
    print("=" * 60)

    # --------------------------------------------------------
    # Verify git repository.
    # --------------------------------------------------------

    if not is_git_repo():

        print()
        print("❌ Not a git repository!")

        print(
            "This directory is not a git repository."
        )

        print()
        print("To set up the bot with git:")

        print(
            "  git clone "
            "https://github.com/CountKrampus/rpgbot.git"
        )

        return False

    # --------------------------------------------------------
    # Fetch GitHub.
    # --------------------------------------------------------

    try:

        print()
        print(
            "📡 Fetching latest version from GitHub..."
        )

        fetch_result = run_git(
            [
                "fetch",
                GITHUB_REMOTE,
                GITHUB_BRANCH
            ],
            timeout=30
        )

        if fetch_result.returncode != 0:

            print()
            print("❌ Check failed")

            error = (
                fetch_result.stderr.strip()
                or fetch_result.stdout.strip()
                or "Unknown Git error."
            )

            print()
            print(f"Error: {error}")

            return False

        print("✅ GitHub connection successful")

        # ----------------------------------------------------
        # Get versions.
        # ----------------------------------------------------

        current = get_current_commit()
        latest = get_latest_commit()

        if current is None:

            print()
            print(
                "❌ Could not determine "
                "current local version."
            )

            return False

        if latest is None:

            print()
            print(
                "❌ Could not determine "
                "latest GitHub version."
            )

            return False

        print()
        print(
            f"Current version: {current}"
        )

        print(
            f"Latest version:  {latest}"
        )

        # ----------------------------------------------------
        # Determine whether local HEAD differs from
        # origin/main.
        #
        # IMPORTANT:
        #
        # Do NOT reuse the result from rev-parse.
        # git diff --quiet returns:
        #
        #   0 = identical
        #   1 = different
        # ----------------------------------------------------

        diff_result = run_git(
            [
                "diff",
                "--quiet",
                "HEAD",
                f"{GITHUB_REMOTE}/{GITHUB_BRANCH}"
            ],
            timeout=10
        )

        # ----------------------------------------------------
        # No differences.
        # ----------------------------------------------------

        if diff_result.returncode == 0:

            print()
            print(
                "✅ You're already up to date!"
            )

            return False

        # ----------------------------------------------------
        # Differences detected.
        # ----------------------------------------------------

        if diff_result.returncode == 1:

            print()
            print(
                "🎉 Update available!"
            )

            # ------------------------------------------------
            # Show incoming commits.
            # ------------------------------------------------

            log_result = run_git(
                [
                    "log",
                    "--oneline",
                    f"HEAD..{GITHUB_REMOTE}/{GITHUB_BRANCH}"
                ],
                timeout=10
            )

            if (
                log_result.returncode == 0
                and log_result.stdout.strip()
            ):

                print()
                print("New commits:")

                for line in (
                    log_result.stdout
                    .strip()
                    .splitlines()
                ):

                    print(
                        f"  • {line}"
                    )

            # ------------------------------------------------
            # Show whether local files have been modified.
            # ------------------------------------------------

            if has_local_changes():

                print()
                print(
                    "⚠️  Local changes detected."
                )

                print()
                print(
                    "Your working directory contains "
                    "uncommitted changes."
                )

                changes = get_local_changes()

                if changes:

                    print()
                    print("Local changes:")

                    for line in changes.splitlines():

                        print(
                            f"  {line}"
                        )

                print()
                print(
                    "The updater will NOT automatically "
                    "overwrite these changes."
                )

            return True

        # ----------------------------------------------------
        # Git itself returned an unexpected result.
        # ----------------------------------------------------

        print()
        print("❌ Check failed")

        error = (
            diff_result.stderr.strip()
            or diff_result.stdout.strip()
            or "Git returned an unexpected status."
        )

        print()
        print(
            f"Error: {error}"
        )

        return False

    except subprocess.TimeoutExpired:

        print()
        print(
            "❌ Git operation timed out."
        )

        print(
            "Check your internet connection "
            "or GitHub availability."
        )

        return False

    except Exception as e:

        print()
        print(
            "❌ Error checking for updates:"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

        return False


# ============================================================
# PULL UPDATES
# ============================================================

def pull_updates():
    """Pull the latest changes from GitHub."""

    print()
    print("=" * 60)
    print("UPDATING BOT")
    print("=" * 60)

    if not is_git_repo():

        print()
        print("❌ Not a git repository!")

        return False

    # --------------------------------------------------------
    # Protect local changes.
    # --------------------------------------------------------

    if has_local_changes():

        print()
        print(
            "⚠️  Local changes detected."
        )

        print()
        print(
            "The updater will not overwrite "
            "uncommitted local changes."
        )

        changes = get_local_changes()

        if changes:

            print()
            print("Changes found:")

            for line in changes.splitlines():

                print(
                    f"  {line}"
                )

        print()
        print(
            "Please commit or stash your changes "
            "before updating."
        )

        return False

    # --------------------------------------------------------
    # Pull.
    # --------------------------------------------------------

    try:

        print()
        print(
            "📥 Pulling latest changes..."
        )

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
            print(
                "✅ Update successful!"
            )

            if result.stdout.strip():

                print()

                for line in (
                    result.stdout
                    .strip()
                    .splitlines()
                ):

                    if line.strip():

                        print(
                            f"  {line}"
                        )

            return True

        # ----------------------------------------------------
        # Pull failed.
        # ----------------------------------------------------

        print()
        print(
            "❌ Update failed!"
        )

        error = (
            result.stderr.strip()
            or result.stdout.strip()
            or "Unknown Git error."
        )

        print()
        print(
            f"Error: {error}"
        )

        # ----------------------------------------------------
        # Helpful diagnostics.
        # ----------------------------------------------------

        lower_error = error.lower()

        if (
            "non-fast-forward" in lower_error
            or "divergent" in lower_error
            or "not possible to fast-forward" in lower_error
        ):

            print()
            print(
                "⚠️  Your local branch has diverged "
                "from GitHub."
            )

            print()
            print(
                "Your local branch contains commits "
                "that GitHub does not have."
            )

            print()
            print(
                "The updater will not overwrite them."
            )

            print()
            print(
                "If you intentionally want to discard "
                "local commits, handle that manually "
                "before running the updater again."
            )

        elif (
            "conflict" in lower_error
            or "merge" in lower_error
        ):

            print()
            print(
                "⚠️  Git reported a merge/conflict problem."
            )

            print()
            print(
                "Review your repository with:"
            )

            print(
                "  git status"
            )

        return False

    except subprocess.TimeoutExpired:

        print()
        print(
            "❌ Update timed out."
        )

        return False

    except Exception as e:

        print()
        print(
            "❌ Error during update:"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

        return False


# ============================================================
# RESTART BOT
# ============================================================

def restart_bot():
    """Restart the bot after a successful update."""

    print()
    print("=" * 60)
    print("RESTARTING BOT")
    print("=" * 60)

    print()
    print(
        "Starting bot..."
    )

    try:

        subprocess.run(
            [
                sys.executable,
                BOT_SCRIPT
            ],
            check=False
        )

    except KeyboardInterrupt:

        print()
        print(
            "⚠️  Bot interrupted by user."
        )

        sys.exit(0)

    except Exception as e:

        print()
        print(
            "❌ Error starting bot:"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

        sys.exit(1)


# ============================================================
# HELP
# ============================================================

def show_help():
    """Show help information."""

    print(__doc__)

    print()
    print("Options:")

    print(
        "  --check"
        "       Check for updates without updating"
    )

    print(
        "  --help"
        "        Show this help message"
    )

    print(
        "  --no-restart"
        " Update but don't restart the bot"
    )

    print()
    print("Examples:")

    print(
        "  python update.py"
    )

    print(
        "  python update.py --check"
    )

    print(
        "  python update.py --no-restart"
    )


# ============================================================
# UPDATE LOG
# ============================================================

def log_update(success):
    """Log update attempt to .update_log."""

    try:

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "commit": get_current_commit(),
            "branch": get_current_branch()
        }

        log_data = []

        if os.path.exists(
            UPDATE_LOG_FILE
        ):

            try:

                with open(
                    UPDATE_LOG_FILE,
                    "r",
                    encoding="utf-8"
                ) as f:

                    log_data = json.load(f)

                if not isinstance(
                    log_data,
                    list
                ):

                    log_data = []

            except Exception:

                log_data = []

        log_data.append(
            log_entry
        )

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

        # Updating should never fail just because
        # the update log cannot be written.

        pass


# ============================================================
# MAIN
# ============================================================

def main():
    """Main update flow."""

    # --------------------------------------------------------
    # Parse command-line arguments.
    # --------------------------------------------------------

    check_only = (
        "--check"
        in sys.argv
    )

    show_help_msg = (
        "--help"
        in sys.argv
        or "-h"
        in sys.argv
    )

    no_restart = (
        "--no-restart"
        in sys.argv
    )

    # --------------------------------------------------------
    # Help.
    # --------------------------------------------------------

    if show_help_msg:

        show_help()

        return 0

    # --------------------------------------------------------
    # Check-only mode.
    # --------------------------------------------------------

    if check_only:

        has_updates = (
            check_for_updates()
        )

        return (
            0
            if not has_updates
            else 1
        )

    # --------------------------------------------------------
    # Normal update mode.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("RPGBOT AUTO-UPDATE SYSTEM")
    print("=" * 60)

    # --------------------------------------------------------
    # Verify repository.
    # --------------------------------------------------------

    if not is_git_repo():

        print()
        print(
            "❌ Not a git repository!"
        )

        print()
        print(
            "This update script requires Git."
        )

        print()
        print(
            "To set up the bot:"
        )

        print()
        print(
            "  1. Backup your settings.json"
        )

        print(
            "  2. Run:"
        )

        print(
            "     git clone "
            "https://github.com/CountKrampus/rpgbot.git"
        )

        print()
        print(
            "  3. Copy your settings.json back"
        )

        print(
            "  4. Run:"
        )

        print(
            "     python update.py"
        )

        return 1

    # --------------------------------------------------------
    # Check for updates.
    # --------------------------------------------------------

    if not check_for_updates():

        print()
        print(
            "✅ All done! "
            "Your bot is up to date."
        )

        return 0

    # --------------------------------------------------------
    # Confirm update.
    # --------------------------------------------------------

    print()
    print("-" * 60)

    response = input(
        "Update now? (yes/no): "
    ).strip().lower()

    if response not in [
        "yes",
        "y"
    ]:

        print()
        print(
            "⏭️  Update cancelled."
        )

        return 0

    # --------------------------------------------------------
    # Pull updates.
    # --------------------------------------------------------

    if not pull_updates():

        print()
        print(
            "❌ Update failed."
        )

        print(
            "Bot not restarted."
        )

        log_update(False)

        return 1

    # --------------------------------------------------------
    # Log successful update.
    # --------------------------------------------------------

    log_update(True)

    # --------------------------------------------------------
    # Don't restart if requested.
    # --------------------------------------------------------

    if no_restart:

        print()
        print(
            "✅ Update complete!"
        )

        print(
            "Bot will start on next run."
        )

        print()
        print(
            f"Run: python {BOT_SCRIPT}"
        )

        return 0

    # --------------------------------------------------------
    # Restart.
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print(
        "UPDATE COMPLETE!"
    )
    print("=" * 60)

    print()
    print(
        "Starting updated bot..."
    )

    restart_bot()

    return 0


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    try:

        sys.exit(
            main()
        )

    except KeyboardInterrupt:

        print()
        print(
            "⚠️  Update interrupted by user."
        )

        sys.exit(1)

    except Exception as e:

        print()
        print(
            "❌ Unexpected error:"
        )

        print(
            f"   {type(e).__name__}: {e}"
        )

        sys.exit(1)