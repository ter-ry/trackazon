from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os

app = Flask(__name__)
CORS(app)

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    asins = data.get("asins", [])

    if not asins:
        return jsonify({"error": "No ASINs provided"}), 400

    asin_file = "scraper/input_asins.json"
    output_file = "scraper/output.json"

    # Save ASINs
    try:
        with open(asin_file, "w", encoding="utf-8") as f:
            json.dump(asins, f)
    except Exception as e:
        return jsonify({"error": f"Failed to write ASINs: {e}"}), 500

    # Run Scrapy spider
    result = subprocess.run(
        ["scrapy", "crawl", "asin"],
        cwd="scraper"
    )

    if result.returncode != 0:
        return jsonify({"error": "Scraping failed"}), 500

    # Load output
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            scraped_data = json.load(f)
        return jsonify(scraped_data)
    except Exception as e:
        return jsonify({"error": f"Failed to read output: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
