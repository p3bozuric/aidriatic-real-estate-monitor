from app.crawl_job.job import JobRunner
from app.database.setup import setup_database

def main():
    setup_database()
    
    job = JobRunner()
    job.start_check()

if __name__ == "__main__":
    main()