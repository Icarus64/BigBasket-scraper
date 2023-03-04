import scrapy
from pyppeteer import launch
import asyncio


class basketSpider(scrapy.Spider):
    name = "basket"
    allowed_domains = ["www.bigbasket.com"]
    product = "conditioner"
    base_url = "https://www.bigbasket.com/ps/?q="+product+"#!page={}"
    start_urls = [base_url.format(1)]

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'output.json'
    }

    async def scrape(self, url):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        await page.goto(url)

        body = await page.content()
        await browser.close()
        return body

    async def parse(self, response):
        num_pages = 3  # set the upper limit for number of pages to scrape
        for page_num in range(1, num_pages+1):
            url = self.base_url.format(page_num)
            page_content = await self.scrape(url)
            selector = scrapy.Selector(text=page_content)
            for product in selector.css('div[qa="product"]'):
                product_name = product.css(
                    'div[qa="product_name"] a::text').get()
                actual_price = product.css(
                    'span.mp-price.ng-scope span::text').get()
                discounted_price = product.css(
                    'span.discnt-price span::text').get()
                if actual_price == None:
                    discounted_price = product.css(
                        'span.discnt-price span.ng-binding::text').get()
                yield {
                    'product_name': product_name.strip() if product_name else None,
                    'actual_price': actual_price.strip() if actual_price else None,
                    'discounted_price': discounted_price.strip() if discounted_price else None,
                }
            # add a delay of 3 seconds before making the next request
            await asyncio.sleep(3)
