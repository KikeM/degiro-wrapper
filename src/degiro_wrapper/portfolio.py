import datetime
import logging
from pathlib import Path

import pandas as pd

import degiro_wrapper as dw


class Portfolio():

    def __init__(self, path_config = "~/degiro-wrapper/degiro.ini"):

        self.path_config = Path(path_config)
        self.config_section = "DEGIRO"

        self.ISIN_CASH = dw.conventions.ISIN_CASH

        # Initialize variables
        self.config = None
        self.user_data = None

        self.amount_df = None
        self.prices_df = None
        self.shares_df = None
        self.nav_df = None
        self.rets_df = None

    def load_configuration(self, path_config = None):
        """Read configuration file.
        """
        logging.info("Reading config.")
        if path_config is None:
            _path = self.path_config
        else:
            _path = Path(path_config)

        config = dw.api_methods.get_config(_path)
        
        self.config = config

        return config

    def get_user_data(self, config = None):

        if config is None:
            _config = self.config
        else:
            _config = config

        user_data = dw.api_methods.get_login_data(config=_config)

        self.user_data = user_data

        return user_data

    def download_positions(self, start, end = None, calendar = None, template = "pos_%Y%m%d"):
        """Download portfolio positions. 

        Parameters
        ----------
        start: "YYMMDD", Datetime-like

        end: "YYMMDD", Datetime-like

        calendar: Datetime-like Index
            This variable overrides start and end.

        template: str
            Template for the position filenames.
            Datetime.strftime(template) will be called.

        Returns
        -------
        None

        Notes
        -----
        If no end is specified, used today's date. 
        """
        # Location to download the xls files.
        path_assets = self.get_path_assets()
        user_data = self.get_user_data()

        # Dates to query the broker for the dates
        if calendar is None:
            calendar = self._create_daily_calendar(start, end)

        self.calendar = calendar

        logging.info("Downloading data")
        dw.api_methods.download_positions(
            calendar=calendar,
            path=path_assets,
            data=user_data,
            filename_template=template,
        )

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

    def get_path_assets(self):
        """Get path for folder to store assets.

        Returns
        -------
        Path-like

        Notes
        -----
        If the folder does not exist it will be created. 
        """
        logging.info("Retrieving assets folder path ...")
        path = Path(self.config[self.config_section]["files_dir"]).expanduser().absolute()

        # Create folder and parents if they do not exist
        if not path.exists():
            logging.info(f"Creating assets folder path at {path}")
            path.mkdir(parents = True)

        return path

    def preprocess_positions(self, path_assets = None, template = "pos_*.xls"):
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
        if path_assets is None:
            _path = self.get_path_assets()
        else:
            _path = path_assets

        positions_raw_df = dw.preprocess.positions_xls_to_df(path = _path, isin_cash=self.ISIN_CASH, glob=template)

        cleaned_data = dw.preprocess.positions_raw_to_clean(positions_raw_df)

        self.amount_df = cleaned_data["amount"]
        self.prices_df = cleaned_data["prices"]
        self.shares_df = cleaned_data["shares"]
        self.nav_df = cleaned_data["nav"]
        self.rets_df = cleaned_data["returns"]

        return cleaned_data

    def download_cashflows(self, path = None):
        """Download the cashflows into the positions and the cash position.

        Parameters
        ----------
        path: Path-like
            Location to download the file.

        Notes
        -----
        If no path is provided, it will be downloaded to the assets folder.
        """
        if path is None:
            _path = self.get_path_assets()
        else:
            _path = path

        date_start = self.calendar[0]
        date_end = self.calendar[-1]

        # Download Account file
        path_account = dw.api_methods.download_cashflows(self.user_data, date_start, date_end, _path)

        # Separate cashflows into internal cashflows and external cashflows
        cf = dw.preprocess.generate_cashflows(path_account=path_account, isin_cash=self.ISIN_CASH)
        
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

    def build_portfolio(self, start = "20190101"):
        """Integration method to compute portfolio time series.

        Invoking this method will connect to the broker API
        """

        # Get API user headers
        self.load_configuration()

        # Download and process all positions
        self.download_positions(start = start)
        self.preprocess_positions()
        
        # Compute cash evolution
        self.download_cashflows()
        self.compute_monetary_fund()

        # Portfolio time series
        self.compute_time_series()
