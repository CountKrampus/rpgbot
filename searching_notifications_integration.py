"""
Wire NotificationSystem into the searching loop
Same pattern as training_notifications_integration.py
"""

from notifications import NotificationSystem
from discord_settings import DiscordSettingsManager


class SearchingNotifier:
    """Manages notifications during searching with proper lifecycle"""
    
    def __init__(self, account_name):
        self.account_name = account_name
        self.notifier = None
        self.config = None
        self.searches_since_last_notification = 0
        self.progress_interval = 500000  # Default: every 500k searches
        
        self._initialize()
    
    def _initialize(self):
        """Initialize notification system from settings"""
        try:
            settings = DiscordSettingsManager()
            self.config = settings.config
            
            if not self.config.get('enabled', False):
                return
            
            webhook_url = self.config.get('webhook_url', '')
            if not webhook_url:
                return
            
            self.notifier = NotificationSystem()
            self.notifier.enable_webhook(webhook_url)
            self.progress_interval = self.config.get('progress_interval', 500000)
            
        except Exception as e:
            print(f"  ⚠️  Discord notification setup failed: {e}")
            self.notifier = None
    
    def is_enabled(self):
        """Check if notifications are enabled"""
        return self.notifier is not None
    
    def on_search_complete(self, searches_completed, items_found, items_per_hour):
        """Called after each search completes"""
        if not self.is_enabled():
            return
        
        self.searches_since_last_notification += 1
        
        if self.config.get('send_progress', True):
            if self.searches_since_last_notification >= self.progress_interval:
                try:
                    self.notifier.send_webhook(
                        "🔍 Searching Progress",
                        f"Account: {self.account_name}\nSearches: {searches_completed:,}\nItems Found: {items_found:,}\nSpeed: {items_per_hour:,.0f} searches/hour",
                        "0099ff"  # Blue
                    )
                    self.searches_since_last_notification = 0
                except Exception as e:
                    print(f"  ⚠️  Failed to send progress notification: {e}")
    
    def on_searching_complete(self, searches_completed, items_found, duration_str):
        """Called when searching finishes normally"""
        if not self.is_enabled():
            return
        
        if self.config.get('send_completion', True):
            try:
                self.notifier.send_webhook(
                    "✅ Searching Complete",
                    f"Account: {self.account_name}\nTotal Searches: {searches_completed:,}\nItems Found: {items_found:,}\nDuration: {duration_str}",
                    "00ff00"  # Green
                )
            except Exception as e:
                print(f"  ⚠️  Failed to send completion notification: {e}")
    
    def on_searching_error(self, error_message):
        """Called when an error occurs during searching"""
        if not self.is_enabled():
            return
        
        if self.config.get('send_errors', True):
            try:
                self.notifier.send_error_alert(
                    self.account_name,
                    error_message
                )
            except Exception as e:
                print(f"  ⚠️  Failed to send error notification: {e}")
    
    def on_searching_cancelled(self, searches_completed, items_found):
        """Called when searching is cancelled by user"""
        if not self.is_enabled():
            return
        
        try:
            self.notifier.send_webhook(
                "⏹️  Searching Cancelled",
                f"Account: {self.account_name}\nSearches: {searches_completed:,}\nItems Found: {items_found:,}",
                "ff6600"  # Orange
            )
        except Exception as e:
            print(f"  ⚠️  Failed to send cancellation notification: {e}")
