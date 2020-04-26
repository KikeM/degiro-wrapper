from random import normalvariate
from time import sleep

import requests
from lxml import html


def parse_table(tree, xpaths):
    """Parse products from tree.

    Parameters
    ----------
    tree: Element HTML

    xpaths: dict
        XPaths to rows and columns in the table.

    Returns
    -------
    list of tuples of strings
        [(name, currency, IB symbol, Trading symbol), ...]

    If no rows are retrieved, list is empty
    """
    # Collect xpaths
    xpath_name      = xpaths["name"]
    xpath_currency  = xpaths["currency"]
    xpath_symbol_ib = xpaths["symbolIB"]
    xpath_symbol    = xpaths["symbolTrading"]

    # Initialize holder and counter
    rows = []
    _row = 1

    # Iterate within the table rows
    while True:

        try:
            name           = tree.xpath(xpath_name.format(row=_row))[0].text
            currency       = tree.xpath(xpath_currency.format(row=_row))[0].text
            symbol_ib      = tree.xpath(xpath_symbol_ib.format(row=_row))[0].text
            symbol_trading = tree.xpath(xpath_symbol.format(row=_row))[0].text
        
        # If no more rows are available, catch error
        except IndexError as error: 
            # pass
            break

        # Append row to list
        rows.append((name, currency, symbol_ib, symbol_trading))

        # Move to the next row
        _row += 1

    return rows


def url_to_tree(url, wait = True):
    """From url get HTML tree.

    Parameters
    ----------
    url: str

    wait: bool
        Forces Normal(0.5, 1) seconds of wait before
        the HTTP request. 

    Returns
    -------
    Element html
    """
    # Wait some random time to prevent getting blocked. 
    if wait == True:

        _sleep_random()

    # Get HTML
    response = requests.get(url=url)

    if response.status_code != 200:
        raise ValueError(f"Response code for {url} was {response.status_code}.")

    # Build tree
    tree = html.fromstring(response.content)
    
    return tree 
    

def _sleep_random(mu = 0.5, sigma = 1):
    """Sleep for random time.
    """
    _time = normalvariate(mu, sigma)
    _time = abs(_time)

    sleep(_time)
