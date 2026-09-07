"""
Wire NotificationSystem into the training loop

This module handles sending notifications at appropriate points:
- Progress updates every N battles
- Completion notification when training ends
- Error notifications on failures
"""

from notifications import NotificationSystem
from discord_settings import DiscordSettingsManager


class TrainingNotifier:
    """Manages notifications during training with proper lifecycle"""
    
    def __init__(self, account_name):
        self.account_name = account_name
        self.notifier = None
        self.config = None
        self.battles_since_last_notification = 0
        self.progress_interval = 500000  # Default
        
        self._initialize()
    
    def _initialize(self):
        """Initialize notification system from settings"""
        try:
            settings = DiscordSettingsManager()
            self.config = settings.config
            
            # Only proceed if notifications are enabled
            if not self.config.get('enabled', False):
                return
            
            # Only proceed if webhook URL is set
            webhook_url = self.config.get('webhook_url', '')
            if not webhook_url:
                return
            
            # Initialize NotificationSystem
            self.notifier = NotificationSystem()
            self.notifier.enable_webhook(webhook_url)
            
            # Get progress interval from settings
            self.progress_interval = self.config.get('progress_interval', 500000)
            
        except Exception as e:
            print(f"  ⚠️  Discord notification setup failed: {e}")
            self.notifier = None
    
    def is_enabled(self):
        """Check if notifications are enabled"""
        return self.notifier is not None
    
    def on_battle_complete(self, battles_completed, total_exp, battles_per_hour):
        """Called after each battle completes"""
        if not self.is_enabled():
            return
        
        self.battles_since_last_notification += 1
        
        # Send progress update at intervals
        if self.config.get('send_progress', True):
            if self.battles_since_last_notification >= self.progress_interval:
                try:
                    self.notifier.send_progress_update(
                        self.account_name,
                        battles_completed,
                        total_exp,
                        battles_per_hour
                    )
                    self.battles_since_last_notification = 0
                except Exception as e:
                    print(f"  ⚠️  Failed to send progress notification: {e}")
    
    def on_training_complete(self, battles_completed, total_exp, duration_str):
        """Called when training finishes normally"""
        if not self.is_enabled():
            return
        
        if self.config.get('send_completion', True):
            try:
                self.notifier.send_completion_notification(
                    self.account_name,
                    battles_completed,
                    total_exp,
                    duration_str
                )
            except Exception as e:
                print(f"  ⚠️  Failed to send completion notification: {e}")
    
    def on_training_error(self, error_message):
        """Called when an error occurs during training"""
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
    
    def on_training_cancelled(self, battles_completed, total_exp):
        """Called when training is cancelled by user"""
        if not self.is_enabled():
            return
        
        # Send cancellation as a special alert
        try:
            self.notifier.send_webhook(
                "⏹️  Training Cancelled",
                f"Account: {self.account_name}\nBattles: {battles_completed:,}\nXP: {total_exp:,}",
                "ff6600"  # Orange
            )
        except Exception as e:
            print(f"  ⚠️  Failed to send cancellation notification: {e}")


# Example integration into training loop:
"""
In training.py, modify the train() function:

def train(driver, account_name, max_battles=None, ...):
    from training_notifications_integration import TrainingNotifier
    
    # Initialize notifications for this account
    notifier = TrainingNotifier(account_name)
    
    if notifier.is_enabled():
        print("  ✅ Discord notifications enabled")
    
    battles_completed = 0
    total_exp_gained = 0
    start_time = time.time()
    
    try:
        while battles_completed < max_battles:
            # ... battle logic ...
            
            battles_completed += 1
            total_exp_gained += xp_gained
            
            # Notify on battle complete (includes progress updates at intervals)
            battles_per_hour = (battles_completed / (time.time() - start_time)) * 3600
            notifier.on_battle_complete(battles_completed, total_exp_gained, battles_per_hour)
            
            # Check cancellation, etc.
            if is_immediate_cancel_requested():
                notifier.on_training_cancelled(battles_completed, total_exp_gained)
                break
        
        # Training completed normally
        duration = time.time() - start_time
        duration_str = format_duration(duration)
        notifier.on_training_complete(battles_completed, total_exp_gained, duration_str)
    
    except Exception as e:
        notifier.on_training_error(str(e))
        raise
"""
