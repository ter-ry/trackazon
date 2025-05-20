
# 🛒 Trackazon — Amazon ASIN Analyzer

Trackazon is a full-stack web tool that scrapes and analyzes live product data from Amazon using ASINs. It includes tools for real-time lookup, scheduled monitoring, and visual analysis (coming soon).

---

## 🔧 Features

- Real-time ASIN lookup
- Scheduled monitoring with CSV export
- Full product data: price, rating, category, rank, image
- Responsive UI with Tailwind CSS
- Progress bar, loading states, and CSV download
- Fully local — no API cost, no cloud backend
- Built with Flask, Scrapy, HTML/JS

---

## 💻 Live Demo

> Open `frontend/index.html` or `frontend/monitor.html` in your browser.

📌 Make sure the Flask backend is running at `http://localhost:5000`.

---

## 🔍 Part 1 – ASIN Lookup Tool

### 🧠 What It Does

- Enter one or multiple ASINs (comma-separated)
- Real-time scraping from Amazon using Scrapy + Flask
- Extracts:
  - Title, price
  - Rating and review count
  - Main & sub category + best seller ranks
  - Product image
- Displays results in a sortable, responsive table
- Fully local, no API cost or third-party tools

### 🚀 How to Run

```bash
cd backend
pip install -r requirements.txt
python app.py
```

- Then open `frontend/index.html` in your browser
- It connects to `http://localhost:5000`

✅ You're ready to lookup any ASIN live.

---

## ⏰ Part 2 – Scheduled Monitoring Tool

### 🧠 What It Does

- Schedule repeated scraping of ASINs over time
- Choose:
  - Scrape interval (1h, 6h, 24h)
  - Duration (1, 3, 7 days)
- Upload ASINs via CSV or enter manually
- Results saved to `monitor.csv` with timestamps
- Download CSV directly via UI
- Fully local (no login or cloud hosting)

### 📁 CSV Format

Your `.csv` must include a column named `ASIN`, like this:

```csv
ASIN
B08N5WRWNW
B0C1234567
```

### 🚀 How to Run

```bash
cd backend
python app.py
```

- Then open `frontend/monitor.html` in your browser
- Use the form to submit ASINs and begin monitoring
- Once the first scrape finishes, data will appear and can be exported

---

## 🗂 Folder Structure

```
backend/    → Flask API and monitoring scheduler
scraper/    → Scrapy spider for Amazon product data
frontend/   → HTML/CSS/JS files (index.html and monitor.html)
docs/       → Screenshots or GitHub Pages static assets
README.md   → Project overview and usage guide
```

---

## ⚠️ Notes

- Works best with ASINs from **amazon.ca**
- **amazon.com** ASINs may differ or return 404
- Requires Python 3.8–3.12 for Scrapy compatibility
- Backend must remain running for scheduled monitoring

---

## 📦 Project Progress

| Phase     | Feature                               | Status       |
|-----------|----------------------------------------|--------------|
| ✅ Part 1 | ASIN Lookup Tool                        | Complete     |
| ✅ Part 2 | Scheduled Monitoring + CSV Export       | Complete     |
| ⏳ Part 3 | Interactive Price & Rating Dashboard    | Coming Soon  |

---

## 🙏 Thank You

If you find this project useful, feel free to ⭐ the repo or share feedback!  
Contributions and ideas welcome — just open an issue or message me.
