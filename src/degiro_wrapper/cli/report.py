from pathlib import Path

import click
import pandas as pd
from degiro_wrapper.conventions import Positions

import matplotlib.pyplot as plt

from .cli import cli


@cli.command
@click.option(
    "--db",
    "path_db",
    type=str,
    required=True,
    default=None,
    help="Path database.",
)
@click.option(
    "--cf",
    "path_cf",
    type=str,
    required=True,
    default=None,
    help="Path cashflows.",
)
@click.option(
    "--pf",
    "path_pf",
    type=str,
    required=True,
    default=None,
    help="Path portfolio.",
)
def report(path_db, path_cf, path_pf):

    path_db = Path(path_db)
    path_cf = Path(path_cf)
    path_pf = Path(path_pf)

    database = pd.read_csv(path_db, index_col=0)
    cashflows = pd.read_csv(path_cf)
    portfolio = pd.read_csv(path_pf, index_col=Positions.ISIN)

    mask = database[Positions.ISIN].isin(portfolio.index)
    database = database.loc[mask]

    aum = database.groupby("date")["valueLocal"].sum()

    aum.plot()
    plt.grid()
    plt.ylabel("AUM (EUR)")
    plt.xlabel("Date")
    plt.show()
    plt.close()

    breakpoint()
