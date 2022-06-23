from degiro_wrapper.conventions import Positions, Transactions, Calculations


def compute_tna(positions):

    tna = positions.groupby(Positions.DATE)[Positions.VALUE_LOCAL].sum()
    tna = tna.squeeze()

    tna.name = Calculations.TNA

    return tna


def compute_cfs(transactions):

    cfs = transactions.groupby(Transactions.DATE)[Transactions.VALUE_LOCAL].sum()
    cfs = cfs.squeeze()

    # In the original file, buying is negative from the cash amount,
    # but it is a inflow to the portfolio.
    cfs = cfs.mul(-1)

    cfs.name = Calculations.CFS

    return cfs


def compute_return_daily(tna, cfs):
    """Compute portfolio daily returns.

    Parameters
    ----------
    tna : pandas.Series
    cfs : pandas.Series

    Returns
    -------
    return_daily : pandas.Series
    """

    _cfs = cfs.reindex(tna.index, fill_value=0.0)
    return_daily = tna / (tna.shift(1) + _cfs) - 1
    first_day = return_daily.index[0]

    # The first day there is not return
    return_daily.loc[first_day] = 0.0

    return_daily.name = Calculations.RETURN_DAILY

    return return_daily


def compute_return_total(return_daily):
    """Compute portfolio cumulative total return.

    Parameters
    ----------
    return_daily : pandas.Series

    Returns
    -------
    return_total : pandas.Series
    """

    return_total = return_daily.add(1).cumprod().sub(1)
    return_total.name = Calculations.RETURN_TOTAL

    return return_total
