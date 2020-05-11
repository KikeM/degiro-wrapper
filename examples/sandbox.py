# ---
# jupyter:
#   jupytext:
#     formats: py,ipynb,md
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.4.2
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# 1. Imports.
# 1. Locate configuration file.
# 1. Retrieve logging data.
# 1. Download/update positions.
# 1. From xls files to dataframe.
# 1. Compute cleaned dataframes. 
# 1. Compute cash returns to allow matrix-like products. 
# 8. Compute performance.

# +
# coding: utf-8
import datetime
import pandas as pd
from pathlib import Path
import degiro_wrapper as dw
from degiro_wrapper.legacy import api_methods
from degiro_wrapper.legacy import preprocess
import logging

logging.info("Reading config.")

CONFIG_DIR = "~/degiro-wrapper/degiro.ini"
CONFIG_SECTION = "DEGIRO"

config = api_methods.get_config(CONFIG_DIR)
user_data = api_methods.get_login_data(config=config)

path = Path(config[CONFIG_SECTION]["files_dir"]).expanduser().absolute()
if not path.exists():
    path.mkdir()

date_start = "20191001"
date_end = datetime.datetime.today()
calendar = pd.date_range(start=date_start, end=date_end, freq="B")

logging.info("Downloading data")
api_methods.download_positions(
    calendar=calendar,
    path=path,
    data=user_data,
    filename_template="pos_%Y%m%d",
)

ISIN_CASH = dw.conventions.ISIN_CASH

positions_raw_df = preprocess.positions_xls_to_df(path, isin_cash=ISIN_CASH)

cleaned_data = preprocess.positions_raw_to_clean(positions_raw_df)

amount_df = cleaned_data["amount"]
prices_df = cleaned_data["prices"]
shares_df = cleaned_data["shares"]
nav_df = cleaned_data["nav"]
rets_df = cleaned_data["returns"]

path_account = api_methods.download_cashflows(user_data, date_start, date_end, path)

cf = preprocess.generate_cashflows(path_account=path_account, isin_cash=ISIN_CASH)
cashflows_df = cf["cashflows"]
cashflows_external_df = cf["cashflows_external"]

# ??? : What means ss and why the following is needed
cashflows_ss = cashflows_df.drop(columns=ISIN_CASH).sum(axis=1)
cashflows_total_ss = (
    cashflows_external_df.set_index("date")["amount"]
    .reindex(cashflows_ss.index, fill_value=0.0)
    .add(cashflows_ss)
)

cash_calendar = cashflows_total_ss.index
for today, yesterday in zip(cash_calendar[1:], cash_calendar):
    
    cash_today = amount_df.loc[today, ISIN_CASH]
    
    cash_yesterday = amount_df.loc[yesterday, ISIN_CASH]

    flows = cashflows_total_ss.loc[today]

    rets_df.loc[today, ISIN_CASH] = (cash_today - flows) / cash_yesterday - 1

logging.info("Compute performance")

weights_df = amount_df.div(amount_df.sum(axis=1), axis="index").shift(1)
weights_df = weights_df.rename(columns={ISIN_CASH: "Cash"})
weights_df.index.name = "Date"

pf_returns_ss = (rets_df * weights_df).dropna(how="all").sum(axis=1)
pf_equity_ss = pf_returns_ss.add(1).cumprod().sub(1)
pf_equity_ss.index.name = "Date"

pf_equity_ss.to_clipboard()

# -


