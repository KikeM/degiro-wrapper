import webbrowser
from random import normalvariate
from time import sleep

import requests
from bs4 import BeautifulSoup
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
        [(name, currency, ISIN, IB symbol, Trading symbol), ...]

    If no rows are retrieved, list is empty.

    Notes
    -----
    Ad-hoc table parsing for IB. 
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
            isin           = get_isin(tree, _row)
            #isin           = None
            
        # If no more rows are available, catch error
        except IndexError as error: 
            # pass
            break

        # Append row to list
        rows.append((name, currency, isin, symbol_ib, symbol_trading))

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
    response = get_response(url, wait = wait)

    # Build tree
    tree = html.fromstring(response.content)
    
    return tree 
    

def url_to_soup(url, wait = True):
    """Convert url to BeautifulSoup.

    Parameters
    ----------
    url: str

    Returns
    -------
    BeautifulSoup
    """
    response = get_response(url, wait = wait)

    soup = BeautifulSoup(response.text, features="lxml")

    return soup


def get_isin(tree, row):
    """Get ISIN value from exchange tree. 

    Parameters
    ----------
    Element HTML

    Returns
    -------
    str
    
    Notes
    -----
    So fu***** lucky. 
    """
    # Read data URL linked to product name
    xpath_data = '//*[@id="exchange-products"]/div/div/div[3]/div/div/div/table/tbody/tr[{row}]/td[2]/a'
    url_data = tree.xpath(xpath_data.format(row = row))[0].attrib['href'].split("'")[1]

    # Get soup from data URL
    soup = url_to_soup(url_data)

    # Get all elements from soup in specific format. 
    elements = set(soup.text.replace('\n', ',').split(','))

    # Capture and exploit ISINXXYYYYYYY structure
    # after set operation
    for element in elements:
        if 'ISIN' in element:
            text = element
            break

    try:
        isin = text.split('ISIN')[-1]
    except UnboundLocalError:
        webbrowser.open_new(url_data)
        input("Hit enter when you have solved the captcha.")
        isin = get_isin(tree, row = row)

    return isin


def _sleep_random(mu = 0.25, sigma = 1):
    """Sleep for random time.
    """
    _time = normalvariate(mu, sigma)
    _time = abs(_time)

    sleep(_time)


def get_response(url, wait = True):
    """Get Requests response with wait parameter. 

    Parameters
    ----------
    url: str

    Returns
    -------
    requests.Response

    Raises
    ------
    ValueError on status_code != 200.
    """
    # Wait some random time to prevent getting blocked. 
    if wait == True:

        _sleep_random()

    # Get HTML
    response = requests.get(url=url)

    if response.status_code != 200:
        raise ValueError(f"Response code for {url} was {response.status_code}.")

    return response