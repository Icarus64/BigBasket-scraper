import scrapy
import asyncio
from pyppeteer import launch

class AProdDataSpider(scrapy.Spider):
    name = "a_prod_data"
    allowed_domains = ["www.amazon.in"]
    start_urls = [
        #"https://www.amazon.in/Clinic-Plus-Strong-Long-Shampoo/dp/B0933B5N19/ref=sr_1_6?keywords=shampoo&sr=8-6",
        #"https://www.amazon.in/LOreal-Paris-Total-Repair-Shampoo/dp/B08CSHBPD5/ref=sr_1_7?keywords=shampoo&sr=8-7&th=1",
        "https://www.amazon.in/Dabur-Vatika-Health-Shampoo-640/dp/B07QD5VR1L/ref=sr_1_8?keywords=shampoo&sr=8-8&th=1",
    ]

    browser = None

    def __init__(self, *args, **kwargs):
        super(AProdDataSpider, self).__init__(*args, **kwargs)
        self.loop = asyncio.get_event_loop()
        self.browser = self.loop.run_until_complete(launch(headless=True))

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers)

    async def parse(self, response):
        # Launch a new browser instance
        
        page = await self.browser.newPage()

        # Navigate to the product page
        await page.goto(response.url)

        #getting the product name
        try:
            product_name = await page.querySelectorEval('#productTitle', 'el => el.textContent')
        except:
            product_name = None

        #getting the product link
        product_link = response.url

        # finding the brand name
        brand_name = None
        overview_div = await page.querySelector('#productOverview_feature_div')
        trs = await overview_div.querySelectorAll('tr')
        for tr in trs:
            if "Brand" in await tr.querySelectorEval('span.a-size-base.a-text-bold', 'el => el.textContent'):
                brand_name = await tr.querySelectorEval('span.a-size-base.po-break-word', 'el => el.textContent')
                break
            

        #finding the MRP and price
        try:
            table = await page.querySelector('.a-lineitem.a-align-top')
            mrp_tr = await table.querySelector('tr:nth-child(1)')
            mrp = await mrp_tr.querySelectorEval('span.a-offscreen', 'el => el.textContent')
            price_tr = await table.querySelector('tr:nth-child(2)')
            price = await price_tr.querySelectorEval('span.a-offscreen', 'el => el.textContent')
        except:
            mrp = None
            price = None

        #Getting the product description
        desc_div = await page.querySelector("#productDescription")
        description = await desc_div.querySelectorEval('span', 'el => el.textContent')

        #Getting the product rating
        try:
            rate_span = await page.querySelector("#acrPopover")
            rating = await rate_span.querySelectorEval("span.a-size-base.a-color-base", "el => el.textContent")
        except:
            rating = None

        #Getting rating count
        ratings_count = await page.querySelectorEval("#acrCustomerReviewText", "el => el.textContent")

        #Getting review_count
        review_cont = await page.querySelector("#askATFLink")
        review_count = await review_cont.querySelectorEval('span.a-size-base', 'el => el.textContent')

        #Getting the quantity options
        quantity_options = []
        quantity_div = await page.querySelector("#tp-inline-twister-dim-values-container")
        q_li = await page.querySelectorAll("li")
        for li in q_li:
            try:
                quantity = await li.querySelectorEval('span.a-size-base.swatch-title-text-display.swatch-title-text', 'el => el.textContent')
            except:
                quantity = None
            
            try:
                qprice_span = await li.querySelector('#_price')
                qprice = await qprice_span.querySelectorEval('span.twisterSwatchPrice.a-size-base.a-color-base', 'el => el.textContent')
            except:
                qprice = None

            if quantity != None and qprice != None:
                quantity_options.append(
                    {
                        'quantity': quantity,
                        'price': qprice
                    }
                )


        #closing the browser
        await page.close()

        yield {
            'product_name': product_name.strip() if product_name else None,
            'product_link': product_link.strip(),
            'brand_name': brand_name if brand_name else None,
            'mrp': mrp.strip() if mrp else None,
            'price': price.strip() if price else None,
            'rating': rating.strip('() ') if rating else None,
            'ratings_count': ratings_count.strip() if ratings_count else None,
            'reviews_count': review_count.strip() if review_count else None,
            'quantity_options': quantity_options,
            'description': description if description else None
        }

