"""
RPGBot Update Menu (Unfinished)
In-game menu for checking and performing updates.

This menu allows users to:
1. Check for updates from within the bot
2. View changelog/what's new
3. Configure auto-update settings
4. Perform updates without closing the bot
5. View update history

Status: UNFINISHED - In development
"""

import threading
import subprocess
import json
import os
from datetime import datetime

try:
    from auto_update_settings_unfinished import AutoUpdateSettings
except ImportError:
    AutoUpdateSettings = None


def update_menu(driver):
    """
    Main update menu - called from main_menu.py
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        None (returns to main menu when done)
    """
    
    while True:
        print("\n" + "="*60)
        print("UPDATE CENTER")
        print("="*60)
        
        # Show current version
        current_version = get_current_version()
        print(f"\nCurrent Version: {current_version}")
        
        print("\n1. Check for Updates")
        print("2. View Changelog")
        print("3. Auto-Update Settings")
        print("4. Update Now")
        print("5. View Update History")
        print("6. Back to Main Menu")
        
        choice = input("\nChoose option: ").strip()
        
        if choice == "1":
            check_for_updates_menu()
        elif choice == "2":
            view_changelog_menu()
        elif choice == "3":
            configure_auto_update_menu()
        elif choice == "4":
            update_now_menu()
        elif choice == "5":
            view_update_history_menu()
        elif choice == "6":
            return
        else:
            print("❌ Invalid choice")


