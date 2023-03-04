import scrapy
from pyppeteer import launch


class PuppestSpider(scrapy.Spider):
    name = "puppest"
    allowed_domains = ["www.bigbasket.com"]
    start_urls = ["https://www.bigbasket.com/ps/?q=mobiles"]

    async def scrape(self, url):
        browser = await launch(headless=True)
        page = await browser.newPage()
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3')
        await page.goto(url)

        # Click the 'show more' button and wait for navigation
        await page.click('button[ng-click="vm.pagginator.showmorepage()"]')
        await page.waitForNavigation(waitUntil='domcontentloaded')

        body = await page.content()
        await browser.close()
        return body

    async def parse(self, response):
        page_content = await self.scrape(response.url)
        selector = scrapy.Selector(text=page_content)
        for product in selector.css('div[qa="product"]'):
            product_name = product.css('div[qa="product_name"] a::text').get()
            actual_price = product.css(
                'span.mp-price.ng-scope span::text').get()
            discounted_price = product.css(
                'span.discnt-price span::text').get()
            yield {
                'product_name': product_name.strip() if product_name else None,
                'actual_price': actual_price.strip() if actual_price else None,
                'discounted_price': discounted_price.strip() if discounted_price else None,
            }
