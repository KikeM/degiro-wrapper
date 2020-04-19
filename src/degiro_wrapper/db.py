"""
Contains an example of backend for db management.
This db will be used in a dashboard as data source.
"""
import datetime
import pandas as pd
from pathlib import Path
import degiro_wrapper as dw
import logging


# TODO : This module is under development.
# TODO : Create a folder in user home (~/.degiro-wrapper/)
# TODO : Create a folder in user home (~/.degiro-wrapper/assets)
# TODO : Create a symlink in user home (~/.degiro-wrapper/degiro.ini)
# TODO : General files handling : from raw to processed
# TODO : This module includes the same content that sandbox has.


def update_data():
    logging.info("Reading config.")

    CONFIG_DIR = "~/degiro-wrapper/degiro.ini"
    ISIN_CASH = dw.conventions.ISIN_CASH

    logging.info("Downloading data")

    # TODO : Batch version of download_positions ???
    config = dw.api_methods.get_config(CONFIG_DIR)
    user_data = dw.api_methods.get_login_data(config=config)
    date_start = "20191001"
    date_end = datetime.datetime.today()
    path = Path(config["DEGIRO"]["files_dir"]).expanduser().absolute()
    if not path.exists(): path.mkdir()

    dw.api_methods.download_positions(
        calendar=pd.date_range(start=date_start, end=date_end, freq="B"),
        path=path,
        data=user_data,
        filename_template="pos_%Y%m%d",
    )

    positions_raw_df = dw.preprocess.positions_xls_to_df(
        path, isin_cash=ISIN_CASH
    )
    path_account = dw.api_methods.download_cashflows(
        user_data, date_start, date_end, path
    )
    cf = dw.preprocess.generate_cashflows(
        path_account=path_account, isin_cash=ISIN_CASH
    )

    cashflows_df = cf["cashflows"]
    cashflows_external_df = cf["cashflows_external"]

    out = dict(**positions_raw_df, **cf)
    return out


out = update_data()
__import__("pdb").set_trace()
out["account"].head()
out["account"].head().dtypes
