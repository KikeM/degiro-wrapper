import configparser
import getpass
import json
import pathlib
import urllib.request

import pandas as pd
import requests
import tqdm
from degiro_wrapper.conventions import FILENAME_POSITIONS, Credentials

from .api_endpoints import (
    url_account,
    url_info_client,
    url_login,
    url_positions,
    url_transactions,
)


def get_config(fname):
    """Read credentials from config file.

    Parameters
    ----------
    fname : str
        Complete path to config file.

    Returns
    -------
    config : config
    """
    config = configparser.ConfigParser()
    _fname = pathlib.Path(fname).expanduser().absolute()
    config.read(_fname)
    return config


def get_session_id(username=None, password=None, config=False):
    """Get sessionId for a username and password.

    Parameters
    ----------
    username: str
    password: str

    Returns
    -------
    str
    """
    sess = requests.Session()

    # Prepare payload
    _payload = {"isPassCodeReset": False, "isRedirectToMobile": False}

    _need_username = username is None and not config
    _need_password = password is None and not config

    if config:
        config = get_config(config)
        username = config["LOGIN"]["username"]
        password = config["LOGIN"]["password"]

    if _need_username or _need_password:

        _payload["username"] = input("Username: ")
        _payload["password"] = getpass.getpass()

    else:

        _payload["username"] = username
        _payload["password"] = password

    _payload = json.dumps(_payload)

    #  Prepare header
    _header = {"content-type": "application/json"}

    # Request access
    _response = sess.post(url=url_login, headers=_header, data=_payload)

    if not _response.ok:
        print(_response.text)
        raise SystemExit("Unable to retrive intAccount value.")

    sess.close()

    return _response.headers["Set-Cookie"].split(";")[0].split("=")[-1]


def get_int_account(session_id=None):
    """Get intAccount values for a sessionId value.

    Parameters
    ----------
    sessionID: str

    Returns
    -------
    int
    """
    sess = requests.Session()

    _payload = {Credentials.SESSION_ID: session_id}

    _response = sess.get(url=url_info_client, params=_payload)

    if not _response.ok:
        print(_response.text)
        raise SystemExit("Unable to retrive intAccount value.")

    _config_dict = _response.json()

    sess.close()

    return _config_dict["data"][Credentials.ACCOUNT_ID]


def get_login_data(config=False):
    """Get sessionId and intAccount values for a username and a password.

    Parameters
    ----------
    username: str
    password: str

    Returns
    -------
    user_data: dict
        - 'intAccount': int
        - 'sessionId': str
    """
    session_id = get_session_id(config=config)
    int_account = get_int_account(session_id)

    credentials = dict()

    credentials[Credentials.SESSION_ID] = session_id
    credentials[Credentials.ACCOUNT_ID] = int_account

    return credentials


def download_positions_raw(
    calendar,
    path,
    credentials,
    filename_template=FILENAME_POSITIONS,
):
    """Dowload positions CSV files.

    Parameters
    ----------
    calendar: pandas.DatetimeIndex
    path: Path-like object
    data: dict
        - 'intAccount'
        - 'sessionId'
    filename_template: str
        By default 'positions_%Y-%m-%d',
        see degiro_wrapper.conventions::FILENAME_POSITIONS
    """
    for date in tqdm.tqdm(calendar):

        filename = date.strftime(filename_template) + ".csv"

        url_formatted = url_positions.format(
            int_account=credentials[Credentials.ACCOUNT_ID],
            session_id=credentials[Credentials.SESSION_ID],
            day=date.strftime("%d"),
            month=date.strftime("%m"),
            year=date.strftime("%Y"),
        )

        _path = path / filename
        urllib.request.urlretrieve(url_formatted, _path)


def download_cashflows_raw(credentials, start, end, path):
    """Download positions and cash flows.

    Parameters
    ----------
    credentials : dict
    start : str or Datetime-like
    end : str or Datetime-like
    path : Path-like

    Returns
    -------
    path : Path-like
    """
    # Parse dates
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # Format download URL
    url_account_formatted = url_account.format(
        int_account=credentials[Credentials.ACCOUNT_ID],
        session_id=credentials[Credentials.SESSION_ID],
        day_i=start.strftime("%d"),
        month_i=start.strftime("%m"),
        year_i=start.strftime("%Y"),
        day_f=end.strftime("%d"),
        month_f=end.strftime("%m"),
        year_f=end.strftime("%Y"),
    )

    # Download account file
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    path = path / f"cashflows_{start}_{end}.csv"
    path, _ = urllib.request.urlretrieve(url_account_formatted, path)

    return path


def download_transactions_raw(credentials, start, end, path):
    """Download transactions CSV file.

    Parameters
    ----------
    credentials : dict
    start : str or Datetime-like
    end : str or Datetime-like
    path : Path-like

    Returns
    -------
    path : Path-like
    """
    # Parse dates
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)

    # Format download URL
    url_transactions_formatted = url_transactions.format(
        int_account=credentials[Credentials.ACCOUNT_ID],
        session_id=credentials[Credentials.SESSION_ID],
        day_i=start.strftime("%d"),
        month_i=start.strftime("%m"),
        year_i=start.strftime("%Y"),
        day_f=end.strftime("%d"),
        month_f=end.strftime("%m"),
        year_f=end.strftime("%Y"),
    )

    # Download account file
    start = start.strftime("%Y-%m-%d")
    end = end.strftime("%Y-%m-%d")
    path = path / f"transactions_{start}_{end}.csv"
    path, _ = urllib.request.urlretrieve(url_transactions_formatted, path)

    return path
