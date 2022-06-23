import re

import numpy as np
import pandas as pd
from degiro_wrapper.conventions import (
    AssetType,
    CashflowType,
    Cashflows,
    CashflowsRaw,
    Positions,
    PositionsRaw,
    Transactions,
    TransactionsRaw,
)
from pandas.errors import EmptyDataError
from tqdm import tqdm


def extract_numbers(frame):
    """Extract numbers from string.

    Parameters
    ----------
    frame : pandas.DataFrame

    Returns
    -------
    frame : pandas.DataFrame
    """
    numeric_const_pattern = (
        "[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?"
    )
    rx = re.compile(numeric_const_pattern, re.VERBOSE)
    frame = frame.applymap(lambda x: rx.findall(x)[0])

    return frame


def replace_values(frame, old, new):
    """Replace string values in DataFrame, from old to new.

    Parameters
    ----------
    frame : pandas.DataFrame
    old : str
    new : str

    Returns
    -------
    frame : pandas.DataFrame
    """
    frame = frame.fillna("-")
    frame = frame.apply(lambda x: x.str.replace(old, new))
    frame = frame.replace("-", np.nan)
    return frame


def clean_positions(path):
    """Create long DataFrame from raw CSV positions.

    Parameters
    ----------
    path : Path-like object

    Returns
    -------
    long : pandas.DataFrame
    """
    columnas = [
        PositionsRaw.PRICE,
        PositionsRaw.PRODUCT,
        PositionsRaw.ISIN,
        PositionsRaw.QUANTITY,
        PositionsRaw.VALUE_LOCAL,
        PositionsRaw.VALUE_EUR,
    ]

    long = pd.DataFrame(columns=columnas)

    files = list(path.glob("pos*.csv"))
    for file in tqdm(files):

        # ---------------------------------------------------------------------
        # Read file
        try:
            positions_day = pd.read_csv(file)
        except EmptyDataError:
            continue

        # ---------------------------------------------------------------------
        # Replace commas with dots
        columns_to_clean = [
            PositionsRaw.PRICE,
            PositionsRaw.VALUE_EUR,
            PositionsRaw.VALUE_LOCAL,
        ]
        positions_day[columns_to_clean] = replace_values(
            frame=positions_day[columns_to_clean],
            old=",",
            new=".",
        )

        # ---------------------------------------------------------------------
        # Extract numerical values
        columns_to_extract = [
            PositionsRaw.VALUE_EUR,
            PositionsRaw.VALUE_LOCAL,
        ]
        positions_day[columns_to_extract] = extract_numbers(
            positions_day[columns_to_extract]
        )

        # ---------------------------------------------------------------------
        # Convert to float and string
        columns_to_float = [
            PositionsRaw.QUANTITY,
            PositionsRaw.PRICE,
            PositionsRaw.VALUE_EUR,
            PositionsRaw.VALUE_LOCAL,
        ]
        positions_day[columns_to_float] = positions_day[columns_to_float].astype(float)

        columns_to_string = [PositionsRaw.ISIN, PositionsRaw.PRODUCT]
        positions_day = positions_day.fillna("-")
        positions_day[columns_to_string] = positions_day[columns_to_string].astype(str)
        positions_day = positions_day.replace("-", np.nan)

        # ---------------------------------------------------------------------
        # Add valuation date
        date = file.stem.split("_")[-1]
        positions_day[Positions.DATE] = date

        # ---------------------------------------------------------------------
        # Append to dataframe
        long = pd.concat([long, positions_day], axis=0)

    # -------------------------------------------------------------------------
    # Convert dates to Datetime
    long[Positions.DATE] = pd.to_datetime(long[Positions.DATE])

    # -------------------------------------------------------------------------
    # Rename columns to structured names
    map_columnas = {
        PositionsRaw.PRODUCT: Positions.NAME,
        PositionsRaw.ISIN: Positions.ISIN,
        PositionsRaw.QUANTITY: Positions.SHARES,
        PositionsRaw.PRICE: Positions.PRICE,
        PositionsRaw.VALUE_LOCAL: Positions.VALUE_LOCAL,
        PositionsRaw.VALUE_EUR: Positions.VALUE_PORTFOLIO,
    }

    long = long.rename(columns=map_columnas)

    # -------------------------------------------------------------------------
    # Add position type
    mask_has_isin = long[Positions.ISIN].notna()

    long.loc[mask_has_isin, Positions.TYPE] = AssetType.ASSET
    long.loc[~mask_has_isin, Positions.TYPE] = AssetType.CASH

    # -------------------------------------------------------------------------
    # Sort by date
    long = long.sort_values(by=Positions.DATE)
    long = long.reset_index(drop=True)

    return long


