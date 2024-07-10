# Info
1. Dynamic fields: fields for prices and shipping price are dynamic depending on the information provided by the site, that is, if there is only payment in US, there will be price_US, if there is in EUR, there will be price_EUR and if there is both, there will be two fields price_US and price_EUR. The same with ship_price, if there is only EUR, there will be ship_price_EUR, etc.
2. When scraping, there are many items that are not shipped to the country of the person scraping, so ship_price will be N/A.

# Installation
`pip install -r requirements.txt`


