# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
# %load_ext autoreload
# %autoreload 2

# %%
import pandas as pd
from tqdm import tqdm as tqdm
from IPython.display import clear_output

from model import parse_table, url_to_tree

# %%
exchanges = [('sbf', 'Euronext France'), 
            ('chixde', 'CHI-X Europe Ltd Clearstream'),
            ('fwb', 'Frankfurt Stock Exchange'),
            ('swb', 'Stuttgart Stock Exchange'), 
            ('ibis', 'XETRA'), 
            ('chixen', 'CHI-X Europe Lts Clearnet'), 
            ('aeb', 'Euronext NL Stocks'), 
            ('bm', 'Bolsa de Madrid'), 
            ('sfb', 'Swedish Stock Exchange'), 
            ('ebs', 'SIX Swiss Exchange'),
            ('chixuk', 'CHI-X Europe Ltd Crest'),
            ('lse', 'London Stock Exchange'), 
            ('lseetf', 'London Stock ETF Exchange')]

# %%
xpaths = dict()

xpaths["symbolIB"]      = '//*[@id="exchange-products"]/div/div/div[3]/div/div/div/table/tbody/tr[{row}]/td[1]'
xpaths["name"]          = '//*[@id="exchange-products"]/div/div/div[3]/div/div/div/table/tbody/tr[{row}]/td[2]/a'
xpaths["symbolTrading"] = '//*[@id="exchange-products"]/div/div/div[3]/div/div/div/table/tbody/tr[{row}]/td[3]'
xpaths["currency"]      = '//*[@id="exchange-products"]/div/div/div[3]/div/div/div/table/tbody/tr[{row}]/td[4]'

# %%
url  = "https://www.interactivebrokers.com/en/index.php?"
url += "f=2222&exch={exchange}&showcategories=ETF&p=&cc=&limit=100&page={page}"

# %%
# Add exchange
products = []

# Collect exchange products
for exchange, _ in tqdm(exchanges):
        
    products_exchange = []
    
    # Collect page products
    for page in tqdm(range(1, 100), leave = False):

        # Add page tag
        _url_page = url.format(exchange=exchange, page = page)

        # Get tree
        tree = url_to_tree(_url_page)

        # Parse table
        products_page = parse_table(tree, xpaths)

        # If no products, this was the last page
        if len(products_page) == 0:
            break

        # Add page products to exchange products
        products_exchange.extend(products_page)

    # Add products with their exchange referenced
    for row in products_exchange:

        products.append(row + (exchange,))
        
    clear_output()

# %%
products_df = pd.DataFrame(data = products, 
                           columns = ['name', 'currency', 'symbolIB', 'symbolTrading', 'exchange'])

# %%
