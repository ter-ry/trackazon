import scrapy
from scrapy import signals
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from collections import Counter
import datetime
import re
from ..items import ToolItem

class DailyASINSpider(scrapy.Spider):
    name = "DailyASINSpider"

    def __init__(self, *args, **kwargs):
        super(DailyASINSpider, self).__init__(*args, **kwargs)
        self.engine = create_engine('mysql+mysqlconnector://if0_35718472:chelseachelsea924@sql302.infinityfree.com/if0_35718472_Amasight')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def start_requests(self):
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT asin FROM public.input"))
            unique_set = set()

            for row in result:
                asin = row[0]
                if asin not in unique_set:
                    unique_set.add(asin)
                    url = f"https://www.amazon.com/dp/{asin}"
                    yield scrapy.Request(url=url, dont_filter=True, callback=self.parse, meta={'asin': asin})

    def parse(self, response):
        items = ToolItem()

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        asin = response.meta['asin']
        data_rows = []
                                        
        def test(s):
            for item in s:
                if item.strip().startswith("#"):
                    return str(item)
            return None

        def get_rank(s):
            for item in s:
                if item.strip().startswith("#"):
                    match = re.search(r'(\d+,)*\d+', item)
                    if match:
                        return int(match.group(0).replace(',', ''))
            return None
        
        def most_common(s):
            counts = Counter(s)
            return counts.most_common(1)[0][0]

        price1 = response.xpath(".//span[@class='a-offscreen']/text()").getall()
        price2 = most_common(price1)
        price = float(price2.replace("$", ""))

        noOfRatings1 = response.xpath(".//div[@id='averageCustomerReviews']/span[3]/a[1]/span[1]").get()
        if noOfRatings1:
            noOfRatings = int(''.join(filter(str.isdigit, noOfRatings1.strip())))
        else:
            noOfRatings = None

        rating1 = response.xpath(".//div[@id='averageCustomerReviews']/span[1]/span[1]/span[1]/a[1]/span[1]/text()").get()
        if rating1:
            rating1 = rating1.strip()
            rating = float(rating1)
        else:
            rating = None

        bsr_list = response.xpath(".//div[@id='detailBulletsWrapper_feature_div']/ul[1]/li[1]/span[1]/text()").getall()
        bsr_list1 = response.xpath(".//th[contains(text(), 'Best Sellers Rank')]/following-sibling::td/span/span[1]/text()").getall()

        bsr = get_rank(bsr_list)
        bsrtest = test(bsr_list)
        if bsrtest is None:
            bsr = get_rank(bsr_list1)
            bsrtest = test(bsr_list1)

        new_row = {'date': current_date, 'asin': asin, 'price': price, 'no_of_ratings': noOfRatings, 'rating': rating, 'best_sellers_rank': bsr}
        data_rows.append(new_row)

        items["data_rows"] = data_rows

        try:
            # Insert new data into the table
            for row in items['data_rows']:
                self.session.execute(text(f"INSERT INTO asin_info (date, asin, price, no_of_ratings, rating, best_sellers_rank) VALUES (:date, :asin, :price, :no_of_ratings, :rating, :best_sellers_rank)"), row)
            self.session.commit()

        except Exception as e:
            self.session.rollback()

        yield items

    @classmethod
    def spider_closed(cls, spider):
        if hasattr(spider, 'session'):
            spider.session.close()
        if hasattr(spider, 'engine'):
            spider.engine.dispose()

from scrapy.signalmanager import dispatcher
dispatcher.connect(DailyASINSpider.spider_closed, signal=signals.spider_closed)

