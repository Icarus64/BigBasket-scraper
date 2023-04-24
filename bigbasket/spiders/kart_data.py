import scrapy
import json
import asyncio
from pyppeteer import launch


class KartDataSpider(scrapy.Spider):
    name = "kart_data"
    allowed_domains = ["www.flipkart.com"]
    start_urls = []
    browser = None
    with open('./kart_links.json', 'r') as file:
        for item in json.load(file):
            for link in item['links']:
                start_urls.append(link)

    def __init__(self, *args, **kwargs):
        super(KartDataSpider, self).__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.browser = self.loop.run_until_complete(launch(headless=True))

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

        # Type the desired pin code and press enter
        input_field = await page.querySelector('input._36yFo0')
        await input_field.type('409999\n')

        # Press on the span tag with class _2P_LDn
        span_element = await page.querySelector('span._2P_LDn')
        await span_element.click()

        # Wait for the element with class _1SLzzw to appear
        await page.waitForSelector('div._1SLzzw')

        # Get the innerHTML of the div with class _1SLzzw and its children
        div_element = await page.querySelector('div.row._2WVRLm')
        delivery_code = await page.evaluate('(element) => element.innerHTML', div_element)

        # Get the rating, review count and rating count
        rating_div = await page.querySelector('div.gUuXy-._16VRIQ')
        if rating_div:
            rating = await rating_div.querySelectorEval('div._3LWZlK', 'el => el.textContent')
            rating_count_span = await rating_div.querySelector('span._2_R_DZ')
            if rating_count_span:
                spans = await rating_count_span.querySelectorAll('span')
                if len(spans) > 2:
                    ratings_count = await (await spans[1].getProperty('textContent')).jsonValue()
                    reviews_count = await (await spans[3].getProperty('textContent')).jsonValue()

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
            # item['price'] = await product_div.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')
            if product_div:
                item['price'] = await product_div.querySelectorEval('div._30jeq3._16Jk6d, div._2Tpdn3._1vevjr', 'el => el.textContent')
            else:
                item['price'] = None

        # Close the browser instance
        await page.close()
        await asyncio.sleep(1)

        # Create a dictionary of the scraped data
        data = {
            'brand_name': brand_name,
            'product_name': product_name.strip(),
            'price': price.strip(),
            'delivery_code': delivery_code,
            'rating': rating,
            'ratings_count': ratings_count,
            'reviews_count': reviews_count,
            'quantity_options': quantity_options,
            'description': description.strip(),
        }

        yield data
