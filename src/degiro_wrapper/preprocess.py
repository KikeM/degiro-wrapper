
import pandas as pd
import urllib
from .api_endpoints import url_account

def positions_xls_to_df(path, isin_cash):
    """
    Parse positions xls files to DataFrame.

    Parameters
    ----------
    path: Path-like object

    isin_cash: str

    Returns
    -------
    pd.DataFrame
    """
    columnas = ['Fecha','Producto','Symbol/ISIN','Cantidad','Precio de ','Valor local','Valor en EUR']

    df = pd.DataFrame(columns=columnas)

    for file in path.glob('pos_*.xls'):

        # Read file
        df_day = pd.read_excel(file)

        # Get positions date
        df_day['Fecha'] = file.stem.split('_')[-1]

        # Append to dataframe
        df = df.append(df_day, sort=False)

    df['Fecha'] = pd.to_datetime(df['Fecha'])

    df = df.reset_index(drop=True)

    map_columnas = {'Fecha':'date','Producto':'product',
                    'Symbol/ISIN':'ISIN','Cantidad':'shares','Precio de ':'price',
                    'Valor local':'amount_to_drop','Valor en EUR':'amount'}

    df = df.rename(columns = map_columnas)
    df = df.drop  (columns = 'amount_to_drop')

    # Add position type
    mask_has_isin = df['ISIN'].notna()

    df.loc[mask_has_isin, 'type']  = 'long'
    df.loc[~mask_has_isin, 'type'] = 'cash'

    df['ISIN'] = df['ISIN'].fillna(isin_cash)

    # Sort by date
    df = df.sort_values(by='date')

    return df

def positions_raw_to_clean(raw_positions):
    """
    From raw positions to date/index-value/column style.

    Parameters
    ----------
    raw_positions: pd.DataFrame

    Returns
    -------
    tuple
        amount_df: position size
        prices_df: close price
        shares_df: number of participations
        nav_df: Net Assets Value, position / shares value
        returns_df: NAV returns

    Notes
    -----
    It does not contain the returns of the cash position.
    """
    amount_df  = raw_positions.pivot(index = 'date', columns='ISIN', values = 'amount')
    prices_df  = raw_positions.pivot(index = 'date', columns='ISIN', values = 'price')
    shares_df  = raw_positions.pivot(index = 'date', columns='ISIN', values = 'shares')

    # Compute share-adjusted values
    nav_df = (amount_df / shares_df).dropna(axis = 1, how = 'all')

    # Compute daily returns
    returns_df = nav_df.pct_change(limit=1)

    # Put on a business day basis
    amount_df  = amount_df.asfreq('B')
    prices_df  = prices_df.asfreq('B')
    shares_df  = shares_df.asfreq('B')
    nav_df     = nav_df.asfreq('B')
    returns_df = returns_df.asfreq('B')

    return amount_df, prices_df, shares_df, nav_df, returns_df

def generate_cashflows(path_account, isin_cash):
    """
    Generate positions and cash flows.

    Parameters
    ----------
    path_account: Path-like to folder

    isin_cash: str

    Returns
    -------
    tuple
        cashflows_df, cashflows_external_df
    """
    # Read and parse
    df_account = pd.read_excel(path_account)
    df_account = df_account.rename(columns={'Variación':'ccyDelta',
                                            'Unnamed: 8':'delta',
                                            'Saldo':'ccyAmount',
                                            'Unnamed: 10':'amount',
                                            'Fecha valor':'date'})

    df_account['date'] = pd.to_datetime(df_account['date'], dayfirst=True)
    df_account = df_account.drop(columns = ['Fecha', 'Hora', 'Producto', 'Tipo', 'ID Orden'])

    # Generate changes in position
    deltas_df = df_account.groupby(['date', 'ISIN', 'amount'])['delta'].sum()
    deltas_df = pd.DataFrame(deltas_df).reset_index()

    # Compute cashflows
    cashflows_df = deltas_df.pivot_table(index='date', columns='ISIN', values='delta', aggfunc='sum')

    # Compute external cashflows
    cashflows_external_df = df_account.loc[df_account['Descripción'].isin(['Ingreso', 'Retirada'])]

    # For some reason DEGIRO has the cashflows mark to market shifted by one.
    # and my guess is that unless there is a position transaction, they dont
    # write cash mark to markets on Fridays ...
    cashflows_df = cashflows_df.asfreq('D')
    cashflows_df[isin_cash] = cashflows_df[isin_cash].shift()
    cashflows_df = cashflows_df.asfreq('B')

    return cashflows_df, cashflows_external_df
