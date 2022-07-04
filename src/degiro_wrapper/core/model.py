def compute_weights(amounts, isin_cash=None, regex=None):
    """
    Compute positions weights.

    Parameters
    ----------
    amounts: pd.DataFrame

    isin_cash: str

    regex: str

    Returns
    -------
    pd.DataFrame
    """
    _amount_df = amounts.copy()

    # Apply filters
    if isin_cash is not None:
        _amount_df = _amount_df.drop(columns=isin_cash)
    if regex is not None:
        _amount_df = _amount_df.filter(regex=regex)

    # Compute weights over the remaining assets
    weights_df = _amount_df.div(_amount_df.sum(axis=1), axis="index")

    return weights_df
