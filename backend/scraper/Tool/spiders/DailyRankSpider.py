import scrapy
from scrapy import signals
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from collections import Counter
import datetime
from ..items import ToolItem

class DailyRankSpider(scrapy.Spider):
    name = "DailyRankSpider"
    max_pages = 2

    def __init__(self, *args, **kwargs):
        super(DailyRankSpider, self).__init__(*args, **kwargs)
        self.engine = create_engine('postgresql://retool:ERcUMAHu3B0k@ep-ancient-wildflower-190949.us-west-2.retooldb.com/retool?sslmode=require')
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def start_requests(self):
        with self.engine.connect() as connection:
            result = connection.execute(text("SELECT asin, keyword FROM public.input"))
            for row in result:
                url = f"https://www.amazon.com/s?k={row[1]}&page=1"
                yield scrapy.Request(url=url, dont_filter=True, callback=self.parse, meta={'asin': row[0], 'keyword': row[1], 'page': 1})

    def parse(self, response):
        items = ToolItem()
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        elements = response.xpath("//*[contains(@class, 'sg-col-4-of-24 sg-col-4-of-12 s-result-item s-asin sg-col-4-of-16 sg-col s-widget-spacing-small sg-col-4-of-20')]")
        data_asins = []
        i = (response.meta['page'] - 1) * 48 + 1
        resultfound = False
        asin = response.meta['asin']
        keyword = response.meta['keyword']

        for element in elements:
            data_asin = element.xpath("./@data-asin").get()
            if data_asin == asin:
                new_row = {'date': current_date, 'asin': asin, 'keyword': keyword, 'rank': i}
                data_asins.append(new_row)
                i=1
                resultfound = True
                break
            else:
                i+=1

        if resultfound == False:
            if response.meta['page'] < self.max_pages:
                next_page_url = f"https://www.amazon.com/s?k={response.meta['keyword']}&page={response.meta['page']+1}"
                yield scrapy.Request(url=next_page_url, dont_filter=True, callback=self.parse, meta={'asin': asin, 'keyword': keyword, 'page': response.meta['page']+1})
            else:
                new_row = {'date': current_date, 'asin': asin, 'keyword': keyword, 'rank': None}
                data_asins.append(new_row)

        items["data_rows"] = data_asins

        try:
            for row in items['data_rows']:
                self.session.execute(text(f"INSERT INTO rank (date, asin, keyword, rank) VALUES (:date, :asin, :keyword, :rank)"), row)
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
dispatcher.connect(DailyRankSpider.spider_closed, signal=signals.spider_closed)

