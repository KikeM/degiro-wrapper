import json
import getpass
import logging
import pathlib
import configparser
import urllib.request

import tqdm
import requests
import pandas as pd

from .api_endpoints import (
    url_account,
    url_info_client,
    url_login,
    url_positions,
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
    logging.info("Config file processed")
    return config


def get_session_id(username=None, password=None, config=False):
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


def get_int_account(session_id=None):
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


def get_login_data(username=None, password=None, config=False):
    """
    Get sessionId and intAccount values for a username and a password.

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

    user_data = dict()

    user_data["sessionId"] = session_id
    user_data["intAccount"] = int_account

    return user_data


def download_positions(
    calendar, path, data, filename_template="positions_%Y%m%d"
):
    """Dowload positions Excel files.

    Parameters
    ----------
    calendar: Timestamps iterable
    path: Path-like object
    data: dict
        - 'intAccount'
        - 'sessionId'
    filename_template: str
        'XXXXX_%Y%m%d'
    """
    for _date in tqdm.tqdm(calendar):

        _filename = _date.strftime(filename_template) + ".xls"
        _file = path / _filename
        if _file.exists():
            continue  # early stop

        url_formated = url_positions.format(
            int_account=data["intAccount"],
            session_id=data["sessionId"],
            day=_date.strftime("%d"),
            month=_date.strftime("%m"),
            year=_date.strftime("%Y"),
        )

        urllib.request.urlretrieve(url_formated, _file)


def download_cashflows(user_data, date_start, date_end, path_account):
    """Download positions and cash flows.

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
    date_start = pd.to_datetime(date_start)
    date_end = pd.to_datetime(date_end)

    # Format download URL
    url_account_formated = url_account.format(
        int_account=user_data["intAccount"],
        session_id=user_data["sessionId"],
        day_i=date_start.strftime("%d"),
        month_i=date_start.strftime("%m"),
        year_i=date_start.strftime("%Y"),
        day_f=date_end.strftime("%d"),
        month_f=date_end.strftime("%m"),
        year_f=date_end.strftime("%Y"),
    )

    # Download account file
    path_account, _ = urllib.request.urlretrieve(
        url_account_formated, path_account / "Account.xls"
    )

    return path_account
