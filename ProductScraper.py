import json

import requests
from bs4 import BeautifulSoup


class Scraper:
    @staticmethod
    def fetch_item_html(url: str) -> str:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Refer': 'https://www.ebay.com/'
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text

    @staticmethod
    def filter_digits(text: str) -> float:
        return float(''.join([i.replace(',', '') for i in text if i.isdigit() or i == '.' or i == ',']).strip())

    def proceed_html(self, html: str, url: str) -> dict:
        item_info = {'url': url}
        soup = BeautifulSoup(html, 'html.parser')
        ship_elements = soup.select_one('div.vim.d-shipping-minview div.ux-labels-values__values-content div').select('span')

        element_mapping = {
            'name': soup.select_one('h1.x-item-title__mainTitle span'),
            'price': [soup.select_one('div.x-price-primary span'), soup.select_one('span.x-price-approx__price span')],
            'condition': soup.select_one('div.x-item-condition-text div span.clipped'),
            'img': soup.select('div.ux-image-carousel img'),
            'seller_name': soup.select_one('div.x-sellercard-atf__info__about-seller span'),
            'seller_url': soup.select_one('div.x-sellercard-atf__info__about-seller a'),
            'options': soup.select_one('select.x-msku__select-box'),
            'quantity_available': soup.select_one('div.d-quantity__availability.evo span'),
            'ship_price': [ship_elements[0], ship_elements[1]] if ship_elements else None
        }

        def process_price(prices):
            for price in prices:
                if price:
                    currency = price.text.split()[0].strip()
                    item_info[f'price_{currency}'] = self.filter_digits(price.text)

        def process_ship_price(prices):
            for price in prices:
                if 'not ship' in prices[0].text:
                    item_info['ship_price'] = 'N/A'
                else:
                    filtered = price.text.replace('(', '').replace(')', '').replace('approx', '').split()
                    item_info[f'ship_price_{filtered[0]}'] = self.filter_digits(filtered[1])

        def process_quantity(quantity):
            item_info['quantity_available'] = self.filter_digits(quantity.text) if 'last one' not in quantity.text.lower() else 1

        def process_options(options):
            item_info['options'] = [option.text.strip() for option in options if option['value'] != "-1"]

        def process_url(url):
            item_info['seller_url'] = url['href']

        def process_img(images):
            item_info['img'] = list(set([i.get('data-zoom-src') for i in images if i]))

        def process_default(element, key):
            item_info[key] = element.text if element else None

        handlers = {
            'price': process_price,
            'ship_price': process_ship_price,
            'quantity_available': process_quantity,
            'options': process_options,
            'seller_url': process_url,
            'img': process_img
        }

        for k, v in element_mapping.items():
            if v is None:
                continue
            handler = handlers.get(k, lambda element, key=k: process_default(element, key))
            handler(v)

        return item_info

    def scrape(self, url: str = None, url_list: list = None) -> dict | list:
        if url_list:
            scraped_data = []
            for ur in url_list:
                html = self.fetch_item_html(ur)
                if html:
                    data = self.proceed_html(html, ur)
                    scraped_data.append(data)
            self.save_file(scraped_data)
            return scraped_data

        elif url:
            html = self.fetch_item_html(url)
            result = self.proceed_html(html, url)
            self.save_file(result)
            return result

    @staticmethod
    def save_file(data: dict | list) -> None:
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(data, file)
        print('Data saved to "data.json"')


