import pandas as pd


def create_ytd_calendar():
    """Create year-to-date business calendar.

    Returns
    -------
    calendar : pandas.DatetimeIndex
    """
    today = pd.to_datetime("today").date()
    year_start = pd.to_datetime(f"{today.year}0101")
    calendar = pd.date_range(freq="B", start=year_start, end=today)
    return calendar