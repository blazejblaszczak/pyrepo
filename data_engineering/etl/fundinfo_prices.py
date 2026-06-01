from datetime import datetime
from pathlib import Path

import pandas as pd
import requests
from core.common.decorators import retry
from core.common.global_data_classes import Databases
from core.common.logging_base import logger_de
from core.common.ssm_env.settings import ENV_API_KEY, ENV_LOGIN
from core.db.db_connector import PostgresConnector
from dateutil.relativedelta import relativedelta


def get_fundinfo_headers():
    return {"login": ENV_LOGIN, "password": ENV_API_KEY}


@retry()
def fundinfo_details_handler():
    """
    FUNDINFO DOCS: https://services.opcvm360.com/en/api-v1-doc/overview
    """
    url = "https://services.opcvm360.com/api-v1/"
    headers = get_fundinfo_headers()

    # get mutual funds ISINs from instruments table
    funds_sql = PostgresConnector.read_query_from_file(
        Path(__file__).parent / "mutual_funds.sql"
    )
    funds_df = PostgresConnector(Databases.my_database).sql_to_pandas(funds_sql)

    # get mutual funds ISINs and IDs from fundinfo
    data = []
    offset = 0
    limit = 1000
    while True:
        response = requests.get(
            url, headers=headers, params={"limit": limit, "offset": offset}
        )
        response.raise_for_status()

        response_data = response.json()["data"]
        if len(response_data) == 0:
            break

        data.extend(response_data)
        offset += limit

    df = pd.DataFrame.from_dict(data, orient="columns")
    req_columns = ["idFundShare", "isin", "currencyQuote"]
    df = df[req_columns]

    # keeping only sinlge records per fundinfo ID, based on currency alphabetically
    # which guarantees that EUR is kept
    df = df.sort_values("currencyQuote").drop_duplicates(
        subset="idFundShare", keep="first"
    )

    # filter only required mutual funds
    df = df.merge(funds_df, how="inner", on="isin")
    df.rename(
        columns={"currencyQuote": "currency", "idFundShare": "fundinfo_id"},
        inplace=True,
    )
    df["created_at"] = pd.Timestamp.utcnow()

    msg = "No funds to upload"

    if len(df) > 0:
        PostgresConnector(Databases.my_database).copy_expert_from_pandas(
            df,
            "fundinfo_details",
            update_on_conflict=True,
            constraint_cols=["fundinfo_id"],
        )

        msg = f"{len(df)} funds uploaded."

    return msg, df


def fundinfo_fillforward_prices(df: pd.DataFrame):
    prices = []

    # creating set for each instrument separately
    for asset, group in df.groupby("idFundShare"):
        group["date"] = pd.to_datetime(group["date"])
        # set date as index and reindex for required timeframe
        group = group.set_index("date")
        window_start = group.index.min()
        window_end = group.index.max()
        full_range = pd.date_range(start=window_start, end=window_end)
        group = group.reindex(full_range)
        # add required data, including filled forward prices
        group["idFundShare"] = asset
        group["close"] = group["close"].ffill()
        group["volume"] = group["volume"].fillna(0).astype(int)
        # add instrument df with prices to prices list
        prices.append(group)

    prices_df = pd.concat(prices)
    prices_df = prices_df.rename_axis("date").reset_index()

    return prices_df


def fundinfo_prices_daily_handler(batch_size: int):
    """
    Get the Fundinfo id first then 1Y +1D history of prices
    for mutual funds and ELTIFs that have is_price_fetched
    Max batch_size for a year +1D of history is 20 (limit on number of returned points)
    """
    assert batch_size <= 20, "batch_size must be <=20, limited by the API"

    pg_write = PostgresConnector(Databases.my_database)

    url = "https://services.opcvm360.com/api-v1/fundshares-history"
    headers = get_fundinfo_headers()

    window_start = (datetime.today() - relativedelta(months=12)).replace(day=1).date()

    funds_sql = PostgresConnector.read_query_from_file(
        Path(__file__).parent / "fundinfo_funds.sql"
    )
    funds_df = PostgresConnector(Databases.my_database).sql_to_pandas(funds_sql)
    funds_list = funds_df["fundinfo_id"].tolist()

    # below df required to solve issue with prices in more than one currency for single fund
    funds_req = funds_df[["fundinfo_id", "currency"]].copy()
    funds_req.rename(columns={"fundinfo_id": "idFundShare"}, inplace=True)

    # get prices data in batches, calls based on fundinfo IDs
    error_list = []
    records_count = 0

    for i in range(0, len(funds_list), batch_size):
        batch = funds_list[i : i + batch_size]
        fundshares_ids = ",".join(str(x) for x in batch)
        params = {
            "fundshares": fundshares_ids,
            "from": window_start,
            "limit": batch_size * 400,
        }

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logger_de.error(f"Error calling FUNDS360: {e}")
            error_list.append(f"Funds IDs {batch}: {e}")
            continue

        data = response.json()
        df = pd.DataFrame.from_dict(data["data"], orient="columns")
        req_columns = ["idFundShare", "date", "vl", "currencyQuote"]
        df = df[req_columns]

        # update price and add volume
        df.rename(columns={"vl": "close", "currencyQuote": "currency"}, inplace=True)
        df["close"] = (df["close"].astype(float) * 100).round(2)
        df["volume"] = 1

        # handling situations when prices are sent in more than one currency for single fund
        df = df.merge(funds_req, how="inner", on=["idFundShare", "currency"])
        df.drop(columns=["currency"], inplace=True)

        # fill forward prices for current batch
        df = fundinfo_fillforward_prices(df=df)

        df = df.merge(
            funds_df, how="left", left_on="idFundShare", right_on="fundinfo_id"
        )
        df.drop(columns=["idFundShare", "fundinfo_id", "isin"], inplace=True)

        df[["open", "high", "low"]] = 0
        df["source"] = "fundinfo"

        pg_write.copy_expert_from_pandas(
            df,
            "fundinfo_prices",
            update_on_conflict=True,
            constraint_cols=["date", "instrument_id"],
        )

        records_count += len(df)

    if len(error_list) > 0:
        raise Exception(f"Errors occurred during processing: {', '.join(error_list)}")

    msg = f"{records_count} prices uploaded to fundinfo_prices table"

    return msg


if __name__ == "__main__":
    msg_check, df_check = fundinfo_details_handler()
    print(msg_check)
    # print(fundinfo_prices_daily_handler(batch_size=20))