if __name__ == '__main__':
    urls = [
        'https://www.ebay.com/itm/374871820791?itmmeta=01J2CDBE56JHYJDJPVK41XKZSK&hash=item57481a09f7:g:C5IAAOSw~GZmg6qG&itmprp=enc%3AAQAJAAAA4Lm05QXUT6QbeZnfSUc3pZXDcytaFkOESO6tKmR9tkMIN4aWZLSKAmz3bLeCp367%2FpLRzSwk2thSAm5YYs37wFpCFpG0uzVQq0L6p3qVuhLk%2FZLd5bog44%2FoLmxBX%2BUzTLymviw4R4wOhzxFtBj5o9K8YVu0qSBnq1lEYgkNt73ks%2BSmvzwFig885Sap8YdhaDJNCX34zI4bMRfb99e5ydUGWzcuk%2F78QRxw3y754Aph2poMjxh6eLL4Ls0df%2FfmTTYha3Xt0PhmC0RK0cqQNFb4oZ3x2HidyZj0mR5FBySj%7Ctkp%3ABFBM1uKtjZNk',
        'https://www.ebay.com/itm/145476802108?itmmeta=01J2CNKHR7Q8DT48NYMTQCY8CP&hash=item21df17d63c:g:82AAAOSwwmpla~pP&itmprp=enc%3AAQAJAAAA0I8iEKKjQI8yUYb5K4eeKx0vXFQCNmTao0%2BE7O8BsG6MgVlt2lf9Cv%2F1ihE4vWAOxZcA9yDy63cie%2FYfQ3uaq%2FUu4iNk1MYFWT7Gflkn4%2Fv9o%2F7HGiRkKr%2F1ePBzpPMzsq93U4%2FvQjMmVU1eEH507wBzNZfzRc%2Ff3s%2FvrNgw6kcv6iqz1kSDerTXe17ywoxEMP2jXTym%2BRfGKBKQJaeFTsemQirf5m0FfHyB3rt%2BqGxb8C7upvw120WEYHBB004MnorKVfuoywcswrPSx0w0QTU%3D%7Ctkp%3ABFBMmJzOlZNk',
        'https://www.ebay.com/itm/226138769042?itmmeta=01J2CQRE8DTRTCCYAK4TDFGJ6D&hash=item34a6ebc692:g:qZcAAOSwyWZmPQoO&itmprp=enc%3AAQAJAAAA4FhrEtckUJZk7DsFQbNNFMwAszfHKcNTyCWG3Vs10OiCH3SSD7A6cP8oifBIZbs1U2vvA0Ael7UhSEximoMlEXag8NswP3RdvzknxLznpwCjOEOpHbNQsTfXmgnY%2Be0MzM%2FhgvB9xyHjo3whag8dgjsA2or8dPADfZb4p1tDy2cZ2MJZHyDVlR2fSmwAnA6WBjDUikjxsk1ZdGIehgdrPtbEYPClJ8lNnV6g8w9Lw7r2YuvHuNuxr44LBzgl2cCF9D9uFJ516VxBiu%2FfaURuzYhpdg8XXmM3KZvhHLHtwNNE%7Ctkp%3ABFBMouThl5Nk',
        'https://www.ebay.com/itm/404111949256?itmmeta=01J2CTR87AAKA4AH3WMCWA8HYW&hash=item5e16f2fdc8:g:ed8AAOSwkdZjxnlz&itmprp=enc%3AAQAJAAAA0HBwSzC%2B4PgBRWUHOZT4VuuRNPBa%2FLaCUuuqybRpl%2BgY3FgwrsixMQ2W3sdanLdEJcLzesI9Z65ZvtMVON6aRmmwihRv%2F9ujQccJ6lGSsPISgH4iKyD1hudJA4ZaCAMRwMfNFjXiE9hG4lU2r%2BNR70STbqZzfk%2FWqKMA%2BHpiXPd9tqgsUHqdQosLP%2BQ6%2FdcEeV3lQcL%2BnWJRGTsGhpxzUvQKjltcR4EfelImhyObU5MCsZkPv7%2BJMhauycf2DDa4gIYpLQNDTtmofXdT4ND8Za8%3D%7Ctkp%3ABk9SR_yD4ZqTZA',
        'https://www.ebay.com/itm/256538059944?itmmeta=01J2CV2SQ6C8P7TKB96YYJSG4Q&hash=item3bbadc24a8:g:fY4AAOSwvGZhxtit&itmprp=enc%3AAQAJAAAA0PpNPkH08z3AEXnEOMXQL9uwpvQgp9HPEfqxbt7wiWMk9K2WS5pOwXRZYUsGy40%2Frd%2FoXvC1UzLvhbS2Bww0gECh7%2BQYTJW%2B3JklpelXKg5KzoBNvpuxEiEMrJujrQBm4hIFJZsTQ%2BzHLEcsJEk3klGnhTph5g%2F1CbYh9hHV7exgHgXifRI2WYPJgGASoDEAFHktFpdanHV79%2BZIZN2o4fBWyCbfRsXs84mxtvt6FQe%2BE%2BSMUvJFwE5Q2HppIu04d4qBZRdBYt%2FSTMD5oKH8yKo%3D%7Ctkp%3ABFBM_puLm5Nk',
        'https://www.ebay.com/itm/285858514792?itmmeta=01J2CVKFR1THATAW2KCRMVWYQY&hash=item428e7ec768%3Ag%3Ax0UAAOSwR%7ENlbaKn&_trkparms=%2526rpp_cid%253D64ba3dd356318a9866be5c44'
    ]
    scraper = Scraper()
    scraped = scraper.scrape(url=urls[0])
    # scraped = scraper.scrape(url_list=urls)

