from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests
from core.common.global_data_classes import Databases
from core.db.db_connector import PostgresConnector


def binance_get_prices():
    # connecting to binance api and requesting crypto prices
    base_url = "https://api.binance.com/api/v3"
    endpoint = "/ticker/price"

    url = f"{base_url}{endpoint}"
    response = requests.get(url)
    response.raise_for_status()

    data = response.json()
    df = pd.DataFrame.from_dict(data, orient="columns")

    return df


def crypto_prices_eur_conversion(crypto_df, binance_df, proxy_symbol):
    # function used to recalculate prices to EUR based on chosen proxy symbol
    crypto_df["binance_symbol"] = crypto_df["symbol"] + proxy_symbol
    prices_df = binance_df.copy()
    prices_cryptos = set(prices_df["symbol"])
    our_cryptos = set(crypto_df["binance_symbol"])
    common_cryptos = our_cryptos.intersection(prices_cryptos)
    if proxy_symbol != "EUR":
        conv_symbol = proxy_symbol + "EUR"
        common_cryptos.add(conv_symbol)

    # preparing dataframe for conversion
    prices_df.set_index("symbol", inplace=True)
    df = prices_df.loc[list(common_cryptos), :]
    df.reset_index(inplace=True)

    # converting price to EUR
    df["price"] = df["price"].astype(float) * 100
    conv_rate = (
        df[df["symbol"] == conv_symbol]["price"].astype(float).values[0]
        if proxy_symbol != "EUR"
        else 100
    )
    df["close"] = df["price"] * conv_rate / 100

    df["symbol"] = df["symbol"].str.replace(proxy_symbol, "")
    df = df.merge(crypto_df[["symbol", "instrument_id"]], on="symbol")

    return df


def binance_live_prices_handler():
    """As not all cryptos have a EUR price directly
    return by the binance endpoint, we use additional
    tokens as a conversion proxy"""

    # getting cryptos list from sql
    sql = PostgresConnector.read_query_from_file(
        Path(__file__).parent / "queries/crypto_list.sql",
    )
    crypto_df = PostgresConnector(Databases.delta_replica).sql_to_pandas(sql)

    # getting crypto prices from binance
    binance_df = binance_get_prices()

    # adding recaluclated prices to final dataframe
    conv_dfs_list = []
    proxy_symbols = ["EUR", "BTC", "BNB"]
    for symbol in proxy_symbols:
        conv_df = crypto_prices_eur_conversion(
            crypto_df=crypto_df, binance_df=binance_df, proxy_symbol=symbol
        )
        conv_dfs_list.append(conv_df)
        conv_list = conv_df["symbol"].tolist()
        crypto_df = crypto_df[~crypto_df["symbol"].isin(conv_list)]

    final_df = pd.concat(conv_dfs_list)
    final_df["currency"] = "EUR"
    final_df["volume"] = 1
    final_df["date"] = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    final_df.reset_index(inplace=True)
    final_df.drop(columns=["index", "price"], inplace=True)

    missing_cryptos = crypto_df["symbol"].tolist()

    # uploading data to table
    PostgresConnector(Databases.delta_main).copy_expert_from_pandas(
        final_df,
        "binance_live_prices",
        update_on_conflict=True,
        constraint_cols=["instrument_id", "date"],
    )

    msg = f"{len(final_df)} records uploaded. Missing prices for following cryptos: {missing_cryptos}"

    return msg


if __name__ == "__main__":
    # binance_df = binance_get_prices()

    # df_test = crypto_prices_eur_conversion(
    #   binance_df=binance_df,
    #   crypto_df=crypto_df,
    #   proxy_symbol='BNB')
    # print(df_test)

    msg_test = binance_live_prices_handler()
    print(msg_test)
