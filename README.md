# Aidriatic Real Estate Monitor

## Project Overview

This project monitors Croatian real estate listings via RSS, crawls new listings, manages user property wishes, stores data in a database, applies filters, and sends email notifications. It provides a REST API for user management and property filtering based on user goals.

---

## Current Architecture

### Core Components ✅ COMPLETED
- **Database:** PostgreSQL with tables for properties, users, user_goals, and user_goal_criteria_met
- **Property Crawling:** RSS monitoring and data extraction via scheduled scripts
- **Filtering:** Advanced property filtering based on user criteria
- **Email Service:** Email notification system setup
- **Scheduling:** Cron-based daily crawling via `daily_script.py`
- **API Framework:** FastAPI with JWT authentication

### API Endpoints ✅ COMPLETED
- **User Management:** Registration, login, profile management with JWT tokens
- **User Goals:** CRUD operations for property search criteria
- **Property Filtering:** Goal-based property matching and listing
- **Database Models:** Pydantic models for request/response validation

---

## Status & TODO

### 🚀 Recently Completed
- ✅ REST API with FastAPI framework
- ✅ JWT authentication system
- ✅ User management endpoints (register/login/profile)
- ✅ User goals CRUD operations
- ✅ Property filtering and goal-matching endpoints
- ✅ Database schema with proper relationships
- ✅ Pydantic models for data validation

### 🔧 Infrastructure Improvements Needed
1. **Database Connection Management**
   - Implement connection pooling instead of per-request connections
   - Proper session management and cleanup

2. **Configuration Management**
   - Centralized settings/config module
   - Environment-specific configurations

3. **Error Handling & Middleware**
   - Global exception handling middleware
   - Standardized error responses
   - Apply rate limiting middleware to endpoints

4. **Background Tasks**
   - Async task queue for property matching updates
   - Email sending via background workers

5. **Logging & Monitoring**
   - Centralized logging configuration
   - API request/response logging
   - Performance monitoring

### 🎯 Next Phase: Frontend Development
1. **User Interface**
   - Login/registration with OAuth (Gmail integration)
   - Dashboard with property matching metrics
   - Goal management interface
   - Property browsing and filtering

2. **User Experience Features**
   - Email preferences and unsubscribe functionality
   - Newsletter history and tracking
   - Contact forms and support

3. **Advanced Features**
   - Text-based property search (optional)
   - Property alerts and notifications
   - Saved searches and bookmarks

---

## Project Structure

```
aidriatic-real-estate-monitor/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── endpoints/          # API route handlers
│   │   │   │   ├── users.py
│   │   │   │   ├── user_goals.py
│   │   │   │   └── properties.py
│   │   │   └── models/             # Pydantic models
│   │   │       ├── user_models.py
│   │   │       ├── user_goal_models.py
│   │   │       └── property_models.py
│   │   └── deps.py                 # FastAPI dependencies
│   ├── database/
│   │   ├── setup.py               # Database schema
│   │   └── control.py             # Database operations
│   ├── scripts/
│   │   ├── initial_setup.py       # First-time setup
│   │   ├── daily_script.py        # Daily crawling job
│   │   └── send_email.py          # Email notifications
│   └── main.py                    # FastAPI application
├── crawl_job/                     # Web crawling logic
├── emailing/                      # Email service
├── filtering/                     # Property filtering
└── pyproject.toml                 # Dependencies and scripts
```

---

## Getting Started

### Prerequisites
- Python 3.12+
- PostgreSQL database
- Environment variables configured in `.env`
- UV package manager (recommended) or pip

### Installation
1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set up database:
   ```bash
   python app/database/setup.py
   ```

3. Run initial setup:
   ```bash
   initial_setup
   ```

4. Start the API server:
   ```bash
   uvicorn app.main:app --reload
   ```

5. Set up daily crawling (cron job):
   ```bash
   # Add to crontab for daily execution
   0 18 * * * /path/to/python -m scripts.daily_script
   ```

### API Documentation
- Interactive docs: `http://localhost:8000/docs`
- OpenAPI schema: `http://localhost:8000/openapi.json`

---

## Environment Configuration

Required environment variables in `.env`:
```
POSTGRES_HOST=localhost
POSTGRES_DB=myproject_db
POSTGRES_USER=myuser
POSTGRES_PASSWORD=mypassword
POSTGRES_EXPOSED_PORT=5432
SECRET_KEY=your-jwt-secret-key
```

---

## Deployment

Ready for deployment on aidriatic.com using Docker and AWS EC2.
Configure CORS origins and security settings for production use.