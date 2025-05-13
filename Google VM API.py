import subprocess
import logging
import time
from flask import Flask, request, jsonify
import logging
import requests
import re

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/run_spider', methods=['POST'])
def run_spider():
    request_received_time = time.time()
    app.logger.debug("Request received")

    spider_details = request.json
    spider_name = spider_details.get('spider_name', 'SearchEngine')
    job_id = spider_details.get('job_id', 'default_job_id')
    
    asins = spider_details.get('asins', [])
    cleaned_asins = [re.sub(r'[^\x00-\x7F]+', '', asin) for asin in asins]
    asins_arg = f"-a asins=\"{','.join(cleaned_asins)}\"" if cleaned_asins else ""
    
    command = f"cd ../Scrapy_Spiders/venv/Tool/Tool && scrapy crawl {spider_name} {asins_arg}"

    app.logger.debug(f"Command prepared: {command}")
    command_preparation_time = time.time()

    try:
        app.logger.debug(f"Starting subprocess for Scrapy command...")
        process_start_time = time.time()
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        process_end_time = time.time()

        app.logger.debug(f"Subprocess started at {process_start_time - request_received_time:.4f} seconds")
        app.logger.debug(f"Command output: {stdout.decode()}")
        app.logger.debug(f"Command error: {stderr.decode()}")
        app.logger.debug(f"Subprocess runtime: {process_end_time - process_start_time:.4f} seconds")

        if process.returncode == 0:
            app.logger.debug("Spider ran successfully")
            return jsonify({
                "status": "success",
                "message": f"Spider '{spider_name}' ran successfully",
                "output": stdout.decode(),
                "process_time": process_end_time - process_start_time,
                "total_time": process_end_time - request_received_time
            }), 200
        else:
            app.logger.error(f"Spider failed to run: {stderr.decode()}")
            return jsonify({
                "status": "error",
                "message": f"Failed to start spider '{spider_name}'",
                "error": stderr.decode(),
                "process_time": process_end_time - process_start_time,
                "total_time": process_end_time - request_received_time
            }), 500
    except Exception as e:
        error_time = time.time()
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An error occurred during the subprocess execution",
            "error": str(e),
            "process_time": error_time - process_start_time,
            "total_time": error_time - request_received_time
        }), 500

@app.route('/receive_data', methods=['POST'])
def receive_data():
    data = request.json.get('data', [])
    if not data:
        app.logger.error("No data received")
        return jsonify({"status": "error", "message": "No data received"}), 400

    app_engine_url = 'https://coastal-science-419508.df.r.appspot.com/api/store_data'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(app_engine_url, json={'data': data}, headers=headers)
    
    if response.status_code != 200:
        app.logger.error(f"Failed to forward data to App Engine: {response.text}")
        return jsonify({"status": "error", "message": "Failed to forward data to App Engine", "details": response.text}), 500

    app.logger.info("Data forwarded to App Engine successfully")
    return jsonify({"status": "success", "message": "Data forwarded to App Engine successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)