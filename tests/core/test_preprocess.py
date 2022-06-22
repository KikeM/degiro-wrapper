import numpy as np
import pandas as pd
from degiro_wrapper.conventions import PositionsRaw
from degiro_wrapper.core.preprocess import extract_numbers, replace_values
from pandas.testing import assert_frame_equal

TEMPLATE = {
    "Producto": {
        0: "CASH & CASH FUND & FTX CASH (EUR)",
        1: "AIRBUS GROUP",
        2: "ISHARES MSCI EUR A",
        3: "ISHARES MSCI WOR A",
        4: "SP 500 EH",
        5: "XTRACKERS II EUROZONE GOVERNMEN...",
    },
    "Symbol/ISIN": {
        0: np.nan,
        1: "NL0000235190",
        2: "IE00B4K48X80",
        3: "IE00B4L5Y983",
        4: "IE00B3ZW0K18",
        5: "LU0290355717",
    },
    "Cantidad": {0: np.nan, 1: 3.0, 2: 14.0, 3: 7.0, 4: 9.0, 5: 1.0},
    "Precio de": {
        0: np.nan,
        1: "100,98",
        2: "63,34",
        3: "74,48",
        4: "91,50",
        5: "229,44",
    },
    "Valor local": {
        0: "EUR 0.17",
        1: "EUR 302.94",
        2: "EUR 886.69",
        3: "EUR 521.33",
        4: "EUR 823.49",
        5: "EUR 229.44",
    },
    "Valor en EUR": {
        0: "0,17",
        1: "302,94",
        2: "886,69",
        3: "521,32",
        4: "823,49",
        5: "229,44",
    },
}


def test_replace_values():

    raw = pd.DataFrame(TEMPLATE)

    columns_to_clean = [
        PositionsRaw.PRICE,
        PositionsRaw.VALUE_EUR,
        PositionsRaw.VALUE_LOCAL,
    ]
    raw[columns_to_clean] = replace_values(
        frame=raw[columns_to_clean],
        old=",",
        new=".",
    )

    expected = {
        "Producto": {
            0: "CASH & CASH FUND & FTX CASH (EUR)",
            1: "AIRBUS GROUP",
            2: "ISHARES MSCI EUR A",
            3: "ISHARES MSCI WOR A",
            4: "SP 500 EH",
            5: "XTRACKERS II EUROZONE GOVERNMEN...",
        },
        "Symbol/ISIN": {
            0: np.nan,
            1: "NL0000235190",
            2: "IE00B4K48X80",
            3: "IE00B4L5Y983",
            4: "IE00B3ZW0K18",
            5: "LU0290355717",
        },
        "Cantidad": {0: np.nan, 1: 3.0, 2: 14.0, 3: 7.0, 4: 9.0, 5: 1.0},
        "Precio de": {
            0: np.nan,
            1: "100.98",
            2: "63.34",
            3: "74.48",
            4: "91.50",
            5: "229.44",
        },
        "Valor local": {
            0: "EUR 0.17",
            1: "EUR 302.94",
            2: "EUR 886.69",
            3: "EUR 521.33",
            4: "EUR 823.49",
            5: "EUR 229.44",
        },
        "Valor en EUR": {
            0: "0.17",
            1: "302.94",
            2: "886.69",
            3: "521.32",
            4: "823.49",
            5: "229.44",
        },
    }
    expected = pd.DataFrame(expected)

    assert_frame_equal(expected, raw)


def test_extract_numbers():

    raw = pd.DataFrame(TEMPLATE)

    columns_to_clean = [
        PositionsRaw.PRICE,
        PositionsRaw.VALUE_EUR,
        PositionsRaw.VALUE_LOCAL,
    ]
    raw[columns_to_clean] = replace_values(
        frame=raw[columns_to_clean],
        old=",",
        new=".",
    )

    columns_to_extract = [
        PositionsRaw.VALUE_EUR,
        PositionsRaw.VALUE_LOCAL,
    ]
    raw[columns_to_extract] = extract_numbers(raw[columns_to_extract])

    expected = {
        "Producto": {
            0: "CASH & CASH FUND & FTX CASH (EUR)",
            1: "AIRBUS GROUP",
            2: "ISHARES MSCI EUR A",
            3: "ISHARES MSCI WOR A",
            4: "SP 500 EH",
            5: "XTRACKERS II EUROZONE GOVERNMEN...",
        },
        "Symbol/ISIN": {
            0: np.nan,
            1: "NL0000235190",
            2: "IE00B4K48X80",
            3: "IE00B4L5Y983",
            4: "IE00B3ZW0K18",
            5: "LU0290355717",
        },
        "Cantidad": {0: np.nan, 1: 3.0, 2: 14.0, 3: 7.0, 4: 9.0, 5: 1.0},
        "Precio de": {
            0: np.nan,
            1: "100.98",
            2: "63.34",
            3: "74.48",
            4: "91.50",
            5: "229.44",
        },
        "Valor local": {
            0: "0.17",
            1: "302.94",
            2: "886.69",
            3: "521.33",
            4: "823.49",
            5: "229.44",
        },
        "Valor en EUR": {
            0: "0.17",
            1: "302.94",
            2: "886.69",
            3: "521.32",
            4: "823.49",
            5: "229.44",
        },
    }
    expected = pd.DataFrame(expected)

    assert_frame_equal(expected, raw)
