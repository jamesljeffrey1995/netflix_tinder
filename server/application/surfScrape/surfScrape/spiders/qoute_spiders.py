import scrapy
import re
import time

class QuotesSpider(scrapy.Spider):
    name = "quotes"
    global i
    i = 0
    url = []
    global movie_list
    movie_list = {"Test","Test2"}
    while i != 1000:
        url.append("https://reelgood.com/source/netflix?offset="+str(i))
        i +=50
    start_urls = url
    def parse(self, response):
        for quote in response.css('table.css-1179hly'):
            movie_list.add(re.sub("<.*?>", "" ,str(quote.css('td.css-1u7zfla.e126mwsw1').getall())))
        yield{"movies":movie_list}
