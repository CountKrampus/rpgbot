"""
Comprehensive training statistics and reporting
"""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta

class TrainingStats:
    def __init__(self, account_name):
        self.account_name = account_name
        self.start_time = time.time()
        self.battles_won = 0
        self.battles_lost = 0
        self.total_xp = 0
        self.errors = []
        self.stats_file = Path.home() / ".rpgbot" / "stats" / f"{account_name}_stats.json"
        self.stats_file.parent.mkdir(parents=True, exist_ok=True)
    
    def record_battle(self, won, xp=0):
        """Record individual battle"""
        if won:
            self.battles_won += 1
        else:
            self.battles_lost += 1
        self.total_xp += xp
    
    def record_error(self, error_type, message):
        """Record error for analysis"""
        self.errors.append({
            'type': error_type,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def get_stats_summary(self):
        """Get formatted statistics summary"""
        elapsed = time.time() - self.start_time
        total_battles = self.battles_won + self.battles_lost
        win_rate = (self.battles_won / total_battles * 100) if total_battles > 0 else 0
        
        battles_per_hour = (total_battles / (elapsed / 3600)) if elapsed > 0 else 0
        xp_per_hour = (self.total_xp / (elapsed / 3600)) if elapsed > 0 else 0
        
        elapsed_str = str(timedelta(seconds=int(elapsed)))
        
        return {
            'total_battles': total_battles,
            'battles_won': self.battles_won,
            'battles_lost': self.battles_lost,
            'win_rate': f"{win_rate:.1f}%",
            'total_xp': self.total_xp,
            'elapsed_time': elapsed_str,
            'battles_per_hour': f"{battles_per_hour:.0f}",
            'xp_per_hour': f"{xp_per_hour:.0f}",
            'errors_encountered': len(self.errors)
        }
    
    def save_stats(self):
        """Save statistics to file"""
        stats = self.get_stats_summary()
        stats['saved_at'] = datetime.now().isoformat()
        
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(stats, f, indent=2)
        except Exception as e:
            print(f"  [STATS] Error saving: {e}")
    
    def print_summary(self):
        """Print formatted statistics"""
        stats = self.get_stats_summary()
        print("\n" + "="*60)
        print(f"  TRAINING STATISTICS - {self.account_name}")
        print("="*60)
        print(f"  Total Battles: {stats['total_battles']:,}")
        print(f"    Won: {stats['battles_won']:,}")
        print(f"    Lost: {stats['battles_lost']:,}")
        print(f"    Win Rate: {stats['win_rate']}")
        print(f"  Total XP: {stats['total_xp']:,}")
        print(f"  Elapsed Time: {stats['elapsed_time']}")
        print(f"  Speed: {stats['battles_per_hour']} battles/hour")
        print(f"  XP Rate: {stats['xp_per_hour']} XP/hour")
        print(f"  Errors: {stats['errors_encountered']}")
        print("="*60 + "\n")
