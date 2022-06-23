# Welcome to the Degiro Wrapper
Degiro broker wrapper and portfolio valuator.

*README under construction.*

**Currently under changes, stable releases will be put up soon**.

- [Welcome to the Degiro Wrapper](#welcome-to-the-degiro-wrapper)
  - [How to install](#how-to-install)

## How to install

```bash
pip install .
```

## How to use

This library creates a CLI, invoked with the command `degiro`.

```
$ degiro
Usage: degiro [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  check-missing-dates     Check missing dates YTD from raw positions.
  create-db-cashflows     Create DB-cashflows from raw cashflows file.
  create-db-positions     Create positions database from raw positions...
  create-db-transactions  Create DB-transactions from raw transactions file.
  describe
  download-cashflows      Download raw cashflows from Degiro.
  download-positions      Download raw positions from Degiro.
  download-transactions   Download raw transactions from Degiro.
  report                  Create general report.
```
Currently there is a basic report available with three time series:
- Total Net Assets;
- portfolio cashflows;
- cumulative return in %.



