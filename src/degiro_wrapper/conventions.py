FILENAME_POSITIONS = "positions_%Y-%m-%d"


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


class Credentials:

    SESSION_ID = "sessionId"
    ACCOUNT_ID = "intAccount"
