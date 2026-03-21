# 🚀 VDP URL Scraper — Deployment Guide

This guide explains how to run the Django + Scrapy application locally.

NOTE: For production deployment or EC2, please refer to guides for:

* Gunicorn + Nginx
* Systemd services and timers
* Production-ready cron jobs

It covers:

* Installation
* Environment variables
* Django setup
* Running Scrapy spiders
* Cron scheduling
* Logging

## 1. 📁 Project Structure

```
vdp-urls-scraper/
├── fixtures/               # Initial Django data (users, projects, spiders, etc.)
├── logs/                   # Log files for spider runs
├── project/                # Main Django app (models, views, admin, API, templates)
├── scrapebucket/           # Scrapy project (settings, spiders, pipelines, utils)
│   ├── spiders/            # All spider definitions (~30+ spiders)
│   ├── spider_helpers/     # Selenium/Playwright helpers and URL parsing tools
│   └── runspider.py        # Standalone spider runner for Scrapy
├── static/                 # Static files (CSS, JS, images)
├── users/                  # Authentication, profiles & user-related templates
├── webscraping/            # Django project core (settings, wsgi, asgi)
├── requirements.txt        # Python dependencies
├── runspider.py            # Root-level runner for quick spider execution
├── scrapy.cfg              # Scrapy config
└── manage.py               # Django admin utility
```

## 2. 🧰 System Requirements
* Python 3.9+
* pip
* virtualenv (recommended)
* SQLite or PostgreSQL

## 3. 🔽 Clone the Repository
```
git clone https://github.com/paultumabini/vdp-urls-scraper.git
cd vdp-urls-scraper
```

## 4. 🧪 Python Virtual Environment (bash)
Create venv

`python3 -m venv venv`

Activate

`source venv/bin/activate`

Install dependencies

`pip install -r requirements.txt`

## 5. 🔐 Environment Variables (.envars)

Create a file in your home directory:

`nano ~/.envars`

Example contents:
```
# Django
export DJANGO_SECRET_KEY="your-secret-key"
export DATABASE_URL="sqlite:///db.sqlite3"

# FTP server (required)
export AIM_FTP_HOST=""
export AIM_FTP_USER=""
export AIM_FTP_PASS=""

# AVAIM login (required)
export AVAIM_EMAIL=""
export AVAIM_PASS=""
```

Load the environment:

`source ~/.envars`

## 6. 🛠️ Django Setup (Local)

Run migrations

`venv/bin/python manage.py migrate`

Create superuser (optional)

`venv/bin/python manage.py createsuperuser`

Run Django development server

`venv/bin/python manage.py runserver`

## 7. 🕷️ Running Scrapy Spiders

All spiders are executed using the root spider runner:

`python webscraping/runspider.py -s <spider_name>`

Example:
```
venv/bin/python webscraping/runspider.py -s webstager
venv/bin/python webscraping/runspider.py -s lynxdigital
```

Run specific a site:

`scrapy crawl <spider_name> -a url=<url>`

Example:

`scrapy crawl tadvantage -a url=https://www.example.com/`


Logs will be saved in the `logs/` folder.

## 8. 📅 Scheduling Spiders with Cron

Create logs folder

`mkdir -p logs`

Edit crontab

`crontab -e`

Example cron configuration (run at 18:00)
```
SHELL=/bin/bash

ENVS=~/.envars
SCRAPE_DIR=/path/to/vdp-urls-scraper
PYTHON=$SCRAPE_DIR/venv/bin/python
LOG_DIR=$SCRAPE_DIR/logs
DATE_CMD="+%Y_%m_%d"

# Ensure logs folder exists
1 0 * * * mkdir -p $LOG_DIR

# Spiders
0 18 * * * . $ENVS && $PYTHON $SCRAPE_DIR/webscraping/runspider.py -s webstager >> $LOG_DIR/webstager_$(date $DATE_CMD).log 2>&1
0 18 * * * . $ENVS && $PYTHON $SCRAPE_DIR/webscraping/runspider.py -s lynxdigital >> $LOG_DIR/lynxdigital_$(date $DATE_CMD).log 2>&1
```