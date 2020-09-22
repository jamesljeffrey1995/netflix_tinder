import scrapy
import re

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = ["https://magicseaweed.com/Tynemouth-Longsands-Surf-Report/26/"]

    def parse(self, response):
        for quote in response.css('div.table-responsive-xs'):
            yield {
                'day': re.sub("<.*?>", "" ,str(quote.css('h6.nomargin.pull-left.heavy.table-header-title').getall())),
                'size': re.sub("<.*?>", "" ,str(quote.css('span.h3.font-sans-serif.heavy.nomargin.text-white').getall()))
            }
