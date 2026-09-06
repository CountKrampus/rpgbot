"""Discord notifications settings menu"""
from pathlib import Path
import json
from notifications import NotificationSystem

class DiscordSettingsManager:
    def __init__(self):
        self.config_dir = Path.home() / ".rpgbot"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "discord_config.json"
        self.config = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                return self.default_config()
        return self.default_config()
    
    def default_config(self):
        return {
            "webhook_url": "",
            "enabled": False,
            "send_progress": True,
            "progress_interval": 500000,
            "send_completion": True,
            "send_errors": True,
        }
    
    def save_config(self):
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"  ❌ Error saving config: {e}")
            return False
    
    def test_webhook(self):
        if not self.config['webhook_url']:
            return False, "No webhook URL configured"
        
        notifier = NotificationSystem()
        notifier.enable_webhook(self.config['webhook_url'])
        
        success = notifier.send_webhook(
            "🧪 Test Notification",
            "If you see this, Discord notifications are working!",
            "0099ff"
        )
        
        return (True, "✅ Webhook is working!") if success else (False, "❌ Webhook test failed")
    
    def set_webhook_url(self, url):
        if not url.startswith("https://discord.com/api/webhooks/"):
            return False, "Invalid webhook URL format"
        
        self.config['webhook_url'] = url
        return (True, "✅ Webhook URL saved") if self.save_config() else (False, "❌ Failed to save")
    
    def toggle_notifications(self):
        self.config['enabled'] = not self.config['enabled']
        self.save_config()
        status = "enabled" if self.config['enabled'] else "disabled"
        return f"✅ Notifications {status}"
    
    def show_status(self):
        status = ["\n" + "="*60, "  DISCORD NOTIFICATIONS STATUS", "="*60]
        
        if self.config['webhook_url']:
            url_preview = self.config['webhook_url'][:50] + "..."
            status.append(f"  Webhook: {url_preview}")
        else:
            status.append("  Webhook: ❌ Not configured")
        
        status.append(f"  Status: {'✅ Enabled' if self.config['enabled'] else '❌ Disabled'}")
        status.append(f"  Progress Updates: {'✅' if self.config['send_progress'] else '❌'}")
        status.append(f"  Completion: {'✅' if self.config['send_completion'] else '❌'}")
        status.append("="*60 + "\n")
        
        return "\n".join(status)

def show_discord_menu():
    manager = DiscordSettingsManager()
    
    while True:
        print(manager.show_status())
        print("  [1] Set Discord Webhook URL")
        print("  [2] Test Webhook")
        print("  [3] Toggle Notifications")
        print("  [0] Back to Settings")
        
        choice = input("\n  Select option: ").strip()
        
        if choice == "1":
            url = input("\n  Enter Discord Webhook URL: ").strip()
            success, message = manager.set_webhook_url(url)
            print(f"\n  {message}")
        elif choice == "2":
            print("\n  Testing webhook...")
            success, message = manager.test_webhook()
            print(f"  {message}")
        elif choice == "3":
            message = manager.toggle_notifications()
            print(f"  {message}")
        elif choice == "0":
            break
        else:
            print("  ❌ Invalid choice")
        
        input("\n  Press Enter to continue...")
        print()
