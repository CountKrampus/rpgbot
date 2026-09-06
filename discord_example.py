"""
Simple example of using Discord notifications
"""

from notifications import NotificationSystem
import time

# Create notifier
notifier = NotificationSystem()

# Enable your Discord webhook
# Get the URL from: https://discord.com/api/webhooks/YOUR_ID/YOUR_TOKEN
webhook_url = "https://discord.com/api/webhooks/YOUR_WEBHOOK_URL_HERE"
notifier.enable_webhook(webhook_url)

# Send a test message
print("Sending test notification...")
notifier.send_webhook(
    "🚀 RPGBot Started",
    "Bot is now running and training!",
    "0099ff"  # Blue
)

# Simulate training with notifications
print("\nSimulating training session...\n")

battles = 0
total_xp = 0

for i in range(10):
    battles += 500000
    total_xp += 2500000
    
    print(f"Battle {i+1}: {battles:,} battles, {total_xp:,} XP")
    
    # Send progress update every 500K battles
    notifier.send_progress_update(
        "CreamKrampus",
        battles,
        total_xp,
        50000  # battles/hour
    )
    
    time.sleep(1)  # Wait 1 second between updates

# Send completion notification
print("\n✅ Training complete!")
notifier.send_completion_notification(
    "CreamKrampus",
    battles,
    total_xp,
    "5:00:00"
)

print("\n✅ All notifications sent to Discord!")
