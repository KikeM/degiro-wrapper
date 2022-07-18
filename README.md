# Welcome to the Degiro Wrapper
Degiro broker wrapper and portfolio valuator.

*README under construction.*

**Currently under changes, stable releases will be put up soon**.

- [Welcome to the Degiro Wrapper](#welcome-to-the-degiro-wrapper)
  - [How to install](#how-to-install)
  - [How to use](#how-to-use)

## How to install

```bash
pip install .
```

## How to use

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

# Disclaimer

If you require any more information or have any questions about our site's disclaimer, please feel free to contact us 
at https://github.com/KikeM/degiro-wrapper/issues.

All the information on this website - https://github.com/KikeM/degiro-wrapper - is published in good faith and for general information purpose only. `degiro-wrapper` does not make any warranties about the completeness, reliability and accuracy of this information. Any action you take upon the information you find with this tool (`degiro-wrapper`), is strictly at your own risk. `degiro-wrapper` will not be liable for any losses and/or damages in connection with the use of our website.

From our website, you can visit other websites by following hyperlinks to such external sites. While we strive to provide only quality links to useful and ethical websites, we have no control over the content and nature of these sites. These links to other websites do not imply a recommendation for all the content found on these sites. Site owners and content may change without notice and may occur before we have the opportunity to remove a link which may have gone 'bad'.

Please be also aware that when you leave our website, other sites may have different privacy policies and terms which are beyond our control. Please be sure to check the Privacy Policies of these sites as well as their "Terms of Service" before engaging in any business or uploading any information.

### Consent
By using our website and tool, you hereby consent to our disclaimer and agree to its terms.

### Update
Should we update, amend or make any changes to this document, those changes will be prominently posted here.