def check_for_updates_menu():
    """Check for updates and show results"""
    
    print("\n" + "="*60)
    print("CHECKING FOR UPDATES")
    print("="*60)
    
    print("\n📡 Fetching latest version from GitHub...")
    
    try:
        # Call update.py to check
        result = subprocess.run(
            ['python', 'update.py', '--check'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            print("\n✅ Check complete!")
            
            # Parse output to show meaningful info
            if "already up to date" in result.stdout.lower():
                print("\n✅ You're already running the latest version!")
                current = get_current_version()
                print(f"Current: {current}")
            else:
                print("\n🎉 Update available!")
                # Show changelog
                show_update_details()
        else:
            print(f"\n❌ Check failed")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
                
    except subprocess.TimeoutExpired:
        print("\n⏱️  Check timed out (took too long)")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")


def view_changelog_menu():
    """View changelog/what's new"""
    
    print("\n" + "="*60)
    print("CHANGELOG")
    print("="*60)
    
    try:
        # Get latest commits from git
        result = subprocess.run(
            ['git', 'log', '--oneline', '-10'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print("\nRecent Updates:")
            print("-" * 60)
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    print(f"  {line}")
        else:
            print("\n❌ Could not fetch changelog")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")


def configure_auto_update_menu():
    """Configure auto-update settings"""
    
    if AutoUpdateSettings is None:
        print("\n❌ Settings module not available")
        input("\nPress Enter to continue...")
        return
    
    settings = AutoUpdateSettings()
    
    while True:
        print("\n" + "="*60)
        print("AUTO-UPDATE SETTINGS")
        print("="*60)
        
        # Display current settings
        settings.display_current_settings()
        
        print("\n1. Toggle Auto-Update")
        print("2. Set Check Frequency")
        print("3. Toggle Auto-Restart After Update")
        print("4. Toggle Quiet Mode")
        print("5. Toggle Notifications")
        print("6. Back to Update Menu")
        
        choice = input("\nChoose option: ").strip()
        
        if choice == "1":
            current = settings.is_auto_update_enabled()
            new_value = not current
            if settings.set_auto_update_enabled(new_value):
                status = "✅ Enabled" if new_value else "❌ Disabled"
                print(f"\n✅ Auto-Update {status}")
            else:
                print("\n❌ Failed to save setting")
        
        elif choice == "2":
            print("\nAvailable frequencies:")
            options = settings.get_frequency_options()
            for i, (hours, label) in enumerate(options, 1):
                print(f"  {i}. {label} ({hours}h)")
            
            freq_choice = input("\nSelect frequency: ").strip()
            try:
                freq_idx = int(freq_choice) - 1
                if 0 <= freq_idx < len(options):
                    hours, label = options[freq_idx]
                    if settings.set_check_frequency_hours(hours):
                        print(f"\n✅ Frequency set to {label}")
                    else:
                        print("\n❌ Failed to save setting")
                else:
                    print("\n❌ Invalid choice")
            except ValueError:
                print("\n❌ Please enter a number")
        
        elif choice == "3":
            current = settings.should_restart_after_update()
            new_value = not current
            if settings.set_restart_after_update(new_value):
                status = "✅ Enabled" if new_value else "❌ Disabled"
                print(f"\n✅ Auto-Restart {status}")
            else:
                print("\n❌ Failed to save setting")
        
        elif choice == "4":
            current = settings.is_quiet_mode_enabled()
            new_value = not current
            if settings.set_quiet_mode(new_value):
                status = "✅ Enabled" if new_value else "❌ Disabled"
                print(f"\n✅ Quiet Mode {status}")
            else:
                print("\n❌ Failed to save setting")
        
        elif choice == "5":
            current = settings.should_notify_on_update()
            new_value = not current
            if settings.set_notify_on_update(new_value):
                status = "✅ Enabled" if new_value else "❌ Disabled"
                print(f"\n✅ Notifications {status}")
            else:
                print("\n❌ Failed to save setting")
        
        elif choice == "6":
            return
        
        else:
            print("\n❌ Invalid choice")
        
        input("\nPress Enter to continue...")


def update_now_menu():
    """Perform update immediately"""
    
    print("\n" + "="*60)
    print("UPDATE NOW")
    print("="*60)
    
    print("\n⚠️  This will:")
    print("  • Stop the current session")
    print("  • Pull latest changes from GitHub")
    print("  • Restart the bot")
    
    response = input("\nContinue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("❌ Update cancelled")
        return
    
    print("\n📥 Starting update...")
    
    try:
        # Run update.py --no-restart
        result = subprocess.run(
            ['python', 'update.py', '--no-restart'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("\n✅ Update successful!")
            print("Bot will restart on next session")
        else:
            print("\n❌ Update failed")
            if result.stderr:
                print(f"Error: {result.stderr[:200]}")
                
    except subprocess.TimeoutExpired:
        print("\n⏱️  Update timed out")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    input("\nPress Enter to continue...")


def view_update_history_menu():
    """View update history from .update_log"""
    
    print("\n" + "="*60)
    print("UPDATE HISTORY")
    print("="*60)
    
    try:
        if os.path.exists('.update_log'):
            with open('.update_log', 'r') as f:
                log_data = json.load(f)
            
            if log_data:
                print("\nRecent Updates:")
                print("-" * 60)
                
                # Show last 10 updates
                for entry in log_data[-10:]:
                    timestamp = entry.get('timestamp', 'unknown')
                    success = "✅" if entry.get('success') else "❌"
                    commit = entry.get('commit', 'unknown')
                    
                    print(f"{success} {timestamp} - {commit}")
            else:
                print("\n📝 No updates recorded yet")
        else:
            print("\n📝 No update history available")
            print("(Will be created after first update)")
            
    except Exception as e:
        print(f"\n❌ Error reading history: {e}")
    
    input("\nPress Enter to continue...")


def get_current_version():
    """Get current git commit SHA"""
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
    return "unknown"


def show_update_details():
    """Show details about available update"""
    
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', 'HEAD..origin/main'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            print("\nNew commits:")
            for line in result.stdout.strip().split('\n')[:5]:
                print(f"  • {line}")
    except Exception:
        pass


# TODO: UNFINISHED FEATURES

# 1. Integration with settings.py
#    - Add auto-update settings to settings.json
#    - Implement get/set functions for auto-update preferences
#
# 2. Background checking
#    - Thread-safe update checking without blocking bot
#    - Notification when updates available
#
# 3. Scheduled updates
#    - Check on startup
#    - Check periodically during automation
#    - Notify user without interrupting
#
# 4. Safe update during automation
#    - Check if automation is running
#    - Queue update for after session
#    - Or restart after current session
#
# 5. Error recovery
#    - Better error messages
#    - Rollback on failed updates
#    - Recovery instructions
#
# 6. Progress indication
#    - Show download progress
#    - Show update status
#    - Estimated time remaining
#
# 7. Update preview
#    - Show all files that will change
#    - Show file sizes
#    - Show update size
#
# 8. Notifications
#    - Desktop notification for updates
#    - In-game notification
#    - Sound notification


if __name__ == '__main__':
    # For testing
    print("This module is meant to be imported from main_menu.py")
    print("Usage: from menus.update_menu import update_menu")
    print("Then call: update_menu(driver)")
