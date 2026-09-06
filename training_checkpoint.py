"""
Training session checkpoint/recovery system
Saves progress periodically so bot can resume if it crashes
"""

import json
import time
from pathlib import Path

class TrainingCheckpoint:
    def __init__(self, account_name):
        self.account_name = account_name
        self.checkpoint_dir = Path.home() / ".rpgbot" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        self.checkpoint_file = self.checkpoint_dir / f"{account_name}_training.json"
    
    def save(self, battles_completed, xp_gained, current_level=None):
        """Save checkpoint every N battles"""
        checkpoint_data = {
            "account": self.account_name,
            "timestamp": time.time(),
            "battles_completed": battles_completed,
            "xp_gained": xp_gained,
            "current_level": current_level
        }
        
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        print(f"  [CHECKPOINT] Saved: {battles_completed} battles, {xp_gained} XP")
    
    def load(self):
        """Load previous checkpoint if it exists"""
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"  [CHECKPOINT] Error loading: {e}")
                return None
        return None
    
    def clear(self):
        """Clear checkpoint after successful completion"""
        if self.checkpoint_file.exists():
            self.checkpoint_file.unlink()
            print(f"  [CHECKPOINT] Cleared")

def resume_training_prompt(checkpoint_data):
    """Prompt user if they want to resume from checkpoint"""
    battles = checkpoint_data.get('battles_completed', 0)
    xp = checkpoint_data.get('xp_gained', 0)
    timestamp = checkpoint_data.get('timestamp', 0)
    
    # Calculate how long ago
    import datetime
    saved_time = datetime.datetime.fromtimestamp(timestamp)
    print(f"\n  Previous training found:")
    print(f"    Battles completed: {battles:,}")
    print(f"    XP gained: {xp:,}")
    print(f"    Saved: {saved_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    response = input("\n  Resume from checkpoint? [y/n]: ").lower().strip()
    return response == 'y'
