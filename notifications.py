"""
Notification and alerting system
- Email notifications
- Webhook notifications
- Progress updates
- Error alerts
"""

import json
import requests
from datetime import datetime

class NotificationSystem:
    def __init__(self):
        self.email_enabled = False
        self.webhook_enabled = False
        self.email_config = {}
        self.webhook_url = None
    
    def enable_email(self, sender_email, password, recipient_email):
        """Enable email notifications"""
        self.email_enabled = True
        self.email_config = {
            'sender': sender_email,
            'password': password,
            'recipient': recipient_email
        }
    
    def enable_webhook(self, webhook_url):
        """Enable webhook notifications (Discord, Slack, etc)"""
        self.webhook_enabled = True
        self.webhook_url = webhook_url
    
    def send_webhook(self, title, message, color="0099ff"):
        """Send notification via webhook"""
        if not self.webhook_enabled or not self.webhook_url:
            return False
        
        try:
            # Format for Discord embed
            data = {
                "embeds": [{
                    "title": title,
                    "description": message,
                    "color": int(color.replace("#", ""), 16) if "#" in color else int(color, 16),
                    "timestamp": datetime.now().isoformat()
                }]
            }
            
            response = requests.post(self.webhook_url, json=data, timeout=10)
            return response.status_code == 204
        except Exception as e:
            print(f"  [WEBHOOK] Error: {e}")
            return False
    
    def send_progress_update(self, account, battles, xp, speed):
        """Send progress update"""
        message = f"Account: {account}\nBattles: {battles:,}\nXP: {xp:,}\nSpeed: {speed} battles/hour"
        self.send_webhook("🔄 Progress Update", message, "00ff00")
    
    def send_error_alert(self, account, error):
        """Send error alert"""
        message = f"Account: {account}\nError: {error}"
        self.send_webhook("❌ Error Alert", message, "ff0000")
    
    def send_completion_notification(self, account, total_battles, total_xp, duration):
        """Send completion notification"""
        message = f"""
Account: {account}
Total Battles: {total_battles:,}
Total XP: {total_xp:,}
Duration: {duration}
"""
        self.send_webhook("✅ Training Complete", message, "00ff00")
    
    def send_session_report(self, stats):
        """Send detailed session report"""
        report = f"""
{stats.get('total_battles', 0):,} battles
{stats.get('win_rate', '0%')} win rate
{stats.get('xp_per_hour', '0')} XP/hour
{stats.get('errors_encountered', 0)} errors
"""
        self.send_webhook("📊 Session Report", report, "0099ff")

class AlertManager:
    def __init__(self):
        self.alerts = []
        self.alert_thresholds = {
            'error_rate': 5,  # % errors
            'memory_usage': 80,  # %
            'cpu_usage': 85,  # %
            'high_ping': 500  # ms
        }
    
    def add_alert(self, alert_type, message, severity="warning"):
        """Add alert to system"""
        self.alerts.append({
            'type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        
        print(f"  [ALERT] [{severity.upper()}] {alert_type}: {message}")
    
    def check_thresholds(self, stats):
        """Check if any thresholds are exceeded"""
        if stats.get('error_rate', 0) > self.alert_thresholds['error_rate']:
            self.add_alert('high_error_rate', 
                          f"Error rate: {stats['error_rate']}%", 
                          'critical')
    
    def get_alerts(self, severity=None):
        """Get alerts filtered by severity"""
        if severity:
            return [a for a in self.alerts if a['severity'] == severity]
        return self.alerts
    
    def clear_alerts(self):
        """Clear all alerts"""
        self.alerts = []
