def compute_weights(input_df, copy=True):
    """
    Compute the weights assuming all positions are long.
    
    Parameters
    ----------
    input_df: pd.DataFrame
        - Index: DatetimeIndex
        - Columns: ['amount', ...]
        - Values: amount in cash
    
    Returns
    -------
    df: pd.DataFrame
        A **copy** of input_df with an extra column, 'weight'
    """
    if copy == True:
        df = input_df.copy()
    else:
        df = input_df
    
    for date in df.index:
    
        assets_value = df.loc[date, 'amount'].sum()

        df.loc[date, 'weight'] = assets_value

        _amounts = df.loc[date, 'amount']
        df.loc[date, 'weight'] = _amounts / df.loc[date, 'weight']
    
    return df