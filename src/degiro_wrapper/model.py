def compute_weights(amounts, isin_cash=None, regex=None):
    """Compute positions weights.

    Parameters
    ----------
    amounts: pd.DataFrame
    isin_cash: str
    regex: str

    Returns
    -------
    pd.DataFrame
    """
    # Apply filters
    if isin_cash is not None:
        amounts = amounts.drop(columns=isin_cash)

    if regex is not None:
        amounts = amounts.filter(regex=regex)

    # Compute weights over the remaining assets
    weights = amounts.div(amounts.sum(axis=1), axis='index')

    return weights
