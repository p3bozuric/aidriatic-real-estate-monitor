# Aidriatic Real Estate Monitor

## Project Overview

This project monitors Croatian real estate listings via RSS, crawls new listings, manages user property wishes, stores data in a database, applies filters, and sends email notifications.

---

## Status & TODO

- **Database:** Implemented and operational.
- **Filters:** Basic logic for hard and soft filters is in place.
- **Scraping:** Logic for tracking scraping and scrape jobs is built.
- **Emails:** Logic for sending email has been setup
- **Scheduling:** Scheduling set up with cron scheduler for linux (project is meant to be run on linux)
- **Email Notifications:** Set up.
- **Deployment:** Ready for deployment on aidriatic.com by using docker and EC2.

### Next Steps

1. **Filter**
    - Set up limits on which properties are going to get extracted for filtering (prefilter based on min and max ID)

2. **User Newsletter setup**
    - API endpoints to create a newsletter request, delete it or edit it.
    - This would require a login perhaps?

---

## Getting Started

1. **Install dependencies:**
    ```sh
    uv pip install -r requirements.txt
    playwright install
    ```

2. **Run the main script:**
    ```sh
    python main.py
    ```

---

## Notes

- Make sure to configure your database and email credentials before running in production.
- See `main.py` for the current entry point and workflow.