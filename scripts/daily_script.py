from crawl_job.job import JobRunner

def main():
    job = JobRunner()

    job.evening_check()

    job.run_scraping_jobs()

    job.cleanup_completed_jobs()

if __name__ == "__main__":
    main()