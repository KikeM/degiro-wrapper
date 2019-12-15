from api_endpoints import url_login, url_info_client, url_positions
import requests
import getpass
import json

import pandas as pd
import urllib.request
import tqdm

def get_session_id(username = None, password = None):
    """
    Get sessionId for a username and password.
    
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
    _payload = {'isPassCodeReset': False,
                'isRedirectToMobile': False}
    
    _need_username = username is None
    _need_password = password is None
    
    if _need_username or _need_password:
        
        _payload['username'] = input('Input username')
        _payload['password'] = getpass.getpass()
        
    else:
        
        _payload['username'] = username
        _payload['password'] = password
        
    _payload = json.dumps(_payload)

    # Prepare header
    _header = {'content-type': 'application/json'}

    # Request access
    _response = sess.post(url     = url_login, 
                          headers = _header, 
                          data    = _payload)
    
    if _response.ok != True:
        print(_response.text)
        raise SystemExit('Unable to retrive intAccount value.')
    
    sess.close()

    return _response.headers['Set-Cookie'].split(';')[0].split('=')[-1]

def get_int_account(session_id = None):
    """
    Get intAccount values for a sessionId value.
    
    Parameters
    ----------
    sessionID: str
    
    Returns
    -------
    int
    """
    sess = requests.Session()
    
    _payload = {'sessionId': session_id}
    
    print(_payload)
    
    _response = sess.get(url    = url_info_client, 
                         params = _payload)
    
    if _response.ok != True:
        print(_response.text)
        raise SystemExit('Unable to retrive intAccount value.')
    
    _config_dict = _response.json()
    
    sess.close()
    
    return _config_dict['data']['intAccount']

def get_login_data(username = None, password = None):
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
    session_id  = get_session_id()
    int_account = get_int_account(session_id)
    
    user_data = dict()
    
    user_data['sessionId']  = session_id
    user_data['intAccount'] = int_account
    
    return user_data

def download_positions(calendar, path, data, filename_template = 'positions_%Y%m%d'):
    """
    Dowload positions Excel files.
    
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

        _filename = _date.strftime(filename_template) + '.xls'

        url_formated = url_positions.format(int_account = data['intAccount'], 
                                            session_id  = data['sessionId'], 
                                            day         = _date.strftime('%d'), 
                                            month       = _date.strftime('%m'), 
                                            year        = _date.strftime('%Y'))

        urllib.request.urlretrieve(url_formated, path / _filename)