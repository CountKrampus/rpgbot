# RPGBot Usage Examples

## Number Format Support

All input fields now support human-friendly number formats:

```
300000   →  300,000 battles
300k     →  300,000 battles
1.5k     →  1,500 battles
2m       →  2,000,000 battles
1.2m     →  1,200,000 battles
5b       →  5,000,000,000 battles
```

### Supported Suffixes
- **k** = thousands (×1,000)
- **m** = millions (×1,000,000)
- **b** = billions (×1,000,000,000)
- **t** = trillions (×1,000,000,000,000)

---

## Training Example

### Old Way (Still Works)
```
How many battles? 3000000
```

### New Way (Much Better!)
```
How many battles? 3m
✅ Confirm: 3m? (y/n): y
```

**Benefits:**
- Faster to type
- Less error-prone
- Clear what you mean

---

## Multi-Account Example

When farming 3 accounts simultaneously:

```bash
# Terminal 1: Account 1
python main.py
  Select account: CreamKrampus
  Training target: 3m
  ✅ Training 3,000,000 battles

# Terminal 2: Account 2
python main.py
  Select account: Goldisduck
  Training target: 2.5m
  ✅ Training 2,500,000 battles

# Terminal 3: Account 3
python main.py
  Select account: TestAccount
  Training target: 1.5m
  ✅ Training 1,500,000 battles
```

**Total: 7 million battles in parallel!**

---

## Searching Example

```
How many searches? 500k
✅ Confirm: 500k? (y/n): y
```

Searches for 500,000 items.

---

## Mining Example

```
How many mines? 250k
✅ Confirm: 250k? (y/n): y
```

Mines 250,000 ore.

---

## Discord Notifications + Large Numbers

```python
from notifications import NotificationSystem
from number_parser import NumberParser

notifier = NotificationSystem()
notifier.enable_webhook("YOUR_WEBHOOK_URL")

# Format large numbers nicely
battles = 1_500_000
xp = 7_500_000

# Send as formatted (1.5m, 7.5m)
notifier.send_progress_update(
    "CreamKrampus",
    battles,
    xp,
    50000
)
```

Discord will show:
```
🔄 Progress Update
━━━━━━━━━━━━━━━━━━━━━━
Battles: 1.5m
XP: 7.5m
Speed: 50k/hour
```

---

## Settings Menu Integration

When you run the bot:

```
MAIN MENU
[1] Training
[2] Searching
[3] Mining
[4] Settings
[0] Exit

Select: 4

SETTINGS
[1] Browser Settings
[2] Discord Notifications ← NEW!
[3] Advanced Settings
[0] Back

Select: 2

DISCORD NOTIFICATIONS STATUS
━━━━━━━━━━━━━━━━━━━━━━━━━━
Webhook: https://discord.com/api/webhooks/...
Status: ❌ Disabled

[1] Set Discord Webhook URL
[2] Test Webhook
[3] Toggle Notifications
[0] Back

Select: 1

Enter Discord Webhook URL: https://discord.com/api/webhooks/YOUR_URL
✅ Webhook URL saved

Select: 3
✅ Notifications enabled

Select: 2
Testing webhook...
✅ Webhook is working!
```

---

## Complete Workflow Example

### Step 1: Configure Discord (One-time)
```bash
python main.py
Select: 4 (Settings)
Select: 2 (Discord)
Select: 1 (Set Webhook URL)
# Paste your Discord webhook URL
Select: 2 (Test Webhook)
✅ Success
```

### Step 2: Start Training Account 1
```bash
python main.py
Select: 1 (Training)
How many battles? 3m
✅ Confirm: 3m? (y/n): y
# Bot starts training
# Discord notifications automatically sent every 500k battles
```

### Step 3: Start Training Account 2 (New Terminal)
```bash
python main.py
Select: 1 (Training)
How many battles? 2.5m
# Bot starts training
# Discord notifications sent
```

### Step 4: Start Training Account 3 (Another Terminal)
```bash
python main.py
Select: 1 (Training)
How many battles? 1.5m
# Bot starts training
# Discord notifications sent
```

### What You See in Discord
```
🔄 Progress Update
Account: CreamKrampus
Battles: 500k
XP: 2.5m
Speed: 50k/hour

🔄 Progress Update
Account: Goldisduck
Battles: 480k
XP: 2.4m
Speed: 48k/hour

🔄 Progress Update
Account: TestAccount
Battles: 520k
XP: 2.6m
Speed: 52k/hour

✅ Training Complete
Account: CreamKrampus
Total Battles: 3m
Total XP: 15m
Duration: 60:30:15
```

**No manual monitoring needed!**

---

## Number Format Cheat Sheet

| Input | Means | Useful For |
|-------|-------|-----------|
| 100000 | 100,000 | Reasonable targets |
| 100k | 100,000 | Faster to type |
| 1m | 1,000,000 | Large milestones |
| 1.5m | 1,500,000 | Specific amounts |
| 5m | 5,000,000 | Multi-account farming |
| 10m | 10,000,000 | Long sessions |
| 100m | 100,000,000 | Weekly goals |
| 1b | 1,000,000,000 | Massive goals |

---

## Error Handling

### Invalid Input
```
How many battles? abc
❌ Invalid input. Use format: 300000 or 300k or 1.5m

How many battles? 0
❌ Value must be at least 1k

How many battles? 300k
✅ Training 300,000 battles
```

### Cancel Input
```
How many battles? q
# Cancelled, back to menu
```

---

## Performance Tips

### For 3 Accounts Farming 7m Total
```
Terminal 1: 3m      (3 hours)
Terminal 2: 2.5m    (2.5 hours)
Terminal 3: 1.5m    (1.5 hours)

All running in parallel = Fastest way!
```

### Recommended Discord Interval
- Default: 500k battles per update
- Too frequent: 100k (spammy)
- Too rare: 1m (miss updates)
- **Sweet spot: 500k or 1m**

---

**Everything is now faster, easier, and more automated!** 🚀
