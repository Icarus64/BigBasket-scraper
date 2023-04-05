import scrapy
from scrapy import Request
import time


class FlipkartSpider(scrapy.Spider):
    name = "flipkart"
    base_url = "https://www.flipkart.com/search?q="
    pages = 5  # example number of pages to crawl

    def __init__(self, name=None, **kwargs):
        super().__init__(name, **kwargs)
        product = kwargs.get('product', 'shampoo')
        self.base_url = str(f"{self.base_url}{product}")
        self.pages = int(kwargs.get('pages', '1'))

    def start_requests(self):
        for page in range(1, self.pages+1):
            url = str(f"{self.base_url}&page={page}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
            yield Request(url, callback=self.parse, headers=headers)
            time.sleep(5)

    def parse(self, response):
        print(self.base_url)
        links = []
        base = 'https://www.flipkart.com'
        for div in response.css('div._4ddWXP'):
            link = div.css('a.s1Q9rs::attr(href)').get()
            links.append(base + link)
        yield {
            'links': links
        }
