from pathlib import Path

import click
import matplotlib.pyplot as plt
import pandas as pd
from degiro_wrapper.conventions import Positions, Transactions
from degiro_wrapper.reporting.calculations import (
    compute_cfs,
    compute_return_daily,
    compute_return_total,
    compute_tna,
)
from degiro_wrapper.reporting.plot import plot_report
from degiro_wrapper.reporting.utils import filter_positions, filter_transactions

from .cli import cli


@cli.command
@click.option(
    "--ps",
    "path_ps",
    type=str,
    required=True,
    default=None,
    help="Path positions.",
)
@click.option(
    "--tr",
    "path_tr",
    type=str,
    required=True,
    default=None,
    help="Path transactions.",
)
@click.option(
    "--pf",
    "path_pf",
    type=str,
    required=True,
    default=None,
    help="Path portfolio.",
)
@click.option(
    "--start",
    "-s",
    "start",
    type=str,
    required=False,
    default=None,
    help="Start date.",
)
@click.option(
    "--end",
    "-e",
    "end",
    type=str,
    required=False,
    default=None,
    help="End date.",
)
@click.option(
    "--path_rp",
    "path_rp",
    type=str,
    required=False,
    default=".",
    help="Path to dump the report.",
)
def report(path_ps, path_tr, path_pf, start, end, path_rp):
    """Create general report."""

    path_ps = Path(path_ps)
    path_tr = Path(path_tr)
    path_pf = Path(path_pf)

    positions = pd.read_csv(path_ps, index_col=0, parse_dates=[Positions.DATE])
    transactions = pd.read_csv(path_tr, parse_dates=[Transactions.DATE])
    portfolio = pd.read_csv(path_pf, index_col=Positions.ISIN)

    if start:
        start = pd.to_datetime(start)
    if end:
        end = pd.to_datetime(end)

    # -------------------------------------------------------------------------
    # Trim data to reporting period
    isins = portfolio.index
    positions = filter_positions(
        positions=positions,
        isins=isins,
        start=start,
        end=end,
    )

    _start = positions[Positions.DATE].min().strftime("%Y-%m-%d")
    _end = positions[Positions.DATE].max().strftime("%Y-%m-%d")
    click.echo(f"Start : {_start}")
    click.echo(f"End   : {_end}")

    transactions = filter_transactions(
        transactions=transactions,
        isins=isins,
        start=start,
        end=end,
    )

    # -------------------------------------------------------------------------
    # Compute TnA
    tna = compute_tna(positions)

    # -------------------------------------------------------------------------
    # Compute CFs
    cfs = compute_cfs(transactions)

    # -------------------------------------------------------------------------
    # Compute daily returns
    return_daily = compute_return_daily(tna=tna, cfs=cfs)

    # -------------------------------------------------------------------------
    # Compute total return
    return_total = compute_return_total(return_daily)

    # -------------------------------------------------------------------------
    # Create report
    path_rp = Path(path_rp)

    path_rp = path_rp / f"report_{_start}_{_end}"
    path_rp.mkdir(exist_ok=True)

    plot_report(path_rp, tna=tna, cfs=cfs, return_total=return_total)
