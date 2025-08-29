#!/bin/bash

# Linux Setup Script for Adriatic Real Estate Monitor
set -e  # Exit on any error

echo "Starting Linux setup for Adriatic Real Estate Monitor..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. I'll install it for you."
    curl -LsSf https://astral.sh/uv/install.sh | sh

fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Docker/docker-compose is not installed. Please install Docker first."
    exit 1
fi

echo "Installing Python dependencies..."
uv sync

echo "Installing Playwright browsers..."
playwright install

echo "Starting Docker services..."
docker-compose up -d --force-recreate --remove-orphans

echo "Creating job_data directory..."
mkdir -p job_data

echo "Running initial setup..."
uv run scripts/initial_setup.py

echo "Setting up cron jobs..."

# Get the current directory (project root)
PROJECT_DIR=$(pwd)
UV_PATH=$(which uv)

# Create temporary crontab file
TEMP_CRON=$(mktemp)

# Get existing crontab (if any) and filter out our jobs
crontab -l 2>/dev/null | grep -v "adriatic-real-estate-monitor" > "$TEMP_CRON" || true

# Add our cron jobs with comments
cat >> "$TEMP_CRON" << EOF

# Adriatic Real Estate Monitor Jobs
# Daily script at midnight (00:00)
0 0 * * * cd $PROJECT_DIR && $UV_PATH run scripts/daily_script.py >> $PROJECT_DIR/logs/daily.log 2>&1
# Email script at 9 AM (09:00)  
0 9 * * * cd $PROJECT_DIR && $UV_PATH run scripts/send_email.py >> $PROJECT_DIR/logs/email.log 2>&1
EOF

# Install the new crontab
crontab "$TEMP_CRON"

# Clean up
rm "$TEMP_CRON"

echo "📝 Creating logs directory..."
mkdir -p logs

echo "✅ Setup completed successfully!"
echo ""
echo "📋 Summary:"
echo "  • Python dependencies installed"
echo "  • Playwright browsers installed" 
echo "  • Docker services started"
echo "  • job_data directory created"
echo "  • Initial setup completed"
echo "  • Cron jobs configured:"
echo "    - daily_script.py runs daily at 00:00"
echo "    - send_email.py runs daily at 09:00"
echo "  • Logs will be saved to: $PROJECT_DIR/logs/"
echo ""
echo "🔍 To verify cron jobs: crontab -l"
echo "📊 To check logs: tail -f logs/daily.log or tail -f logs/email.log"