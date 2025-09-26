import feedparser
import os
from datetime import datetime

def parse_rss_feed(url):
    # Parse the feed
    feed = feedparser.parse(url)

    new_entries = []

    for entry in feed.entries:

        new_entries.append({
            "id": entry.get('link', 'No link').split("id=")[-1],
            "title": entry.get('title', 'No title'),
            "link": entry.get('link', 'No link'),
            "published": entry.get('published', 'No date')
        })

    return new_entries

def save_entries_to_file(entries, folder="rss_export"):
    # Prepare export folder and filename
    os.makedirs(folder, exist_ok=True)
    timestamp = datetime.now().strftime("%d%m%Y%H")
    filename = f"rss_export_{timestamp}.txt"
    filepath = os.path.join(folder, filename)

    # Save the entries to file
    with open(filepath, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"ID: {entry.get('id', 'No id')}\n")
            f.write(f"Title: {entry.get('title', 'No title')}\n")
            f.write(f"Link: {entry.get('link', 'No link')}\n")
            f.write(f"Published: {entry.get('published', 'No date')}\n\n")

    print(f"Saved latest entries to {filepath}")
