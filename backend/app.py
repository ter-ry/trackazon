
import os
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import subprocess
import json
import pandas as pd
from monitor import schedule_monitoring, latest_scrape_data

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRAPER_DIR = os.path.join(BASE_DIR, "scraper")
asin_file = os.path.join(SCRAPER_DIR, "input_asins.json")
output_file = os.path.join(SCRAPER_DIR, "output.json")
monitor_csv = os.path.join(BASE_DIR, "backend", "data", "monitor.csv")

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.json
    asins = data.get("asins", [])
    if not asins:
        return jsonify({"error": "No ASINs provided"}), 400

    if os.path.exists(asin_file):
        os.remove(asin_file)
    if os.path.exists(output_file):
        os.remove(output_file)

    with open(asin_file, "w") as f:
        json.dump(asins, f)

    try:
        subprocess.run(["scrapy", "crawl", "asin_spider"], cwd=SCRAPER_DIR, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Scraper failed", "details": str(e)}), 500

    if not os.path.exists(output_file):
        return jsonify({"error": "No output file found"}), 500

    with open(output_file, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    os.remove(asin_file)
    os.remove(output_file)

    return jsonify(scraped_data)

@app.route("/monitor/start", methods=["POST"])
def start_monitor():
    data = request.form or request.json
    interval = int(data.get("interval", 6))
    duration = int(data.get("duration", 1))
    asins = []

    if "file" in request.files:
        file = request.files["file"]
        df = pd.read_csv(file)
        df.columns = [col.strip().upper() for col in df.columns]
        if "ASIN" not in df.columns:
            return jsonify({"error": "CSV must contain an 'ASIN' column"}), 400
        asins = df["ASIN"].dropna().astype(str).str.strip().tolist()
    elif "asins" in data:
        asins = [x.strip() for x in data.get("asins").split(",")]

    if not asins:
        return jsonify({"error": "No ASINs provided"}), 400

    schedule_monitoring(asins, interval, duration)
    return jsonify({"status": "monitoring scheduled"})

@app.route("/monitor/current", methods=["GET"])
def get_latest_data():
    return jsonify(latest_scrape_data())

@app.route("/monitor/download", methods=["GET"])
def download_monitor_csv():
    if os.path.exists(monitor_csv):
        return send_file(monitor_csv, as_attachment=True)
    return jsonify({"error": "CSV file not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
