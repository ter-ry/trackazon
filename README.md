# 🛒 Amazon Analyzer — ASIN Lookup Tool

This is Part 1 of the **Amazon Analyzer Project**, a full-stack web tool that scrapes and analyzes live product data from Amazon using ASINs.

> 🔍 Lookup any Amazon ASIN to retrieve detailed product info in real-time — directly from the source.

---

## 🔧 Features

- Enter multiple ASINs (comma-separated)
- Real-time scraping with Scrapy and Flask
- Retrieves:
  - Product title and price
  - Ratings and review count
  - Best seller ranks (main and sub categories)
  - Product image
- Sortable, responsive table (built with Tailwind CSS)
- Progress bar and loading indicator
- Fully local tool (no API cost)

---

## 💻 Live Demo

![screenshot](docs/screenshot.png) <!-- Add your real screenshot later -->

(Or [watch demo video](#) if backend isn’t running)

---

## 🚀 How to Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/your-username/amazon-analyzer.git
cd amazon-analyzer

### 2. Set up Python backend
```bash
cd backend
pip install -r requirements.txt
python app.py

### 3. Launch the frontend
Open docs/index.html in any browser
It connects to http://localhost:5000 by default
✅ You’re ready to scrape product data live.


🗂 Folder Structure
backend/    → Flask API that triggers the spider
scraper/    → Scrapy project for Amazon scraping
docs/       → Frontend interface (GitHub Pages ready)
README.md   → You are here


⚠️ Notes
The backend must be running locally for the tool to work.
Works best with ASINs from amazon.ca
amazon.com ASINs may differ or return 404
Ensure your environment uses Python 3.8–3.12 for Scrapy compatibility


📦 Roadmap
Phase        Feature	                              Status
✅ Part 1   ASIN Lookup Tool	                        Complete
🔄 Part 2   Scheduled Monitoring + CSV Export	     In Progress
⏳ Part 3   Interactive Price & Rating Dashboard	    Coming Soon


⭐️ Like This Project?
Give it a ⭐ on GitHub or connect with me — feedback and collaboration welcome!