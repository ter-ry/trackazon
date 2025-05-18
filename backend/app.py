from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import os
import datetime

app = Flask(__name__)
CORS(app)

@app.route("/lookup", methods=["POST"])
def lookup():
    data = request.get_json()
    asins = data.get("asins", [])

    if not asins:
        return jsonify({"error": "No ASINs provided"}), 400

    asin_file = "backend/scraper/input_asins.json"
    output_file = "backend/scraper/output.json"

    # Write ASINs to file
    with open(asin_file, "w", encoding="utf-8") as f:
        json.dump(asins, f)

    # Run the Scrapy spider inside scraper folder
    result = subprocess.run(
        ["scrapy", "crawl", "asin", "-a", f"asins={','.join(asins)}"],
        cwd="backend/scraper"
    )

    if result.returncode != 0:
        return jsonify({"error": "Scraping failed"}), 500

    # Read and return scraped data
    try:
        with open(output_file, "r", encoding="utf-8") as f:
            scraped_data = json.load(f)
        return jsonify(scraped_data)
    except Exception as e:
        return jsonify({"error": f"Failed to read output: {str(e)}"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
