import datetime
import logging
from pathlib import Path

import pandas as pd

import degiro_wrapper as dw
from degiro_wrapper.connector import ConnectorDegiro


class Portfolio():

    def __init__(self, path_config = "~/degiro-wrapper/degiro.ini"):

        self.ISIN_CASH = dw.conventions.ISIN_CASH

        self.connector = ConnectorDegiro(path_config)

        self.amount_df = None
        self.prices_df = None
        self.shares_df = None
        self.nav_df = None
        self.rets_df = None

    def _create_daily_calendar(self, start, end = None):
        """Creates daily calendar with business day frequency.

        Parameters
        ----------
        start: "YYMMDD", Datetime-like

        end: "YYMMDD", Datetime-like

        Returns
        -------
        Datetime-like Index

        Notes
        -----
        If no end is specified, used today's date. 
        """

        date_start = start

        if end is None:
            date_end = datetime.datetime.today()
        else:
            date_end = end

        calendar = pd.date_range(start=date_start, end=date_end, freq="B")

        return calendar

    def get_timeseries_positions(self, start, end = None, calendar = None):
        """From raw xls files to dataframes.

        Parameters
        ----------
        path_assets: Path-like

        template: str
            Regex template to identify the files to parse. 

        Returns
        -------
        dict
            - Keys: "amount", "prices", "shares", "nav", "returns"
            - Values: pd.DataFrame
        """

        if calendar is None:
            self.calendar = self._create_daily_calendar(start, end)
        else:
            self.calendar = calendar
            
        data = self.connector.get_positions(calendar=self.calendar, isin_cash=self.ISIN_CASH)

        self.amount_df = data["amount"]
        self.prices_df = data["prices"]
        self.shares_df = data["shares"]
        self.nav_df = data["nav"]
        self.rets_df = data["returns"]

        return data

    def download_cashflows(self):
        """Download the cashflows into the positions and the cash position.
        """

        start = self.calendar[0]
        end = self.calendar[-1]

        cf = self.connector.get_cashflows(start, end, self.ISIN_CASH)
        
        cashflows_df = cf["cashflows"]
        cashflows_external_df = cf["cashflows_external"]
        
        self.cashflows_df = cashflows_df
        self.cashflows_external_df = cashflows_external_df

        return cashflows_df, cashflows_external_df

    def compute_monetary_fund(self):
        """Compute monetary fund returns.

        Notes
        -----
        To use the fund as an additional position, we can assume it 
        is invested in a monetary fund.  
        """
        # ??? : why the following is needed
        # I think I need to aggreagate the cashflows into the positions and the 
        # actual amount of cash in the monetary fund.
        cashflows_ss = self.cashflows_df.drop(columns=self.ISIN_CASH).sum(axis=1)
        
        cashflows_total_ss = (
            self.cashflows_external_df.set_index("date")["amount"]
            .reindex(cashflows_ss.index, fill_value=0.0)
            .add(cashflows_ss)
        )

        cash_calendar = cashflows_total_ss.index

        # Compute monetary fund daily return
        for today, yesterday in zip(cash_calendar[1:], cash_calendar):

            cash_today = self.amount_df.loc[today, self.ISIN_CASH]

            cash_yesterday = self.amount_df.loc[yesterday, self.ISIN_CASH]

            flows = cashflows_total_ss.loc[today]

            # Adjust in the numerator or the denominator?
            # Does it matter?
            self.rets_df.loc[today, self.ISIN_CASH] = (cash_today - flows) / cash_yesterday - 1

    def compute_time_series(self):
        """Compute general portfolio time series:

        1. Weights.
        2. Daily returns.
        3. Total return (adjusted for cashflows).

        From these one can compute most of 
        the performance and risk metrics. 
        """
        self.compute_weights()
        self.compute_return_daily()
        self.compute_return_total()

    def compute_weights(self):
        """Compute positions weights.

        Returns
        -------
        pd.DataFrame
            - Columns: position ISIN
            - Index: Datetime-like
            - Values: float
        """

        logging.info("Computing weights ...")

        _amount_df = self.amount_df

        weights_df = _amount_df.div(_amount_df.sum(axis=1), axis="index").shift(1)
        weights_df = weights_df.rename(columns={self.ISIN_CASH: "Cash"})
        weights_df.index.name = "Date"

        self.weights_df = weights_df.copy()

        return weights_df

    def compute_return_daily(self):
        """Compute portfolio daily returns.

        Returns
        -------
        pd.Series
            - Index: Datetime-like
            - Values: float
            - Name: returnDaily
        """
        logging.info("Computing daily returns ...")

        returns_ss = (self.rets_df * self.weights_df).dropna(how="all").sum(axis=1)
        returns_ss.index.name = "Date"
        returns_ss.name = "returnDaily"
        
        self.returns_ss = returns_ss.copy()

        return returns_ss

    def compute_return_total(self):
        """Compute portfolio total return. 

        Returns
        -------
        pd.Series
            - Index: Datetime-like
            - Values: float
            - Name: returnTotal
        """        
        logging.info("Computing total return ...")
        
        return_total_ss = self.returns_ss.add(1).cumprod().sub(1)
        return_total_ss.index.name = "Date"
        return_total_ss.name = "returnTotal"

        self.return_total_ss = return_total_ss.copy()

        return return_total_ss

    def build_portfolio(self, start = "20190101", end = None, calendar = None):
        """Integration method to compute portfolio time series.

        Invoking this method will connect to the broker API
        """

        # Download and process all positions
        self.get_timeseries_positions(start = start, end = end, calendar = calendar)
        
        # Compute cash evolution
        self.download_cashflows()
        self.compute_monetary_fund()

        # Portfolio time series
        self.compute_time_series()
