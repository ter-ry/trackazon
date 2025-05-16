import scrapy
import datetime
import re
import json
from collections import Counter

class Test(scrapy.Spider):
    name = "Test"

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self.asins = ["B00IJ0ALYS", "B001ARYU58"]
        self.results = []

    def start_requests(self):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.google.com/"
        }

        for asin in self.asins:
            url = f"https://www.amazon.com/dp/{asin.strip()}"
            yield scrapy.Request(url=url, headers=headers, callback=self.parse, meta={'asin': asin})

    def parse(self, response):
        def clean_string(s):
            s = s.strip()
            return re.sub(r'\s+', ' ', s)

        def remove_html_tags_and_clean(text):
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\(See Top 100 in [^)]+\)', '', text)
            text = text.replace('&amp;', '&')
            return text.strip()

        def extract_categories_and_rankings(text):
            text = remove_html_tags_and_clean(text)
            pattern = r'#(\d{1,3}(?:,\d{3})*) in ([^#]+)'
            matches = re.findall(pattern, text)

            main_category_rank = int(matches[0][0].replace(',', '')) if matches else None
            main_category = matches[0][1].strip() if matches else None
            sub_category_rank = int(matches[1][0].replace(',', '')) if len(matches) > 1 else None
            sub_category = matches[1][1].strip() if len(matches) > 1 else None

            return {
                'main_category': main_category,
                'main_category_rank': main_category_rank,
                'sub_category': sub_category,
                'sub_category_rank': sub_category_rank,
            }

        def most_common(lst):
            return Counter(lst).most_common(1)[0][0] if lst else None

        asin = response.meta['asin']
        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Title
        name = clean_string(response.xpath(".//*[@id='productTitle']/text()").get() or "")

        # About
        about = response.xpath(".//div[@id='feature-bullets']//span[@class='a-list-item']/text()").getall()
        if not about:
            about = response.xpath("//ul[contains(@class, 'a-unordered-list') and contains(@class, 'a-vertical')]//span[@class='a-list-item a-size-base a-color-base']/text()").getall()
        about = [item.strip() for item in about if item.strip()]

        # Best Sellers Rank
        rank_text = response.xpath(".//th[contains(text(), 'Best Sellers Rank')]/following-sibling::td").get()
        if not rank_text:
            rank_text = response.xpath(".//div[@id='detailBulletsWrapper_feature_div']/ul[1]/li[1]").get()
        if not rank_text:
            rank_text = response.xpath(".//span[contains(text(), 'Best Sellers Rank:')]/following-sibling::text()[1]").get()

        rank_data = extract_categories_and_rankings(rank_text) if rank_text else {}

        # Price
        price_raw = response.xpath(".//span[@class='a-offscreen']/text()").getall()
        price_str = most_common(price_raw)
        price = float(price_str.replace("$", "")) if price_str else None

        # Ratings count
        ratings_text = response.xpath(".//div[@id='averageCustomerReviews']/span[3]/a[1]/span[1]/text()").get()
        no_of_ratings = int(''.join(filter(str.isdigit, ratings_text))) if ratings_text else None

        # Star rating
        rating_str = response.xpath(".//*[@id='acrPopover']/span[1]/a/span/text()").get()
        rating = float(rating_str.strip()) if rating_str else None

        # Image
        image = response.xpath(".//div[@id='imgTagWrapperId']/img/@src").get()

        product_data = {
            "date": current_date,
            "asin": asin,
            "name": name,
            "about": about,
            "main_category": rank_data.get("main_category"),
            "main_category_rank": rank_data.get("main_category_rank"),
            "sub_category": rank_data.get("sub_category"),
            "sub_category_rank": rank_data.get("sub_category_rank"),
            "price": price,
            "no_of_ratings": no_of_ratings,
            "rating": rating,
            "image": image
        }

        print(json.dumps(product_data, indent=2, ensure_ascii=False))
