###########
# Login
###########
url_login = "https://trader.degiro.nl/login/secure/login"

#############
# Client info
#############
url_info_client = "https://trader.degiro.nl/pa/secure/client"

###########
# Positions
###########
url_positions = "https://trader.degiro.nl/reporting/secure/v3/positionReport/csv"
url_positions += "?intAccount={int_account}"
url_positions += "&sessionId={session_id}"
url_positions += "&country=ES"
url_positions += "&lang=es"
url_positions += "&toDate={day}%2F{month}%2F{year}"

##############
# Cash Account
##############
url_account = "https://trader.degiro.nl/reporting/secure/v3/cashAccountReport/csv"
url_account += "?intAccount={int_account}"
url_account += "&sessionId={session_id}"
url_account += "&country=ES"
url_account += "&lang=es"
url_account += "&fromDate={day_i}%2F{month_i}%2F{year_i}"
url_account += "&toDate={day_f}%2F{month_f}%2F{year_f}"

##############
# Transactions
##############
url_transactions = "https://trader.degiro.nl/reporting/secure/v3/transactionReport/csv"
url_transactions += "?intAccount={int_account}"
url_transactions += "&sessionId={session_id}"
url_transactions += "&country=ES"
url_transactions += "&lang=es"
url_transactions += "&fromDate={day_i}%2F{month_i}%2F{year_i}"
url_transactions += "&toDate={day_f}%2F{month_f}%2F{year_f}"
