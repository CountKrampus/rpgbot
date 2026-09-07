"""
Wire NotificationSystem into the mining loop
Same pattern as training_notifications_integration.py
"""

from notifications import NotificationSystem
from discord_settings import DiscordSettingsManager


class MiningNotifier:
    """Manages notifications during mining with proper lifecycle"""
    
    def __init__(self, account_name):
        self.account_name = account_name
        self.notifier = None
        self.config = None
        self.mines_since_last_notification = 0
        self.progress_interval = 500000  # Default: every 500k mines
        
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
    
    def on_mine_complete(self, mines_completed, ore_collected, mines_per_hour):
        """Called after each mine completes"""
        if not self.is_enabled():
            return
        
        self.mines_since_last_notification += 1
        
        if self.config.get('send_progress', True):
            if self.mines_since_last_notification >= self.progress_interval:
                try:
                    self.notifier.send_webhook(
                        "⛏️  Mining Progress",
                        f"Account: {self.account_name}\nMines: {mines_completed:,}\nOre Collected: {ore_collected:,}\nSpeed: {mines_per_hour:,.0f} mines/hour",
                        "8b4513"  # Brown (ore color)
                    )
                    self.mines_since_last_notification = 0
                except Exception as e:
                    print(f"  ⚠️  Failed to send progress notification: {e}")
    
    def on_mining_complete(self, mines_completed, ore_collected, duration_str):
        """Called when mining finishes normally"""
        if not self.is_enabled():
            return
        
        if self.config.get('send_completion', True):
            try:
                self.notifier.send_webhook(
                    "✅ Mining Complete",
                    f"Account: {self.account_name}\nTotal Mines: {mines_completed:,}\nOre Collected: {ore_collected:,}\nDuration: {duration_str}",
                    "00ff00"  # Green
                )
            except Exception as e:
                print(f"  ⚠️  Failed to send completion notification: {e}")
    
    def on_mining_error(self, error_message):
        """Called when an error occurs during mining"""
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
    
    def on_mining_cancelled(self, mines_completed, ore_collected):
        """Called when mining is cancelled by user"""
        if not self.is_enabled():
            return
        
        try:
            self.notifier.send_webhook(
                "⏹️  Mining Cancelled",
                f"Account: {self.account_name}\nMines: {mines_completed:,}\nOre Collected: {ore_collected:,}",
                "ff6600"  # Orange
            )
        except Exception as e:
            print(f"  ⚠️  Failed to send cancellation notification: {e}")
