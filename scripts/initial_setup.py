from crawl_job.job import JobRunner
from database.setup import setup_database

setup_database()

job = JobRunner()

job.start_check()