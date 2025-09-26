import json
import os
import time
from datetime import datetime, timedelta
import random
from loguru import logger
from rss_parser.rss_parsing import parse_rss_feed
from crawl_job.crawler import process_real_estate_listing
from app.database.setup import setup_database

class JobRunner:
    def __init__(self):
        self.rss_url = "https://www.realestatecroatia.com/hrv/rss.asp"
        self.base_url = "http://www.realestatecroatia.com/hrv/detail.asp?id={}"
        self.data_file = "job_data/job_runner_data.json"
        self.load_data()

        setup_database()
    
    def load_data(self):
        """Load persistent data"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {
                "initial_min_id": None,
                "last_evening_max_id": None,
                "pending_jobs": [],
                "system_initialized": False
            }
    
    def save_data(self):
        """Save persistent data"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def get_ids_from_rss(self):
        """Extract all IDs from RSS feed"""
        try:
            rss_data = parse_rss_feed(self.rss_url)
            ids = [int(item['id']) for item in rss_data]
            return sorted(ids)
        except Exception as e:
            logger.error(f"Error parsing RSS feed: {e}")
            return []
    
    def start_check(self):
        """Run once on system boot - get the minimum ID as baseline"""
        logger.info(f"Running initial start check at {datetime.now()}")
        
        if self.data["system_initialized"]:
            logger.warning("System already initialized. Use evening_check() for regular operations.")
            return
        
        ids = self.get_ids_from_rss()
        if not ids:
            logger.error("No IDs found in RSS feed during start check")
            return
        
        min_id = min(ids)
        
        self.data["initial_min_id"] = min_id
        self.data["system_initialized"] = True
        
        logger.info(f"System initialized with minimum ID: {min_id}")
        self.save_data()
    
    def evening_check(self):
        """Run at 23:59 daily - find maximum ID and schedule scraping jobs"""
        logger.info(f"Running evening check at {datetime.now()}")
        
        if not self.data["system_initialized"]:
            logger.error("System not initialized. Run start_check() first!")
            return
        
        ids = self.get_ids_from_rss()
        if not ids:
            logger.warning("No IDs found in RSS feed")
            return
        
        max_id = max(ids)
        
        # Determine minimum ID for this batch
        if self.data["last_evening_max_id"] is None:
            # First evening check after start_check
            min_id = self.data["initial_min_id"]
        else:
            # Subsequent evening checks
            min_id = self.data["last_evening_max_id"] + 1
        
        logger.info(f"Evening check: ID range is {min_id} to {max_id} ({max_id - min_id + 1} IDs)")
        
        # Create list of IDs to scrape
        id_range = list(range(min_id, max_id + 1))
        
        # Schedule scraping jobs across the night (00:00-05:00)
        self.schedule_scraping_jobs(id_range)
        
        # Update last evening max for next run
        self.data["last_evening_max_id"] = max_id
        self.save_data()
    
    def schedule_scraping_jobs(self, id_list):
        """Schedule scraping jobs evenly across 5 hours (00:00-05:00)"""
        if not id_list:
            logger.warning("No IDs to scrape")
            return
        
        # Clear any existing pending jobs
        self.data["pending_jobs"] = []
        
        # Calculate time intervals (5 hours = 18000 seconds)
        total_seconds = 5 * 60 * 60  # 5 hours
        interval = total_seconds / len(id_list) if len(id_list) > 1 else 0
        
        logger.info(f"Scheduling {len(id_list)} jobs with {interval:.1f} second intervals")
        
        # Create job schedule starting from next midnight
        tomorrow = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        for i, id_num in enumerate(id_list):
            job_time = tomorrow + timedelta(seconds=i * interval)
            
            self.data["pending_jobs"].append({
                "id": id_num,
                "scheduled_time": job_time.isoformat(),
                "completed": False
            })
        
        self.save_data()
        logger.info(f"Scheduled {len(id_list)} scraping jobs from {tomorrow} to {tomorrow + timedelta(hours=5)}")
    
    def run_scraping_jobs(self):
        """Check and run any pending scraping jobs"""
        current_time = datetime.now()
        jobs_run = 0
        
        for job in self.data["pending_jobs"]:
            if job["completed"]:
                continue
            
            job_time = datetime.fromisoformat(job["scheduled_time"])
            
            # If it's time to run this job (with 1 minute tolerance)
            if current_time >= job_time and current_time <= job_time + timedelta(minutes=1):
                self.scrape_listing(job["id"])
                job["completed"] = True
                jobs_run += 1
        
        if jobs_run > 0:
            logger.info(f"Completed {jobs_run} scraping jobs")
            self.save_data()
    
    def scrape_listing(self, listing_id):
        """Scrape a single listing by ID"""
        try:
            url = self.base_url.format(listing_id)
            logger.debug(f"Scraping listing ID {listing_id}: {url}")
            
            # Your existing function call
            process_real_estate_listing(url, id=listing_id)
            
            # Add small random delay to be nice to the server
            time.sleep(random.uniform(1, 3))
            
        except Exception as e:
            logger.error(f"Error scraping listing {listing_id}: {e}")
    
    def cleanup_completed_jobs(self):
        """Remove completed jobs older than 1 day"""
        cutoff_time = datetime.now() - timedelta(days=1)
        
        self.data["pending_jobs"] = [
            job for job in self.data["pending_jobs"]
            if not job["completed"] or 
            datetime.fromisoformat(job["scheduled_time"]) > cutoff_time
        ]
        self.save_data()
    
    def get_status(self):
        """Get current job runner status"""
        total_jobs = len(self.data["pending_jobs"])
        completed_jobs = sum(1 for job in self.data["pending_jobs"] if job["completed"])
        pending_jobs = total_jobs - completed_jobs
        
        status_message = f"""
Job Runner Status:
- System initialized: {self.data.get('system_initialized', False)}
- Initial minimum ID: {self.data.get('initial_min_id', 'None')}
- Last evening max ID: {self.data.get('last_evening_max_id', 'None')}
- Next minimum ID: {(self.data.get('last_evening_max_id', 0) + 1) if self.data.get('last_evening_max_id') else self.data.get('initial_min_id', 'None')}
- Total jobs: {total_jobs}
- Completed: {completed_jobs}
- Pending: {pending_jobs}

External Scheduler Guide:
- Run start_check() ONCE when system first boots
- Call evening_check() at 23:59 daily
- Call run_scraping_jobs() every minute during 00:00-05:00
- Call cleanup_completed_jobs() once daily (e.g., at 06:00)
        """
        
        logger.info(status_message)
        
        return {
            "system_initialized": self.data.get('system_initialized', False),
            "initial_min_id": self.data.get('initial_min_id'),
            "last_evening_max_id": self.data.get('last_evening_max_id'),
            "next_min_id": (self.data.get('last_evening_max_id', 0) + 1) if self.data.get('last_evening_max_id') else self.data.get('initial_min_id'),
            "total_jobs": total_jobs,
            "completed_jobs": completed_jobs,
            "pending_jobs": pending_jobs
        }
    
# Usage
if __name__ == "__main__":
    runner = JobRunner()
    
    # Example usage - call these from your external scheduler
    
    # ON FIRST BOOT ONLY:
    runner.start_check()      # Run ONCE when system first starts
    
    # THEN EVERY DAY:
    runner.evening_check()    # Call at 23:59 daily
    runner.run_scraping_jobs()  # Call every minute during 00:00-05:00
    runner.cleanup_completed_jobs()  # Call once daily (e.g., at 06:00)
    
    # Check status anytime:
    runner.get_status()