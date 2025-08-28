from rss_parser.rss_parsing import parse_rss_feed, save_entries_to_file
from crawl_job.crawler import process_real_estate_listing
import asyncio
from database.setup import setup_database
from loguru import logger

setup_database()

# RSS feed URL
url = "https://www.realestatecroatia.com/hrv/rss.asp"

# 1)
latest_real_estate = parse_rss_feed(url)

# 2)
save_entries_to_file(latest_real_estate)

# 3)
process_real_estate_listing(latest_real_estate[0]['link'], id=latest_real_estate[0]['id'])


