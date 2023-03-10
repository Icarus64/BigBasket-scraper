import scrapy
import asyncio
from pyppeteer import launch


class ShampooDataSpider(scrapy.Spider):
    name = "shampoo_data"
    start_urls = ["https://www.flipkart.com/head-shoulders-smooth-silky-anti-dandruff-shampoo-softer-smoother-hair/p/itm4d1d0a0d5e49b?pid=SMPFYG2TYVHGJZB2&lid=LSTSMPFYG2TYVHGJZB2TJOQAP&marketplace=FLIPKART&q=shampoo&store=g9b%2Flcf%2Fqqm%2Ft36&srno=s_1_6&otracker=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_ps&otracker1=AS_QueryStore_OrganicAutoSuggest_1_4_na_na_ps&fm=search-autosuggest&iid=3b9b5dbf-a29a-48e9-83b2-952e3ca42e0e.SMPFYG2TYVHGJZB2.SEARCH&ppt=sp&ppn=sp&ssid=rl1chv7y1s0000001678433058028&qH=186764a607df448c"]

    async def parse(self, response):
        # Launch a new browser instance
        browser = await launch(headless=True)
        page = await browser.newPage()

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
        await browser.close()

        # Create a dictionary of the scraped data
        data = {
            'brand_name': brand_name,
            'product_name': product_name.strip(),
            'price': price.strip(),
            'quantity_options': quantity_options,
            'description': description.strip(),
        }

        yield data
