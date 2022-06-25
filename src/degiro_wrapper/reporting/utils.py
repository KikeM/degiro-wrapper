from degiro_wrapper.conventions import Positions, Transactions


def filter_positions(positions, isins, start=None, end=None):
    """Remove positions out of reporting period.

    Parameters
    ----------
    positions : pandas.DataFrame
    isins : list-like
        ISIN values in the portfolio.
    start : Datetime-like, optional
        by default None
    end : Datetime-like, optional
        by default None

    Returns
    -------
    positions : pandas.DataFrame
    """

    # -------------------------------------------------------------------------
    # Keep positions related to portfolio
    mask_isins = positions[Positions.ISIN].isin(isins)
    positions = positions.loc[mask_isins]

    # -------------------------------------------------------------------------
    # Trim in time
    executed = True
    alive = True

    if end:
        executed = positions[Positions.DATE] <= end
    if start:
        alive = positions[Positions.DATE] >= start

    if (start is not None) | (end is not None):
        mask = executed & alive
        positions = positions.loc[mask]

    return positions


def filter_transactions(transactions, isins, start=None, end=None):
    """Remove transactions out of reporting period.

    Parameters
    ----------
    transactions : pandas.DataFrame
    isins : list-like
        ISIN values in the portfolio.
    start : Datetime-like, optional
        by default None
    end : Datetime-like, optional
        by default None

    Returns
    -------
    transactions : pandas.DataFrame
    """

    # -------------------------------------------------------------------------
    # Remove unnecessary columns
    drop_columns = [
        Transactions.EXCHANGE,
        Transactions.EXECUTION,
        Transactions.ID,
        Transactions.RATE,
        Transactions.VALUE,
        Transactions.VALUE_CCY,
        Transactions.PRICE_CCY,
        Transactions.TOTAL,
        Transactions.TOTAL_CCY,
        Transactions.TRANSACTION_COSTS_CCY,
        Transactions.VALUE_LOCAL_CCY,
    ]
    transactions = transactions.drop(drop_columns, axis=1)

    # -------------------------------------------------------------------------
    # Keep positions related to portfolio
    mask_cfs = transactions[Transactions.ISIN].isin(isins)
    transactions = transactions.loc[mask_cfs]

    # -------------------------------------------------------------------------
    # Trim in time
    executed = True
    alive = True

    if end:
        alive = transactions[Transactions.DATE] <= end
    if start:
        executed = transactions[Transactions.DATE] >= start

    if (start is not None) | (end is not None):
        mask = executed & alive
        transactions = transactions.loc[mask]

    return transactions
