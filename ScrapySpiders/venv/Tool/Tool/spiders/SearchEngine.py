import scrapy
from scrapy import signals
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from collections import Counter
import datetime
import re
import requests
from ..items import ToolItem
import logging

class SearchEngine(scrapy.Spider):
    name = "SearchEngine"

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(SearchEngine, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.closed, signal=signals.spider_closed)
        return spider

    def __init__(self, job_id=None, asins=None, *args, **kwargs):
        super(SearchEngine, self).__init__(*args, **kwargs)
        self.job_id = job_id or 'default_job_id'
        self.results = []
        self.asins = asins.split(',') if asins else []

    def start_requests(self):
        for asin in self.asins:
            url = f"https://www.amazon.com/dp/{asin.strip()}"
            yield scrapy.Request(url=url, dont_filter=True, callback=self.parse, meta={'asin': asin})

    def parse(self, response):
        items = ToolItem()

        current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        asin = response.meta['asin']
        data_rows = []
                                                
        def most_common(s):
            counts = Counter(s)
            return counts.most_common(1)[0][0]
        
        def clean_string(s):
            s = s.strip()
            s = re.sub(r'\s+', ' ', s)
            return s

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

        #Name
        name = response.xpath(".//*[@id='productTitle']/text()").get()
        name = clean_string(name)

        #About
        about = response.xpath(".//div[@id='feature-bullets']//span[@class='a-list-item']/text()").getall()
        if not about:
            about = response.xpath(".//*[@id='productFactsDesktopExpander']/div[1]/ul/li").getall()
            about = [remove_html_tags_and_clean(item) for item in about]

        about = [item.strip() for item in about if item.strip()]

        #Categories + Ranks
        rank_text = response.xpath(".//th[contains(text(), 'Best Sellers Rank')]/following-sibling::td").get()
        if not rank_text:
            rank_text = response.xpath(".//div[@id='detailBulletsWrapper_feature_div']/ul[1]/li[1]").get()

        if not rank_text:
            main_category = None
            main_category_rank = None
            sub_category = None
            sub_category_rank = None
        else:
            rank_data = extract_categories_and_rankings(rank_text)
            main_category = rank_data['main_category']
            main_category_rank = rank_data['main_category_rank']
            sub_category = rank_data['sub_category']
            sub_category_rank = rank_data['sub_category_rank']

        #Price
        price1 = response.xpath(".//span[@class='a-offscreen']/text()").getall()
        price2 = most_common(price1)
        price = float(price2.replace("$", ""))

        #No of Ratings
        noOfRatings1 = response.xpath(".//div[@id='averageCustomerReviews']/span[3]/a[1]/span[1]").get()
        if noOfRatings1:
            noOfRatings = int(''.join(filter(str.isdigit, noOfRatings1.strip())))
        else:
            noOfRatings = None

        #Rating
        rating1 = response.xpath(".//*[@id='acrPopover']/span[1]/a/span/text()").get()
        if rating1:
            rating1 = rating1.strip()
            rating = float(rating1)
        else:
            rating = None

        #Image
        image = response.xpath(".//div[@id='imgTagWrapperId']/img/@src").get()

        new_row = {'date': current_date, 'asin': asin, 'name': name, 'about': about, 'category': main_category, 'sub_category': sub_category, 'main_category_rank': main_category_rank, 'sub_category_rank': sub_category_rank, 'price': price, 'no_of_ratings': noOfRatings, 'rating': rating, 'image': image}
        self.results.append(new_row)
        self.log(f'Data: {new_row}')


    def closed(self, reason):
        self.logger.info(f"Spider closed because {reason}")
        self.send_results()

    def send_results(self):
        url = 'http://34.92.112.237:8080/receive_data'
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, json={'data': self.results}, headers=headers)
        if response.status_code == 200:
            self.log('Data successfully sent to the API.')
        else:
            self.log(f'Failed to send data to the API. Status: {response.status_code}, Body: {response.text}')