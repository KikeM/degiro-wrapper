from pathlib import Path

import click
import pandas as pd
from degiro_wrapper.conventions import Positions

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
    "--path",
    "path_products",
    type=str,
    required=False,
    default=".",
    help="Path products list.",
)
def describe(path_db, path_products):

    path_db = Path(path_db)
    path_products = Path(path_products)

    database = pd.read_csv(path_db, index_col=0)

    products = database[[Positions.NAME, Positions.ISIN]]
    products = products.drop_duplicates()

    path_products = path_products / "products.csv"
    products.to_csv(path_products)
