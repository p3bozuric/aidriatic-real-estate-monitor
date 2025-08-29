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

1. **User Newsletter API setup**
    - API endpoints to create a newsletter request, delete it or edit it.
    - This would require a login perhaps?

2. **Front end setup and user stories**
    - Login or registration on opening the web-site. Gmail enabled
    - My account dashboard - edit account, if active subscriber show metrics (in last x days we found x real-estates suitable for you - click and open the list of those real-estates),..
    - Active subscriber or inactive (add new boolean to subscriber information)
    - Previous newsletter interface with dates of sending,... (integrate new database table for saving of generated emails for users)
    - Simple "unsubscribe" button for newsletters
    - Basic "contact us" form
    - Show a loading spinner during data fetch
    - Display a "no results found" message if no listings match
    - Add a "refresh listings" button
    - Show last update time on dashboard

---

## Getting Started

Prepare with setup.bat for windows or setup.sh for linux.
---

## Notes

- Make sure to configure your .env credentials before running in production.