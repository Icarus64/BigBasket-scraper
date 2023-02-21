import scrapy
import time


class ShampooSpiderSpider(scrapy.Spider):
    name = "shampoo_spider"
    allowed_domains = ["www.bigbasket.com"]
    start_urls = [
        "https://www.bigbasket.com/ps/?q=shampoo"]

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, dont_filter=True)
            time.sleep(3)  # Add a 5 second delay between requests

    def parse(self, response):
        
        with open("./dump.txt", "wb") as file:
            file.write(response.body)

        for item in response.css('div.items > *'):
            yield {
                'name': item.css('a::text').get(),
                'price': item.css('p:nth-child(1) > span:nth-child(1)::text').get(),
                'quantity': item.css('p:nth-child(1) > span:nth-child(2)::text').get(),
            }
