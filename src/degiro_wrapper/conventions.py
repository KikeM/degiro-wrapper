from turtle import position


FILENAME_POSITIONS = "positions_%Y-%m-%d"


class Credentials:

    SESSION_ID = "sessionId"
    ACCOUNT_ID = "intAccount"


class AssetType:

    ASSET = "asset"
    CASH = "cash"


class Positions:

    DATE = "date"
    NAME = "name"
    ISIN = "ISIN"
    SHARES = "shares"
    PRICE = "price"
    TYPE = "type"
    VALUE_LOCAL = "valueLocal"
    VALUE_PORTFOLIO = "valuePortfolio"


class PositionsRaw:

    PRODUCT = "Producto"
    ISIN = "Symbol/ISIN"
    QUANTITY = "Cantidad"
    PRICE = "Precio de"
    VALUE_LOCAL = "Valor local"
    VALUE_EUR = "Valor en EUR"


class CashflowsRaw:

    DELTA = "Variación"
    UNNAMED_DELTA = "Unnamed: 8"
    AMOUNT = "Saldo"
    UNNAMED_AMOUNT = "Unnamed: 10"
    DATE_VALUE = "Fecha valor"
    DESCRIPTION = "Descripción"
    DATE = "Fecha"
    TIME = "Hora"
    PRODUCT = "Producto"
    TYPE = "Tipo"
    ID = "ID Orden"


class Cashflows:

    DELTA = "delta"
    DELTA_CCY = "deltaCcy"
    AMOUNT = "amount"
    AMOUNT_CCY = "amountCcy"
    DATE = "date"
    DATE_VALUE = "dateValue"
    DESCRIPTION = "description"
    TIME = "time"
    TYPE = "type"
    ID = "id"


class CashflowType:

    BUY = "BUY"
    SELL = "SELL"
    RAW_COMPRA = "Compra"
    RAW_VENTA = "Venta"


class TransactionsRaw:

    EXCHANGE = "Bolsa de"
    EXECUTION = "Centro de ejecución"
    RATE = "Tipo de cambio"
    PRICE = "Precio"
    UNNAMED_PRICE = "Unnamed: 8"
    VALUE_LOCAL = "Valor local"
    UNNAMED_VALUE_LOCAL = "Unnamed: 10"
    VALUE = "Valor"
    UNNAMED_VALUE = "Unnamed: 12"

    TRANSACTION_COSTS = "Costes de transacción"
    UNNAMED_COSTS = "Unnamed: 15"

    TOTAL = "Total"
    UNNAMED_TOTAL = "Unnamed: 17"

    SHARES = "Número"

    DATE = "Fecha"
    TIME = "Hora"
    PRODUCT = "Producto"
    TYPE = "Tipo"
    ID = "ID Orden"


class Transactions:

    EXCHANGE = "exchange"
    EXECUTION = "exchangeExecution"
    RATE = "fxRate"
    AMOUNT_CCY = "amountCcy"
    SHARES = "shares"

    PRICE = "price"
    PRICE_CCY = "priceCcy"

    VALUE_LOCAL = Positions.VALUE_LOCAL
    VALUE_LOCAL_CCY = VALUE_LOCAL + "Ccy"

    VALUE = Positions.VALUE_PORTFOLIO
    VALUE_CCY = VALUE + "Ccy"

    TRANSACTION_COSTS = "costsTransaction"
    TRANSACTION_COSTS_CCY = "costsTransactionCcy"

    TOTAL = "total"
    TOTAL_CCY = "totalCcy"

    DATE = "date"
    DATE_VALUE = "dateValue"
    TIME = "time"
    TYPE = "type"
    ID = "id"
