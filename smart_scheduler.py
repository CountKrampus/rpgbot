"""
Intelligent task scheduling based on:
- Time of day
- Server load patterns
- Account priorities
- Resource availability
"""

import time
from datetime import datetime, timedelta
from enum import Enum

class Priority(Enum):
    LOW = 3
    MEDIUM = 2
    HIGH = 1
    CRITICAL = 0

class SmartScheduler:
    def __init__(self):
        self.tasks = {}
        self.running = False
        self.server_peak_hours = [12, 18, 19, 20]  # Noon, 6-8 PM
    
    def add_task(self, task_id, account, task_type, duration, priority=Priority.MEDIUM):
        """Add task to scheduler"""
        self.tasks[task_id] = {
            'account': account,
            'type': task_type,  # 'training', 'searching', 'mining'
            'duration': duration,
            'priority': priority,
            'status': 'queued',
            'created_at': time.time(),
            'started_at': None,
            'completed_at': None
        }
    
    def get_optimal_start_time(self):
        """Calculate best time to start tasks based on server patterns"""
        current_hour = datetime.now().hour
        
        # Avoid peak hours if possible
        if current_hour in self.server_peak_hours:
            # Find next off-peak hour
            for i in range(24):
                next_hour = (current_hour + i) % 24
                if next_hour not in self.server_peak_hours:
                    return next_hour
        
        return current_hour
    
    def should_throttle(self):
        """Determine if we should throttle requests"""
        current_hour = datetime.now().hour
        
        if current_hour in self.server_peak_hours:
            return True
        
        return False
    
    def get_task_order(self):
        """Get tasks in optimal order (by priority)"""
        sorted_tasks = sorted(
            self.tasks.items(),
            key=lambda x: (x[1]['priority'].value, x[1]['created_at'])
        )
        return [task_id for task_id, _ in sorted_tasks]
    
    def get_next_task(self):
        """Get next task to run"""
        queued = [
            (task_id, task) for task_id, task in self.tasks.items()
            if task['status'] == 'queued'
        ]
        
        if not queued:
            return None
        
        # Sort by priority and creation time
        queued.sort(key=lambda x: (x[1]['priority'].value, x[1]['created_at']))
        return queued[0][0]
    
    def mark_running(self, task_id):
        """Mark task as running"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'running'
            self.tasks[task_id]['started_at'] = time.time()
    
    def mark_completed(self, task_id):
        """Mark task as completed"""
        if task_id in self.tasks:
            self.tasks[task_id]['status'] = 'completed'
            self.tasks[task_id]['completed_at'] = time.time()
    
    def print_queue(self):
        """Print task queue"""
        print("\n" + "="*70)
        print("  TASK QUEUE")
        print("="*70)
        for task_id, task in sorted(self.tasks.items(), 
                                    key=lambda x: x[1]['priority'].value):
            print(f"  [{task['priority'].name:8}] {task_id:20} {task['account']:15} {task['status']:10}")
        print("="*70 + "\n")

class ResourceMonitor:
    """Monitor system resources and adjust workload"""
    
    def __init__(self):
        self.cpu_threshold = 80  # %
        self.memory_threshold = 80  # %
        self.network_threshold = 90  # %
    
    def get_cpu_usage(self):
        """Get CPU usage percentage"""
        try:
            import psutil
            return psutil.cpu_percent(interval=1)
        except:
            return 0
    
    def get_memory_usage(self):
        """Get memory usage percentage"""
        try:
            import psutil
            return psutil.virtual_memory().percent
        except:
            return 0
    
    def can_add_workload(self):
        """Check if system can handle more work"""
        cpu = self.get_cpu_usage()
        memory = self.get_memory_usage()
        
        if cpu > self.cpu_threshold or memory > self.memory_threshold:
            return False
        
        return True
    
    def get_recommended_concurrency(self):
        """Get recommended number of concurrent tasks"""
        memory = self.get_memory_usage()
        cpu = self.get_cpu_usage()
        
        # Start with 3, reduce based on resource usage
        concurrency = 3
        
        if memory > 70:
            concurrency = 2
        if memory > 85:
            concurrency = 1
        
        if cpu > 70:
            concurrency = max(1, concurrency - 1)
        
        return concurrency