def clean_cashflows(raw):
    """Clean cashflows file.

    Parameters
    ----------
    raw : pandas.DataFrame

    Returns
    -------
    clean : pandas.DataFrame
    """

    clean = raw.rename(
        columns={
            CashflowsRaw.DELTA: Cashflows.DELTA_CCY,
            CashflowsRaw.UNNAMED_DELTA: Cashflows.DELTA,
            CashflowsRaw.AMOUNT: Cashflows.AMOUNT_CCY,
            CashflowsRaw.UNNAMED_AMOUNT: Cashflows.AMOUNT,
            CashflowsRaw.DATE_VALUE: Cashflows.DATE_VALUE,
            CashflowsRaw.DATE: Cashflows.DATE,
            CashflowsRaw.TIME: Cashflows.TIME,
            CashflowsRaw.PRODUCT: Positions.NAME,
            CashflowsRaw.TYPE: Cashflows.TYPE,
            CashflowsRaw.ID: Cashflows.ID,
            CashflowsRaw.DESCRIPTION: Cashflows.DESCRIPTION,
        }
    )

    # -------------------------------------------------------------------------
    # Convert to float
    columns_commas = [Cashflows.DELTA, Cashflows.AMOUNT]
    clean[columns_commas] = replace_values(clean[columns_commas], old=",", new=".")
    clean[columns_commas] = clean[columns_commas].astype(float)

    # -------------------------------------------------------------------------
    # Convert to date
    columns_date = [Cashflows.DATE, Cashflows.DATE_VALUE]
    for col in columns_date:
        clean[col] = pd.to_datetime(
            clean[col],
            dayfirst=True,
            errors="coerce",
            format="%d-%m-%Y",
        )

    # -------------------------------------------------------------------------
    # Find buy and sell CFs
    type_pairs = [
        (CashflowType.RAW_COMPRA, CashflowType.BUY),
        (CashflowType.RAW_VENTA, CashflowType.SELL),
    ]
    for type_raw, type_clean in type_pairs:
        mask = clean[Cashflows.DESCRIPTION].str.contains(type_raw)
        clean.loc[mask, Cashflows.TYPE] = type_clean

    return clean


def clean_transactions(raw):
    """Clean transactions file.

    Parameters
    ----------
    raw : pandas.DataFrame

    Returns
    -------
    clean : pandas.DataFrame
    """

    clean = raw.rename(
        columns={
            TransactionsRaw.EXCHANGE: Transactions.EXCHANGE,
            TransactionsRaw.EXECUTION: Transactions.EXECUTION,
            TransactionsRaw.RATE: Transactions.RATE,
            TransactionsRaw.PRICE: Transactions.PRICE,
            TransactionsRaw.UNNAMED_PRICE: Transactions.PRICE_CCY,
            TransactionsRaw.VALUE_LOCAL: Transactions.VALUE_LOCAL,
            TransactionsRaw.UNNAMED_VALUE_LOCAL: Transactions.VALUE_LOCAL_CCY,
            TransactionsRaw.VALUE: Transactions.VALUE,
            TransactionsRaw.UNNAMED_VALUE: Transactions.VALUE_CCY,
            TransactionsRaw.TRANSACTION_COSTS: Transactions.TRANSACTION_COSTS,
            TransactionsRaw.UNNAMED_COSTS: Transactions.TRANSACTION_COSTS_CCY,
            TransactionsRaw.TOTAL: Transactions.TOTAL,
            TransactionsRaw.UNNAMED_TOTAL: Transactions.TOTAL_CCY,
            TransactionsRaw.DATE: Transactions.DATE,
            TransactionsRaw.TIME: Transactions.TIME,
            TransactionsRaw.PRODUCT: Positions.NAME,
            TransactionsRaw.TYPE: Transactions.TYPE,
            TransactionsRaw.ID: Transactions.ID,
            TransactionsRaw.SHARES: Transactions.SHARES,
        }
    )

    # -------------------------------------------------------------------------
    # Convert to date
    clean[Transactions.DATE] = pd.to_datetime(
        clean[Transactions.DATE],
        dayfirst=True,
        errors="coerce",
        format="%d-%m-%Y",
    )

    return clean


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
    amount_df = raw_positions.pivot(index="date", columns="ISIN", values="amount")
    prices_df = raw_positions.pivot(index="date", columns="ISIN", values="price")
    shares_df = raw_positions.pivot(index="date", columns="ISIN", values="shares")

    # Compute share-adjusted values
    nav_df = (amount_df / shares_df).dropna(axis=1, how="all")

    # Compute daily returns
    returns_df = nav_df.pct_change(limit=1)

    # Put on a business day basis
    amount_df = amount_df.asfreq("B")
    prices_df = prices_df.asfreq("B")
    shares_df = shares_df.asfreq("B")
    nav_df = nav_df.asfreq("B")
    returns_df = returns_df.asfreq("B")

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
    df_account = df_account.rename(
        columns={
            "Variación": "ccyDelta",
            "Unnamed: 8": "delta",
            "Saldo": "ccyAmount",
            "Unnamed: 10": "amount",
            "Fecha valor": "date",
        }
    )

    df_account["date"] = pd.to_datetime(df_account["date"], dayfirst=True)
    df_account = df_account.drop(
        columns=["Fecha", "Hora", "Producto", "Tipo", "ID Orden"]
    )

    # Generate changes in position
    deltas_df = df_account.groupby(["date", "ISIN", "amount"])["delta"].sum()
    deltas_df = pd.DataFrame(deltas_df).reset_index()

    # Compute cashflows
    cashflows_df = deltas_df.pivot_table(
        index="date", columns="ISIN", values="delta", aggfunc="sum"
    )

    # Compute external cashflows
    cashflows_external_df = df_account.loc[
        df_account["Descripción"].isin(["Ingreso", "Retirada"])
    ]

    # For some reason DEGIRO has the cashflows mark to market shifted by one.
    # and my guess is that unless there is a position transaction, they dont
    # write cash mark to markets on Fridays ...
    cashflows_df = cashflows_df.asfreq("D")
    cashflows_df[isin_cash] = cashflows_df[isin_cash].shift()
    cashflows_df = cashflows_df.asfreq("B")

    return cashflows_df, cashflows_external_df
