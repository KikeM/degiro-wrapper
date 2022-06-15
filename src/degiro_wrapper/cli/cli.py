from pathlib import Path
from pprint import pprint

import click
import pandas as pd
from degiro_wrapper.core.api_methods import download_positions_raw
from degiro_wrapper.core.utils import create_ytd_calendar
from degiro_wrapper.core.api_methods import get_login_data


@click.group
def cli():
    click.echo("Welcome to the degiro-wrapper CLI!")


@cli.command
@click.option("--from", "-f", "from_", type=str, help="Starting date.")
@click.option(
    "--to",
    "-t",
    "to",
    type=str,
    default="today",
    help="Ending date.",
    show_default=True,
)
@click.option(
    "--path",
    "-p",
    "path",
    type=str,
    default=".",
    required=True,
    help="Path to download the files.",
)
def download_positions(from_, to, path):
    """Download raw positions from Degiro."""
    click.echo("Downloading positions ...")

    today = pd.to_datetime(to).date()
    calendar = pd.date_range(freq="B", start=from_, end=today)

    start = calendar[0].strftime("%Y-%M-%d")
    end = calendar[-1].strftime("%Y-%M-%d")
    click.echo(f"Date Range : {start} - {end}")

    path = Path(path)
    click.echo(f"Path : {path}")

    credentials = get_login_data()
    download_positions_raw(path=path, calendar=calendar, credentials=credentials)

    click.echo("Done!")


@cli.command
@click.option(
    "--path",
    "-p",
    "path",
    type=str,
    default=".",
    required=True,
    help="Path to check the positions files and dates.",
)
def check_missing_dates(path):

    path = Path(path)

    csv_files = path.glob("*.csv")
    dates = list(map(lambda x: x.stem.split("_")[-1], csv_files))
    dates = pd.to_datetime(dates, yearfirst=True)
    dates = dates.sort_values()

    calendar_ytd = create_ytd_calendar()

    dates = set(dates)
    calendar_ytd = set(calendar_ytd)
    dates_missing = calendar_ytd.difference(dates)
    dates_missing = pd.DatetimeIndex(dates_missing)
    dates_missing = dates_missing.sort_values()

    pprint(dates_missing, compact=False)