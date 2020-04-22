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

# + extensions={"jupyter_dashboards": {"version": 1, "views": {"grid_default": {}, "report_default": {"hidden": false}}}}
# coding: utf-8
import matplotlib.pyplot as plt

import datetime
import pandas as pd
from pathlib import Path
import degiro_wrapper as dw
import logging

plt.ion()

logging.info("Reading config.")

CONFIG_DIR = "/Users/mmngreco/github/mmngreco/degiro-wrapper/degiro.ini"
CONFIG_SECTION = "DEGIRO"

ISIN_CASH = dw.conventions.ISIN_CASH

config = dw.api_methods.get_config(CONFIG_DIR)
user_data = dw.api_methods.get_login_data(config=config)

path = Path(config[CONFIG_SECTION]["files_dir"]).expanduser().absolute()
if not path.exists():
    path.mkdir()

date_start = "20191001"
date_end = datetime.datetime.today()
calendar = pd.date_range(start=date_start, end=date_end, freq="B")

logging.info("Downloading data")
dw.api_methods.download_positions(
    calendar=calendar,
    path=path,
    data=user_data,
    filename_template="pos_%Y%m%d",
)

positions_raw_df = dw.preprocess.positions_xls_to_df(path, isin_cash=ISIN_CASH)
cleaned_data = dw.preprocess.positions_raw_to_clean(positions_raw_df)

amount_df = cleaned_data["amount"]
prices_df = cleaned_data["prices"]
shares_df = cleaned_data["shares"]
nav_df = cleaned_data["nav"]
rets_df = cleaned_data["returns"]

path_account = dw.api_methods.download_cashflows(user_data, date_start, date_end, path)
cf = dw.preprocess.generate_cashflows(path_account=path_account, isin_cash=ISIN_CASH)
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

# + extensions={"jupyter_dashboards": {"version": 1, "views": {"grid_default": {}, "report_default": {"hidden": false}}}}
weights_df.plot.area(title="Weights")

# + extensions={"jupyter_dashboards": {"version": 1, "views": {"grid_default": {}, "report_default": {"hidden": false}}}}
weights_df.tail(1).T[weights_df.index[-1]].plot.pie();

# + extensions={"jupyter_dashboards": {"version": 1, "views": {"grid_default": {}, "report_default": {"hidden": false}}}}
pf_returns_ss = (rets_df * weights_df).dropna(how="all").sum(axis=1)
pf_returns_ss.plot();

# + extensions={"jupyter_dashboards": {"version": 1, "views": {"grid_default": {}, "report_default": {"hidden": true}}}}
pf_equity_ss = pf_returns_ss.add(1).cumprod().sub(1)
pf_equity_ss.plot();
# -


