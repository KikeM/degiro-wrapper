from pathlib import Path
from pprint import pprint

import click
import pandas as pd
from degiro_wrapper.core.api_methods import (
    download_cashflows_raw,
    download_positions_raw,
    get_login_data,
)
from degiro_wrapper.core.preprocess import clean_cashflows, clean_positions
from degiro_wrapper.core.utils import create_ytd_calendar


@click.group
def cli():
    click.echo("Welcome to the degiro-wrapper CLI!")


@cli.command
@click.option(
    "--start",
    "-s",
    "start",
    type=str,
    required=True,
    help="Starting date.",
)
@click.option(
    "--end",
    "-e",
    "end",
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
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Dry run.",
)
def download_positions(start, end, path, dry):
    """Download raw positions from Degiro."""
    click.echo("Downloading positions ...")

    today = pd.to_datetime(end).date()
    # Degiro provides updated positions with one-day lag
    if end == "today":
        today = today - pd.offsets.BDay(1)
    calendar = pd.date_range(freq="B", start=start, end=today)

    start = calendar[0].strftime("%Y-%M-%d")
    end = calendar[-1].strftime("%Y-%M-%d")
    path = Path(path)
    click.echo(f"Start : {start}")
    click.echo(f"End   : {end}")
    click.echo(f"Path  : {path.absolute()}")

    if not dry:
        credentials = get_login_data()
        download_positions_raw(path=path, calendar=calendar, credentials=credentials)

    if dry:
        click.echo("Nothing done, end of dry run!")
    else:
        click.echo("Done!")


@cli.command
@click.option(
    "--path",
    "-p",
    "path",
    type=str,
    default=".",
    required=True,
    help="Path to download cashflows file.",
)
@click.option(
    "--start",
    "-s",
    "start",
    type=str,
    required=True,
    help="Starting date.",
)
@click.option(
    "--end",
    "-e",
    "end",
    type=str,
    default="today",
    help="Ending date.",
    show_default=True,
)
@click.option(
    "--dry",
    is_flag=True,
    default=False,
    help="Dry run.",
)
def download_cashflows(path, start, end, dry):
    """Download raw cashflows from Degiro."""

    click.echo("Downloading cashflows ...")

    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    path = Path(path)
    click.echo(f"Start : {start}")
    click.echo(f"End   : {end}")
    click.echo(f"Path  : {path.absolute()}")

    if not dry:
        credentials = get_login_data()
        download_cashflows_raw(
            credentials=credentials,
            start=start,
            end=end,
            path=path,
        )

    if dry:
        click.echo("Nothing done, end of dry run!")
    else:
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
    """Check missing dates YTD from raw positions."""

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


@cli.command
@click.option(
    "--path",
    "-p",
    "path",
    type=str,
    required=True,
    help="Path to extract positions.",
)
@click.option(
    "--to",
    "-t",
    "path_to",
    type=str,
    required=False,
    default=None,
    help="Path to dump database. By default the parent of --path is used.",
)
def create_db_positions(path, path_to):
    """Create positions database from raw positions folder."""

    path = Path(path)
    click.echo(f"Cleaning raw positions from : {path.absolute()}")

    if path_to is None:
        path_to = path.parent
    path_to = Path(path_to) / "db_positions.csv"
    click.echo(f"Dumping DB-positions to {path_to.absolute()}")

    long = clean_positions(path)
    long.to_csv(path_to)

    click.echo("Done!")


@cli.command
@click.option(
    "--path",
    "-p",
    "path",
    type=str,
    required=True,
    help="Path to extract positions.",
)
@click.option(
    "--to",
    "-t",
    "path_to",
    type=str,
    required=False,
    default=".",
    help="Path to dump database. By default the parent of --path is used.",
)
def create_db_cashflows(path, path_to):
    """Create DB-cashflows from raw cashflows file."""

    path = Path(path)
    click.echo(f"Cleaning raw cashflows from : {path.absolute()}")

    path_to = Path(path_to) / "db_cashflows.csv"
    click.echo(f"Dumping DB-cashflows to {path_to.absolute()}")

    raw = pd.read_csv(path)
    cfs = clean_cashflows(raw)
    cfs.to_csv(path_to, index=False)

    click.echo("Done!")
