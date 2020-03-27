# Welcome to the Degiro Wrapper
Degiro broker wrapper and *soon* portfolio valuator.

# How to install

```bash
pip install -r requirements.txt
```


## How to use

For the run `src/sandbox.ipynb`. When you call `get_login_data` 
you will be prompted for your username and password (using getpass,
so that your password won't show ;)

Cheers

# Developper's corner
Specific details for contribution are given.

## How to build the requirements file
If you carry out changes or use new libraries, you can easily update the `requirements.txt` file with the following command:
```bash
pipdeptree | grep '^\w' > requirements.txt
```