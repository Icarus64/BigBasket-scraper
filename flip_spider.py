import json
import asyncio
from pyppeteer import launch

urls = []
with open('./flipkart_links.json', 'r') as file:
    for item in json.load(file):
        for link in item['links']:
            urls.append(link)

data = []

async def crawler():
    browser = await launch(headless=True)
    for link in urls:
        page = await browser.newPage()

        # Navigate to the product page
        await page.goto(link)

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
            item['price'] = await product_div.querySelectorEval('div._30jeq3._16Jk6d', 'el => el.textContent')

        # Close the browser instance
        await page.close()

        data.append({
            'brand_name': brand_name,
            'product_name': product_name.strip(),
            'price': price.strip(),
            'rating': rating,
            'ratings_count': ratings_count,
            'reviews_count': reviews_count,
            'quantity_options': quantity_options,
            'description': description.strip(),
        })

        await asyncio.sleep(3)
    
    await browser.close()

asyncio.run(crawler())
with open('./flip_data.json', 'w') as file:
    json.dump(data, file)