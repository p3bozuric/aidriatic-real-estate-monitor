from crawl_job.job import JobRunner

job = JobRunner()

job.evening_check()

job.run_scraping_jobs()

job.cleanup_completed_jobs()