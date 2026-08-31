#!/usr/bin/env python3
"""
RPGBot Auto-Update Script
Pulls latest changes from GitHub and restarts the bot.

Usage:
    python update.py              # Update and restart
    python update.py --check      # Check for updates without updating
    python update.py --help       # Show help
"""

import subprocess
import os
import sys
import json
from datetime import datetime


def is_git_repo():
    """Check if current directory is a git repository."""
    return os.path.exists('.git')


def get_current_branch():
    """Get the current git branch name."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_current_commit():
    """Get the current git commit SHA."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()[:7]
    except Exception:
        pass
    return None


def check_for_updates():
    """Check if there are updates available without applying them."""
    print("\n" + "="*60)
    print("CHECKING FOR UPDATES")
    print("="*60)
    
    if not is_git_repo():
        print("\n❌ Not a git repository!")
        print("This directory is not a git repository.")
        print("\nTo set up the bot with git, run:")
        print("  git clone https://github.com/CountKrampus/rpgbot.git")
        return False
    
    try:
        print("\n📡 Fetching latest changes from GitHub...")
        result = subprocess.run(
            ['git', 'fetch', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print(f"❌ Fetch failed: {result.stderr}")
            return False
        
        print("✅ Fetch successful")
        
        # Check if there are differences
        result = subprocess.run(
            ['git', 'diff', 'HEAD', 'origin/main', '--quiet'],
            capture_output=True,
            timeout=5
        )
        
        current = get_current_commit()
        print(f"\nCurrent version: {current}")
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'origin/main'],
                capture_output=True,
                text=True,
                timeout=5
            )
            latest = result.stdout.strip()[:7]
            print(f"Latest version:  {latest}")
        except Exception:
            latest = "unknown"
        
        if result.returncode == 0:
            print("\n✅ You're already up to date!")
            return False
        else:
            print("\n🎉 Update available!")
            
            # Show what changed
            try:
                result = subprocess.run(
                    ['git', 'log', '--oneline', 'HEAD..origin/main'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    print("\nNew commits:")
                    for line in result.stdout.strip().split('\n'):
                        print(f"  • {line}")
            except Exception:
                pass
            
            return True
        
    except subprocess.TimeoutExpired:
        print("❌ Git operation timed out")
        return False
    except Exception as e:
        print(f"❌ Error checking for updates: {e}")
        return False


def pull_updates():
    """Pull the latest changes from GitHub."""
    print("\n" + "="*60)
    print("UPDATING BOT")
    print("="*60)
    
    if not is_git_repo():
        print("\n❌ Not a git repository!")
        print("This directory is not a git repository.")
        print("\nTo set up the bot with git, run:")
        print("  git clone https://github.com/CountKrampus/rpgbot.git")
        return False
    
    try:
        print("\n📥 Pulling latest changes...")
        result = subprocess.run(
            ['git', 'pull', 'origin', 'main'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("✅ Update successful!")
            
            # Show what was updated
            if result.stdout:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        print(f"  {line}")
            
            return True
        else:
            print(f"\n❌ Update failed!")
            print(f"Error: {result.stderr}")
            
            # Show helpful error messages
            if "merge conflict" in result.stderr.lower():
                print("\n⚠️  Merge conflict detected!")
                print("You have local changes that conflict with the update.")
                print("To resolve:")
                print("  1. Review your local changes: git status")
                print("  2. Stash them: git stash")
                print("  3. Try updating again: python update.py")
            
            return False
        
    except subprocess.TimeoutExpired:
        print("❌ Update timed out (taking too long)")
        return False
    except Exception as e:
        print(f"❌ Error during update: {e}")
        return False


def restart_bot():
    """Restart the bot after update."""
    print("\n" + "="*60)
    print("RESTARTING BOT")
    print("="*60)
    print("\nStarting bot...")
    
    try:
        subprocess.run(['python', 'main.py'], check=False)
    except KeyboardInterrupt:
        print("\n\n⚠️  Bot interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        sys.exit(1)


def show_help():
    """Show help message."""
    print(__doc__)
    print("\nOptions:")
    print("  --check       Check for updates without updating")
    print("  --help        Show this help message")
    print("  --no-restart  Update but don't restart the bot")
    print("\nExamples:")
    print("  python update.py              # Check, update, and restart")
    print("  python update.py --check      # Just check for updates")
    print("  python update.py --no-restart # Update without restarting")


def log_update(success):
    """Log update attempt to .update_log file."""
    try:
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "commit": get_current_commit(),
            "branch": get_current_branch()
        }
        
        # Read existing log
        log_file = '.update_log'
        log_data = []
        if os.path.exists(log_file):
            try:
                with open(log_file, 'r') as f:
                    log_data = json.load(f)
            except Exception:
                log_data = []
        
        # Add new entry
        log_data.append(log_entry)
        
        # Keep only last 20 entries
        log_data = log_data[-20:]
        
        # Write log
        with open(log_file, 'w') as f:
            json.dump(log_data, f, indent=2)
    except Exception:
        pass  # Silently fail if we can't write log


def main():
    """Main update flow."""
    # Parse arguments
    check_only = '--check' in sys.argv
    show_help_msg = '--help' in sys.argv or '-h' in sys.argv
    no_restart = '--no-restart' in sys.argv
    
    if show_help_msg:
        show_help()
        return 0
    
    # Check for updates
    if check_only:
        has_updates = check_for_updates()
        return 0 if not has_updates else 1
    
    # Normal update flow
    print("\n" + "="*60)
    print("RPGBOT AUTO-UPDATE SYSTEM")
    print("="*60)
    
    # Check if it's a git repo
    if not is_git_repo():
        print("\n❌ Not a git repository!")
        print("\nThis update script requires git. To set up the bot with git:")
        print("\n  1. Backup your settings.json file")
        print("  2. Run: git clone https://github.com/CountKrampus/rpgbot.git")
        print("  3. Copy your settings.json back")
        print("  4. Then you can use: python update.py")
        return 1
    
    # Check for updates
    if not check_for_updates():
        print("\n✅ All done! Your bot is up to date.")
        return 0
    
    # Ask for confirmation
    print("\n" + "-"*60)
    response = input("Update now? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n⏭️  Update cancelled.")
        return 0
    
    # Pull updates
    if not pull_updates():
        print("\n❌ Update failed. Bot not restarted.")
        log_update(False)
        return 1
    
    log_update(True)
    
    # Restart bot
    if no_restart:
        print("\n✅ Update complete! Bot will start on next run.")
        print("Run: python main.py")
        return 0
    
    print("\n" + "="*60)
    print("Update complete! Starting bot...")
    print("="*60)
    
    restart_bot()
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Update interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
