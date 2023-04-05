import scrapy
import json
import asyncio
from pyppeteer import launch


class KartDataSpider(scrapy.Spider):
    name = "kart_data"
    allowed_domains = ["www.flipkart.com"]
    start_urls = []
    with open('./flipkart_links.json', 'r') as file:
        for item in json.load(file):
            for link in item['links']:
                start_urls.append(link)

    browser = None  # Declare browser variable as class variable

    async def start_requests(self):
        # Launch a new browser instance if not already created
        if not self.browser:
            self.browser = await launch(headless=True)

        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

        # Close the browser instance
        await self.browser.close()



    async def parse(self, response):
        
        page = await self.browser.newPage()

        # Navigate to the product page
        await page.goto(response.url)

        # Get the div tag with class="_1MR4o5"

        breadcrumb_divs = await page.querySelectorAll('div._1MR4o5 div')

        if len(breadcrumb_divs) >= 2:

            div_target = await page.querySelector('div._1MR4o5 div:nth-last-child(2)')

            brand_name = await div_target.querySelectorEval('a._2whKao', "el => el.textContent")
        else:
            brand_name = None

        # Get the div tag with class="aMaAEs"
        div_aMaAEs = await page.querySelector('div.aMaAEs')

        if div_aMaAEs:
            # Get the product name
            product_name = await div_aMaAEs.querySelectorEval('span.B_NuCI', 'el => el.textContent')

            # Get the price
            price = await div_aMaAEs.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')
        else:
            product_name = None
            price = None

        # Get the description
        description = await page.querySelectorEval('div._1mXcCf, div._1mXcCf.RmoJUa', 'el => el.textContent')

        quantity_options = []
        els = await page.querySelectorAll('a._1fGeJ5, a._1fGeJ5.PP89tw')
        for el in els:
            quantity_options.append({
                'quantity': await (await el.getProperty('textContent')).jsonValue(),
                'href': await (await el.getProperty('href')).jsonValue()
            })

        for item in quantity_options:
            await page.goto(item["href"], waitUntil='networkidle2', timeout=10000)
            product_div = await page.querySelector('div.aMaAEs')
            item['price'] = await product_div.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')

        # Close the browser instance
        await page.close()

        # Create a dictionary of the scraped data
        data = {
            'brand_name': brand_name,
            'product_name': product_name.strip(),
            'price': price.strip(),
            'quantity_options': quantity_options,
            'description': description.strip(),
        }

        await asyncio.sleep(3)
        yield data