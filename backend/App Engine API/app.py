from flask import Flask, request, jsonify  # Import 'request' correctly here
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://retool:ERcUMAHu3B0k@ep-ancient-wildflower-190949.us-west-2.retooldb.com/retool?sslmode=require'

db = SQLAlchemy(app)

# Data Structure
class ProductData(db.Model):
    __tablename__ = 'product_data'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    asin = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    main_category_rank = db.Column(db.Integer, nullable=True)
    sub_category_rank = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Float, nullable=True)
    no_of_ratings = db.Column(db.Integer, nullable=True)
    image = db.Column(db.String(255), nullable=True)

# Get Data from Database
@app.route('/api/data', methods=['GET'])
def get_data():
    asin_list = request.args.getlist('asins')
    days = int(request.args.get('days', 7))
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    if not asin_list:
        return jsonify({'error': 'No ASINs provided'}), 400
    
    results = ProductData.query.filter(
            ProductData.asin.in_(asin_list),
            ProductData.date >= start_date,
            ProductData.date <= end_date
        ).all()
    
    data_list = []
    for result in results:
        data_list.append({
            'date': result.date.strftime('%Y-%m-%d'),
            'asin': result.asin,
            'price': result.price,
            'main_category_rank': result.main_category_rank,
            'sub_category_rank': result.sub_category_rank,
            'rating': result.rating,
            'no_of_ratings': result.no_of_ratings,
            'image': result.image
        })
    
    return jsonify(data_list)

# Call API in VM to run Scrapy Spider
@app.route('/api/run_spider', methods=['POST'])
def run_spider():
    vm_flask_endpoint = "http://34.92.112.237:8080/run_spider"
    spider_details = request.get_json()
    asins = spider_details.get('asins')

    if not spider_details:
        return jsonify({"status": "error", "message": "No data provided"}), 400
    
    response = requests.post(vm_flask_endpoint, json={'spider_name': 'SearchEngine', 'asins': asins})
    return jsonify({"status": "success", "message": "Spider is running"}), response.status_code

@app.route('/api/status/<job_id>', methods=['POST'])
def update_status(job_id):
    status_message = request.json.get('status', 'No status provided')
    return jsonify({"job_id": job_id, "status": "updated", "message": status_message})

scraped_data = []

@app.route('/api/store_data', methods=['POST'])
def store_data():
    global scraped_data
    data = request.json.get('data')
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided'}), 400

    scraped_data = data
    return jsonify({'status': 'success', 'message': 'Data stored successfully'}), 200

@app.route('/api/send_data', methods=['GET'])
def send_data():
    global scraped_data
    if not scraped_data:
        return jsonify({"status": "error", "message": "No data available"}), 404
    try:
        return jsonify(scraped_data), 200
    finally:
        scraped_data = []

@app.route('/api/data_status', methods=['GET'])
def data_status():
    return jsonify({'isDataReady': bool(scraped_data)})

if __name__ == '__main__':
    app.run(debug=True)