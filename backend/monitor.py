
import os
import json
import csv
import datetime
import subprocess
from apscheduler.schedulers.background import BackgroundScheduler

monitor_data = []
scheduler = BackgroundScheduler()
scheduler.start()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPER_DIR = os.path.join(BASE_DIR, "scraper")
ASIN_FILE = os.path.join(SCRAPER_DIR, "input_asins.json")
OUTPUT_FILE = os.path.join(SCRAPER_DIR, "output.json")
CSV_PATH = os.path.join(BASE_DIR, "backend", "data", "monitor.csv")

def run_real_scraper(asins):
    os.makedirs(os.path.dirname(ASIN_FILE), exist_ok=True)
    with open(ASIN_FILE, "w") as f:
        json.dump(asins, f)
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    subprocess.run(["scrapy", "crawl", "asin_spider"], cwd=SCRAPER_DIR, check=True)
    if not os.path.exists(OUTPUT_FILE):
        return []
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_to_csv(data):
    os.makedirs(os.path.dirname(CSV_PATH), exist_ok=True)
    fieldnames = [
        "asin", "name", "price", "rating", "no_of_ratings",
        "main_category", "main_category_rank",
        "sub_category", "sub_category_rank", "image", "timestamp"
    ]

    filtered_data = [
        {k: v for k, v in item.items() if k in fieldnames} for item in data
    ]

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(filtered_data)
        print(f"[DEBUG] Writing {len(filtered_data)} records to monitor.csv")


def scrape_job(asins):
    global monitor_data
    try:
        data = run_real_scraper(asins)
        for item in data:
            item["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        monitor_data = data
        save_to_csv(monitor_data)
    except Exception as e:
        print("[ERROR] Scrape job failed:", e)

def schedule_monitoring(asins, interval_hours, duration_days):
    job_id = f"monitor_{datetime.datetime.now().timestamp()}"
    scrape_job(asins)
    scheduler.add_job(scrape_job, "interval", args=[asins], hours=interval_hours, id=job_id)
    scheduler.add_job(lambda: scheduler.remove_job(job_id), "date",
                      run_date=datetime.datetime.now() + datetime.timedelta(days=duration_days))

def latest_scrape_data():
    return monitor_data
