# Aidriatic Real Estate Monitor

## Project Overview

This project monitors Croatian real estate listings via RSS, crawls new listings, manages user property wishes, stores data in a database, applies filters, and sends email notifications.

---

## TODO

1. **Scheduled RSS Checks**
    - Perform an RSS check at 00:00 on the first day of each month, and another at midnight daily.
    - For each check, collect all listing IDs published in that window that are not already in the database.

2. **User Management**
    - Implement user registration and management.
    - Allow users to specify their property preferences ("wishes").

3. **Database Integration**
    - Store property data in a database (convert JSON to DB records).
    - Use Supabase, Airflow, or another suitable solution for storage and orchestration.

4. **Filtering**
    - Implement HARD filters (strict requirements).
    - Implement SOFT filters (preferences, nice-to-have).

5. **Email Notifications**
    - Set up email sending to notify users about new listings that match their filters.

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