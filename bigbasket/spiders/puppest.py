import asyncio
import scrapy
from pyppeteer import launch


class PuppestSpider(scrapy.Spider):
    name = "puppest"
    allowed_domains = ["www.bigbasket.com"]
    start_urls = ["https://www.bigbasket.com/ps/?q=shampoo"]

    async def scrape(self, url):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.goto(url)
        body = await page.content()
        await browser.close()
        return body

    async def parse(self, response):
        page_content = await self.scrape(response.url)
        selector = scrapy.Selector(text=page_content)
        for product in selector.css('div[qa="product"]'):
            product_name = product.css('div[qa="product_name"] a::text').get()
            actual_price = product.css('span.mp-price.ng-scope span::text').get()
            discounted_price = product.css('span.discnt-price span::text').get()
            yield {
                'product_name': product_name.strip() if product_name else None,
                'actual_price': actual_price.strip() if actual_price else None,
                'discounted_price': discounted_price.strip() if discounted_price else None,
            }
