import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json

app = Flask(__name__)
CORS(app)

# Calculate absolute paths to the scraper folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # project root
SCRAPER_DIR = os.path.join(BASE_DIR, "scraper")
asin_file = os.path.join(SCRAPER_DIR, "input_asins.json")
output_file = os.path.join(SCRAPER_DIR, "output.json")

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.json
    asins = data.get("asins", [])
    if not asins:
        return jsonify({"error": "No ASINs provided"}), 400

    # Clean up previous files
    if os.path.exists(asin_file):
        os.remove(asin_file)
    if os.path.exists(output_file):
        os.remove(output_file)

    # Save input ASINs
    with open(asin_file, "w") as f:
        json.dump(asins, f)

    # Run the spider
    try:
        subprocess.run(["scrapy", "crawl", "asin_spider"], cwd=SCRAPER_DIR, check=True)
    except subprocess.CalledProcessError as e:
        return jsonify({"error": "Scraper failed", "details": e.stderr}), 500

    # Read output
    if not os.path.exists(output_file):
        return jsonify({"error": "No output file found"}), 500

    with open(output_file, "r", encoding="utf-8") as f:
        scraped_data = json.load(f)

    # Clean up output if desired
    os.remove(asin_file)
    os.remove(output_file)

    return jsonify(scraped_data)

if __name__ == "__main__":
    app.run(debug=True)
