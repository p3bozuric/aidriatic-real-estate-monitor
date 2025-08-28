from rss_parser.rss_parsing import parse_rss_feed, save_entries_to_file
from crawl_job.crawler import process_real_estate_listing
import asyncio


# RSS feed URL
url = "https://www.realestatecroatia.com/hrv/rss.asp"

latest_real_estate = parse_rss_feed(url)



save_entries_to_file(latest_real_estate)

process_real_estate_listing(latest_real_estate[0]['link'], id=latest_real_estate[0]['id'])


