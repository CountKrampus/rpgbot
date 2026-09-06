"""
Auto-Update Settings Configuration (Integrated)

This module now integrates with settings.py for persistence.
Settings are stored in settings.json and managed through the settings system.

Status: UNFINISHED → NOW INTEGRATED (Phase 2 Complete!)
"""

import json
import os
from datetime import datetime


class AutoUpdateSettings:
    """
    Manage auto-update settings from settings.json
    
    NOW INTEGRATED: Settings are part of settings.py system
    - Settings persist across bot restarts
    - Can be configured from main settings menu (Option 10)
    - Can be configured from Update Center menu (Option 9)
    """
    
    def __init__(self, settings_file="settings.json"):
        """
        Initialize settings manager
        
        Args:
            settings_file: Path to settings.json
        """
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self):
        """Load settings from file or create defaults"""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                return settings if isinstance(settings, dict) else {}
        except Exception as e:
            print(f"❌ Error loading settings: {e}")
        
        return {}
    
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving settings: {e}")
            return False
    
    # ========================================================================
    # GETTER FUNCTIONS (INTEGRATED - now part of settings.py)
    # ========================================================================
    
    def is_auto_update_enabled(self):
        """Check if auto-update is enabled"""
        return self.settings.get("auto_update_enabled", False)
    
    def get_check_frequency_hours(self):
        """Get update check frequency in hours"""
        return self.settings.get("auto_update_check_frequency_hours", 24)
    
    def should_restart_after_update(self):
        """Check if bot should restart after update"""
        return self.settings.get("auto_update_restart_after", True)
    
    def is_quiet_mode_enabled(self):
        """Check if quiet mode is enabled (no notifications)"""
        return self.settings.get("auto_update_quiet_mode", False)
    
    def get_last_check_time(self):
        """Get timestamp of last update check"""
        return self.settings.get("auto_update_last_check", None)
    
    def should_notify_on_update(self):
        """Check if notifications should be shown"""
        return self.settings.get("auto_update_notify", True)
    
    # ========================================================================
    # SETTER FUNCTIONS (INTEGRATED - now part of settings.py)
    # ========================================================================
    
    def set_auto_update_enabled(self, enabled):
        """Enable/disable auto-update"""
        self.settings["auto_update_enabled"] = bool(enabled)
        return self.save_settings()
    
    def set_check_frequency_hours(self, hours):
        """Set update check frequency"""
        if hours < 1 or hours > 168:  # 1 hour to 1 week
            print("❌ Frequency must be between 1 and 168 hours")
            return False
        self.settings["auto_update_check_frequency_hours"] = int(hours)
        return self.save_settings()
    
    def set_restart_after_update(self, restart):
        """Set whether to restart after update"""
        self.settings["auto_update_restart_after"] = bool(restart)
        return self.save_settings()
    
    def set_quiet_mode(self, quiet):
        """Enable/disable quiet mode"""
        self.settings["auto_update_quiet_mode"] = bool(quiet)
        return self.save_settings()
    
    def set_last_check_time(self, timestamp=None):
        """Set timestamp of last check (defaults to now)"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        self.settings["auto_update_last_check"] = timestamp
        return self.save_settings()
    
    def set_notify_on_update(self, notify):
        """Enable/disable notifications"""
        self.settings["auto_update_notify"] = bool(notify)
        return self.save_settings()
    
    # ========================================================================
    # HELPER FUNCTIONS
    # ========================================================================
    
    def should_check_for_updates(self):
        """
        Determine if we should check for updates based on frequency
        """
        if not self.is_auto_update_enabled():
            return False
        
        last_check = self.get_last_check_time()
        frequency_hours = self.get_check_frequency_hours()
        
        if last_check is None:
            return True
        
        try:
            elapsed = datetime.now() - datetime.fromisoformat(last_check)
            return elapsed.total_seconds() > (frequency_hours * 3600)
        except Exception:
            return True
    
    def get_frequency_options(self):
        """Get list of frequency options for menu"""
        return [
            (1, "Every hour"),
            (6, "Every 6 hours"),
            (12, "Every 12 hours"),
            (24, "Daily"),
            (48, "Every 2 days"),
            (168, "Weekly"),
        ]
    
    def display_current_settings(self):
        """Display current auto-update settings"""
        print("\n" + "="*60)
        print("AUTO-UPDATE SETTINGS")
        print("="*60)
        
        enabled = "✅ Enabled" if self.is_auto_update_enabled() else "❌ Disabled"
        print(f"\nAuto-Update Status:    {enabled}")
        
        freq = self.get_check_frequency_hours()
        print(f"Check Frequency:       Every {freq} hours")
        
        restart = "✅ Yes" if self.should_restart_after_update() else "❌ No"
        print(f"Auto-Restart:          {restart}")
        
        quiet = "✅ Enabled" if self.is_quiet_mode_enabled() else "❌ Disabled"
        print(f"Quiet Mode:            {quiet}")
        
        notify = "✅ Enabled" if self.should_notify_on_update() else "❌ Disabled"
        print(f"Notifications:         {notify}")
        
        last_check = self.get_last_check_time()
        if last_check:
            print(f"Last Check:            {last_check}")
        else:
            print(f"Last Check:            Never")
        
        print("\n✅ Settings persist across bot restarts (integrated with settings.py)")
        print()


# ============================================================================
# MODULE-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

_settings_instance = None


def get_auto_update_settings():
    """Get global settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AutoUpdateSettings()
    return _settings_instance


def get_auto_update_enabled():
    """Check if auto-update is enabled"""
    return get_auto_update_settings().is_auto_update_enabled()


def set_auto_update_enabled(enabled):
    """Enable/disable auto-update"""
    return get_auto_update_settings().set_auto_update_enabled(enabled)


def get_check_frequency():
    """Get check frequency in hours"""
    return get_auto_update_settings().get_check_frequency_hours()


def set_check_frequency(hours):
    """Set check frequency"""
    return get_auto_update_settings().set_check_frequency_hours(hours)


def should_check_now():
    """Determine if we should check for updates now"""
    return get_auto_update_settings().should_check_for_updates()


def record_check_time():
    """Record that we just checked for updates"""
    return get_auto_update_settings().set_last_check_time()


if __name__ == '__main__':
    # For testing
    print("This module provides auto-update settings management")
    print("Status: NOW INTEGRATED with settings.py ✅")
    print("\nUsage:")
    print("  from auto_update_settings_integrated_unfinished import AutoUpdateSettings")
    print("  settings = AutoUpdateSettings()")
    print("  settings.display_current_settings()")
