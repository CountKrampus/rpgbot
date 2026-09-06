"""
Multi-account management and automation
- Run multiple accounts in parallel
- Automatic rotation between accounts
- Load balancing
"""

import threading
import time
from pathlib import Path
import json

class MultiAccountManager:
    def __init__(self):
        self.accounts = {}
        self.active_threads = {}
        self.max_concurrent = 3  # Max 3 accounts at once
        self.rotation_enabled = False
    
    def add_account(self, account_name, config):
        """Add account to manager"""
        self.accounts[account_name] = {
            'config': config,
            'status': 'idle',
            'battles': 0,
            'xp': 0,
            'last_run': None,
            'thread': None
        }
    
    def run_parallel(self, account_list, task_func):
        """Run task on multiple accounts in parallel"""
        threads = []
        
        for account in account_list[:self.max_concurrent]:
            thread = threading.Thread(
                target=self._run_account_task,
                args=(account, task_func)
            )
            thread.daemon = True
            thread.start()
            threads.append((account, thread))
        
        # Wait for all to complete
        for account, thread in threads:
            thread.join()
        
        self.print_summary()
    
    def _run_account_task(self, account, task_func):
        """Run task for single account"""
        try:
            self.accounts[account]['status'] = 'running'
            result = task_func(account)
            self.accounts[account]['status'] = 'completed'
            self.accounts[account]['last_run'] = time.time()
            return result
        except Exception as e:
            self.accounts[account]['status'] = f'error: {str(e)[:50]}'
    
    def enable_rotation(self, interval=3600):
        """Enable automatic account rotation every N seconds"""
        self.rotation_enabled = True
        self.rotation_interval = interval
    
    def get_next_account(self):
        """Get account with lowest battles/XP for rotation"""
        if not self.accounts:
            return None
        
        return min(self.accounts.items(), 
                  key=lambda x: x[1]['battles'])[0]
    
    def print_summary(self):
        """Print all accounts summary"""
        print("\n" + "="*70)
        print("  MULTI-ACCOUNT SUMMARY")
        print("="*70)
        for account, data in self.accounts.items():
            print(f"  {account:20} | Battles: {data['battles']:8,} | XP: {data['xp']:10,} | {data['status']}")
        print("="*70 + "\n")

class AccountRotationScheduler:
    """Schedule training across multiple accounts automatically"""
    
    def __init__(self, manager):
        self.manager = manager
        self.schedule = {}
    
    def add_schedule(self, account, battles_per_day, start_hour=None):
        """Schedule account to run N battles per day"""
        self.schedule[account] = {
            'battles_per_day': battles_per_day,
            'start_hour': start_hour,
            'completed_today': 0,
            'last_reset': time.time()
        }
    
    def should_run(self, account):
        """Check if account should run now"""
        if account not in self.schedule:
            return False
        
        sched = self.schedule[account]
        completed = sched['completed_today']
        target = sched['battles_per_day']
        
        if completed < target:
            # Check start hour if specified
            if sched['start_hour'] is not None:
                import datetime
                current_hour = datetime.datetime.now().hour
                if current_hour < sched['start_hour']:
                    return False
            return True
        
        return False
    
    def update_progress(self, account, battles_completed):
        """Update daily progress"""
        self.schedule[account]['completed_today'] += battles_completed
    
    def reset_daily(self):
        """Reset daily counters at midnight"""
        for account in self.schedule:
            self.schedule[account]['completed_today'] = 0
            self.schedule[account]['last_reset'] = time.time()
