from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, List, Dict, Any
import datetime

class Scheduler:
    """
    Scheduler for running video scanning jobs on a regular basis
    """
    
    def __init__(self):
        """Initialize the scheduler"""
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.jobs = {}
    
    def schedule_job(self, job_id: str, func: Callable, interval_hours: int = 12, args: List = None, kwargs: Dict = None):
        """
        Schedule a job to run at regular intervals
        
        Args:
            job_id: Unique identifier for the job
            func: Function to call
            interval_hours: Interval between runs in hours
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
        """
        if job_id in self.jobs:
            self.remove_job(job_id)
        
        # Schedule the job to run at the specified interval
        job = self.scheduler.add_job(
            func,
            'interval',
            hours=interval_hours,
            args=args or [],
            kwargs=kwargs or {},
            id=job_id,
            next_run_time=datetime.datetime.now()  # Run immediately
        )
        
        self.jobs[job_id] = job
        return job
    
    def schedule_daily_job(self, job_id: str, func: Callable, hour: int = 0, minute: int = 0, args: List = None, kwargs: Dict = None):
        """
        Schedule a job to run daily at a specific time
        
        Args:
            job_id: Unique identifier for the job
            func: Function to call
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            args: Arguments to pass to the function
            kwargs: Keyword arguments to pass to the function
        """
        if job_id in self.jobs:
            self.remove_job(job_id)
        
        # Schedule the job to run daily at the specified time
        trigger = CronTrigger(hour=hour, minute=minute)
        job = self.scheduler.add_job(
            func,
            trigger,
            args=args or [],
            kwargs=kwargs or {},
            id=job_id
        )
        
        self.jobs[job_id] = job
        return job
    
    def remove_job(self, job_id: str):
        """
        Remove a scheduled job
        
        Args:
            job_id: Unique identifier for the job
        """
        if job_id in self.jobs:
            self.scheduler.remove_job(job_id)
            del self.jobs[job_id]
    
    def shutdown(self):
        """Shut down the scheduler"""
        self.scheduler.shutdown()
