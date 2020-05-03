import configparser
import datetime
import getpass
import json
import logging
import pathlib
import urllib.request
from pathlib import Path

import pandas as pd
import requests
import tqdm

from .api_endpoints import (url_account, url_info_client, url_login,
                            url_positions)


class ConnectorDegiro():
    
    def __init__(self, path_config, username = None, password = None):
        
        self.config_section = "DEGIRO"

        self.template_download = "positions_%Y%m%d"
        self.template_parse = "positions_*.xls"

        self.path_config = Path(path_config)
        
        self.config = None
        self.user_data = None
        self.path_account = None

        # Try to read config file
        try:
            self.get_config()
        except:
            self.config = None

        # Get login data
        self.get_login_data(username=username, password=password, config=self.config)

    def get_config(self, fname = None):
        """Read credentials from config file.

        Parameters
        ----------
        fname : str
            Complete path to config file.

        Returns
        -------
        config : config
        """

        if fname is None:
            _fname = self.path_config
        else:
            _fname = fname
        config = configparser.ConfigParser()
        _fname = pathlib.Path(_fname).expanduser().absolute()
        config.read(_fname)

        self.config = config

        logging.info("Config file processed")
        return config

    def get_session_id(self, username=None, password=None, config=False):
        """Get sessionId for a username and password.

        Parameters
        ----------
        username: str
        password: str
        config : config

        Returns
        -------
        str
        """

        # Prepare payload
        _payload = {"isPassCodeReset": False, "isRedirectToMobile": False}

        _need_username = username is None and not config
        _need_password = password is None and not config

        if config:
            username = config["DEGIRO"]["username"]
            password = config["DEGIRO"]["password"]
            logging.info("Config loaded correctly for user: %s." % username)

        if _need_username or _need_password:
            _payload["username"] = input("Username: ")
            _payload["password"] = getpass.getpass()
        else:
            _payload["username"] = username
            _payload["password"] = password

        _payload = json.dumps(_payload)
        _header = {"content-type": "application/json"}

        with requests.Session() as sess:
            _response = sess.post(url=url_login, headers=_header, data=_payload)

        if not _response.ok:
            logging.error(_response.text)
            raise SystemExit("Unable to retrive intAccount value.")

        return _response.headers["Set-Cookie"].split(";")[0].split("=")[-1]

    def get_int_account(self, session_id=None):
        """Get intAccount values for a sessionId value.

        Parameters
        ----------
        sessionID: str

        Returns
        -------
        int
        """

        _payload = {"sessionId": session_id}

        with requests.Session() as sess:
            _response = sess.get(url=url_info_client, params=_payload)

        if not _response.ok:
            logging.error(_response.text)
            raise SystemExit("Unable to retrive intAccount value.")

        _config_dict = _response.json()

        return _config_dict["data"]["intAccount"]

    def get_login_data(self, username=None, password=None, config=False):
        """
        Get sessionId and intAccount values for a username and a password.

        Parameters
        ----------
        username: str
        password: str
        config: dict-like

        Returns
        -------
        user_data: dict
            - "intAccount": int
            - "sessionId": str
        """
        session_id = self.get_session_id(username, password, config)
        int_account = self.get_int_account(session_id)

        user_data = dict()

        user_data["sessionId"] = session_id
        user_data["intAccount"] = int_account

        self.user_data = user_data

        return user_data

    def download_positions(self, calendar):
        """Dowload positions Excel files.

        Parameters
        ----------
        calendar: Timestamps iterable
        """

        # Loop through dates in the calendar. 
        for _date in tqdm.tqdm(calendar):

            _filename = _date.strftime(self.template_download) + ".xls"
            _file = self.path_assets / _filename
            if _file.exists():
                continue  # early stop

            url_formated = url_positions.format(
                int_account=self.user_data["intAccount"],
                session_id=self.user_data["sessionId"],
                day=_date.strftime("%d"),
                month=_date.strftime("%m"),
                year=_date.strftime("%Y"),
            )

            urllib.request.urlretrieve(url_formated, _file)

    def download_cashflows(self, start, end, path_account):
        """Download cash and positions flows.

        Parameters
        ----------
        user_date: dict
        date_start: str or Datetime-like
        date_end: str or Datetime-like
        path_account: Path-like to folder

        Returns
        -------
        path_account: Path-like
        """
        # Parse dates
        start = pd.to_datetime(start)
        end = pd.to_datetime(end)

        # Format download URL
        url_account_formated = url_account.format(
            int_account=self.user_data["intAccount"],
            session_id=self.user_data["sessionId"],
            day_i=start.strftime("%d"),
            month_i=start.strftime("%m"),
            year_i=start.strftime("%Y"),
            day_f=end.strftime("%d"),
            month_f=end.strftime("%m"),
            year_f=end.strftime("%Y"),
        )

        # Download account file
        path_account_file, _ = urllib.request.urlretrieve(
            url_account_formated, path_account / "Account.xls"
        )

        return path_account_file

    def preprocess_cashflows(self, isin_cash):
        """Generate cash and positions flows.

        Parameters
        ----------
        isin_cash : str

        Returns
        -------
        out : dict
            account, cashflows, cashflows_external
        """
        # Read and parse
        raw_df = pd.read_excel(self.path_account)
        raw_df = raw_df.rename(
            columns={
                "Variación": "ccyDelta",
                "Unnamed: 8": "delta",
                "Saldo": "ccyAmount",
                "Unnamed: 10": "amount",
                "Fecha valor": "date",
            }
        )

        raw_df["date"] = pd.to_datetime(raw_df["date"], dayfirst=True)
        account_df = raw_df.drop(
            columns=["Fecha", "Hora", "Producto", "Tipo", "ID Orden"]
        )

        # Generate changes in position
        deltas_df = account_df.groupby(["date", "ISIN", "amount"])["delta"].sum()
        deltas_df = pd.DataFrame(deltas_df).reset_index()

        # Compute cashflows
        cashflows_df = deltas_df.pivot_table(
            index="date", columns="ISIN", values="delta", aggfunc="sum"
        )

        # Compute external cashflows
        cashflows_external_df = account_df.loc[
            account_df["Descripción"].isin(["Ingreso", "Retirada"])
        ]

        # For some reason DEGIRO has the cashflows mark to market shifted by one.
        # and my guess is that unless there is a position transaction, they dont
        # write cash mark to markets on Fridays ...
        cashflows_df = cashflows_df.asfreq("D")
        cashflows_df[isin_cash] = cashflows_df[isin_cash].shift()
        cashflows_df = cashflows_df.asfreq("B")

        out = dict(
            account=account_df,
            cashflows=cashflows_df,
            cashflows_external=cashflows_external_df,
        )

        return out

    def preprocess_positions(self, positions):
        """From raw positions to date/index-value/column style.

        Parameters
        ----------
        positions: pd.DataFrame

        Returns
        -------
        out : dict
            amount : position size
            prices : close price
            shares : number of participations
            nav : Net Assets Value, position / shares value
            returns : NAV returns

        Notes
        -----
        It does not contain the returns of the cash position.
        """

        # TODO: take into account short positions. 

        amount_df = positions.pivot(
            index="date", columns="ISIN", values="amount"
        )
        prices_df = positions.pivot(
            index="date", columns="ISIN", values="price"
        )
        shares_df = positions.pivot(
            index="date", columns="ISIN", values="shares"
        )

        # Compute share-adjusted values
        nav_df = (amount_df / shares_df).dropna(axis=1, how="all")

        # Compute daily returns
        returns_df = nav_df.pct_change(limit=1)

        # Put on a business day basis
        amount_df = amount_df.asfreq("B")
        prices_df = prices_df.asfreq("B")
        shares_df = shares_df.asfreq("B")
        nav_df = nav_df.asfreq("B")
        returns_df = returns_df.asfreq("B")

        out = dict(
            amount=amount_df,
            prices=prices_df,
            shares=shares_df,
            returns=returns_df,
            nav=nav_df,
        )

        return out

    def xls_to_df(self, isin_cash):
        """
        Parse positions xls files to DataFrame.

        Parameters
        ----------
        path: Path-like object
        isin_cash: str

        Returns
        -------
        pd.DataFrame
        """
        columnas = [
            "Fecha",
            "Producto",
            "Symbol/ISIN",
            "Cantidad",
            "Precio de ",
            "Valor local",
            "Valor en EUR",
        ]

        df = pd.DataFrame(columns=columnas)

        # TODO: use start and end to only parse the necessary data
        for _file in self.path_assets.glob(self.template_parse):

            # Read _file
            df_day = pd.read_excel(_file)

            # Get positions date
            df_day["Fecha"] = _file.stem.split("_")[-1]

            # Append to dataframe
            df = df.append(df_day, sort=False)

        df["Fecha"] = pd.to_datetime(df["Fecha"])
        df = df.reset_index(drop=True)
        map_columnas = {
            "Fecha": "date",
            "Producto": "product",
            "Symbol/ISIN": "ISIN",
            "Cantidad": "shares",
            "Precio de ": "price",
            "Valor local": "amount_to_drop",
            "Valor en EUR": "amount",
        }

        df = df.rename(columns=map_columnas)
        df = df.drop(columns="amount_to_drop")

        # Add position type
        mask_has_isin = df["ISIN"].notna()

        df.loc[mask_has_isin, "type"] = "long"
        df.loc[~mask_has_isin, "type"] = "cash"

        df["ISIN"] = df["ISIN"].fillna(isin_cash)
        df = df.sort_values(by="date")

        return df

    def get_positions(self, calendar, isin_cash):
        """Get portfolio positions time series.

        Parameters
        ----------
        calendar:
        isin_cash: str

        Returns
        -------
        out : dict
            amount : position size
            prices : close price
            shares : number of participations
            nav : Net Assets Value, position / shares value
            returns : NAV returns
        """
        self.download_positions(calendar=calendar)
        positions_raw = self.xls_to_df(isin_cash=isin_cash)
        out = self.preprocess_positions(positions=positions_raw)

        return out

    def get_cashflows(self, start, end, isin_cash):
        """Get cash and positions flows.

        Parameters
        ----------
        start: str, Datetime-like
        end: str, Datetime-like
        isin_cash : str

        Returns
        -------
        out : dict
            account, cashflows, cashflows_external
        """
        self.path_account = self.download_cashflows(start, end, self.path_assets)
        
        return self.preprocess_cashflows(isin_cash)

    @property
    def path_assets(self):
        """Get path for folder to store assets.

        Returns
        -------
        Path-like

        Notes
        -----
        If the folder does not exist it will be created. 
        """
        path = Path(self.config[self.config_section]["files_dir"]).expanduser().absolute()

        # Create folder and parents if they do not exist
        if not path.exists():
            logging.info(f"Creating assets folder path at {path}")
            path.mkdir(parents = True)

        return path
