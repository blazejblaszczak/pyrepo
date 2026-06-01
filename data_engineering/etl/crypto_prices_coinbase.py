from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Tuple, Union

import time
import requests
from data_engineering.common.http_requests import get_json

import numpy as np
import pandas as pd
import pytz
from core.common.global_data_classes import Databases
from core.common.logging_base import logger_workers
from core.common.market_utils.active_instruments import (
    get_active_coinbase_id_to_instrument,
    get_active_cryptos,
)
from core.common.tables import DeltaTables
from core.db.db_connector import PostgresConnector
from data_engineering.common.prices_utils import (
    MISSING_INSTRUMENTS_MSG_TEMPLATE,
    fill_gaps,
)


def get_coinbase_session():
    session_coinbase = requests.Session()
    return session_coinbase


def fetch_cryptos_coinbase_prices(
    coinbase_id: str, start_date: str, end_date: str, timeframe_seconds: int
):
    session_coinbase = get_coinbase_session()
    # We enforce 10 requests / second max
    time.sleep(0.11)
    url = f"{COINBASE_BASE_API_URL}/products/{coinbase_id}/candles?start={start_date}&end={end_date}&granularity={timeframe_seconds}"
    response = get_json(session_coinbase, url)
    return response


def fill_gaps_for_crypto_prices(
    crypto_prices_buffer,
    crypto_prices,
    timeframe_seconds,
    start_date,
    open_interval_end_date,
    with_gaps_filling: bool = True,
) -> list:
    if with_gaps_filling is True:
        crypto_prices_df = pd.DataFrame(crypto_prices)
        if timeframe_seconds == 3600:
            freq = "H"
        elif timeframe_seconds == 86400:
            freq = "D"
        else:
            raise Exception(f"Wrong timeframe specified: {timeframe_seconds=}")

        if crypto_prices_df.empty:
            return crypto_prices_buffer

        try:
            crypto_prices_df = fill_gaps(
                crypto_prices_df, start_date, open_interval_end_date, freq
            )

            # filter out today's timestamps, need to do it twice, because fill_gaps
            # above generates today's timestamps anyway
            crypto_prices_df = crypto_prices_df[
                crypto_prices_df["date"]
                < pd.to_datetime(open_interval_end_date, utc=True)
            ]
        except Exception as e:
            logger_workers.exception(
                "Exception during filling gaps in crypto historical prices"
            )
            crypto_prices_buffer.extend(crypto_prices)

        crypto_prices_buffer.extend(crypto_prices_df.to_dict("records"))
    else:
        crypto_prices_buffer.extend(crypto_prices)

    return crypto_prices_buffer


def iterate_over_crypto_prices(
    instrument_data,
    table_prices,
    crypto_prices_buffer,
    symbols_in_buffer,
    errors_http_count,
    failed_pairs,
    with_gaps_filling,
    default_start_date,
    timeframe_seconds,
):
    instrument_id = instrument_data["instrument_id"]
    coinbase_id = instrument_data["coinbase_id"]
    symbol_repr_for_logs = "--".join((coinbase_id, str(instrument_id)))

    if default_start_date is None:
        start_date = instrument_data["start_date"]
    else:
        start_date = datetime.strptime(default_start_date, "%Y-%m-%d")
        start_date = start_date.date()

    # it looks like coinbase casts date e.g. 2022-10-18 to timestamp 2022-10-18 00:00
    # effectively making open interval on the right side of date range for hourly prices
    # but closed one for daily prices
    # need to be carefull about it, since we also have gaps filling that relies on end_date

    # this is effectively yesterday, but I don't want to mess with get_enabled_cryptos_price_range()
    end_date = instrument_data["end_date"]

    # effectively today
    open_interval_end_date = end_date + timedelta(days=1)
    symbol, currency = coinbase_id.split("-")

    prices, errors = _fetch_crypto_price(
        coinbase_id,
        start_date,
        open_interval_end_date,
        timeframe_seconds,
    )

    errors_http_count += errors
    if errors > 0:
        failed_pairs.append(symbol_repr_for_logs)

    if len(prices) == 0:
        return (
            crypto_prices_buffer,
            symbols_in_buffer,
            errors_http_count,
            failed_pairs,
        )

    crypto_prices = [
        _coinbase_candle_to_price(symbol, price, currency, instrument_id)
        for price in prices
    ]

    crypto_prices = [
        i for i in crypto_prices if i["date"].date() < open_interval_end_date
    ]

    crypto_prices_buffer = fill_gaps_for_crypto_prices(
        crypto_prices_buffer=crypto_prices_buffer,
        crypto_prices=crypto_prices,
        timeframe_seconds=timeframe_seconds,
        start_date=start_date,
        open_interval_end_date=open_interval_end_date,
        with_gaps_filling=with_gaps_filling,
    )

    symbols_in_buffer.append(symbol_repr_for_logs)

    if len(crypto_prices_buffer) > 300:
        symb_w_errors = safely_upload_crypto_prices(crypto_prices_buffer, table_prices)
        if len(symb_w_errors) > 0:
            failed_pairs.extend(symb_w_errors)
        # clean buffer after db dump either success or not
        crypto_prices_buffer = []
        symbols_in_buffer = []

    return (
        crypto_prices_buffer,
        symbols_in_buffer,
        errors_http_count,
        failed_pairs,
    )


def fetch_cryptos_prices(
    table_instruments: str = "instruments",
    table_prices: str = "stocks_prices",
    timeframe_seconds: int = 3600,
    max_price_days_range: int = 12,
    with_gaps_filling: bool = True,
    default_start_date: str = None,
):
    crypto_price_ranges = get_enabled_cryptos_price_range(
        table_instruments=table_instruments,
        table_prices=table_prices,
        max_price_days_range=max_price_days_range,
    )

    errors_http_count = 0
    failed_pairs = []
    crypto_prices_buffer = []
    symbols_in_buffer = []

    for _, instrument_data in crypto_price_ranges.iterrows():
        (
            crypto_prices_buffer,
            symbols_in_buffer,
            errors_http_count,
            failed_pairs,
        ) = iterate_over_crypto_prices(
            instrument_data=instrument_data,
            table_prices=table_prices,
            crypto_prices_buffer=crypto_prices_buffer,
            symbols_in_buffer=symbols_in_buffer,
            errors_http_count=errors_http_count,
            failed_pairs=failed_pairs,
            with_gaps_filling=with_gaps_filling,
            default_start_date=default_start_date,
            timeframe_seconds=timeframe_seconds,
        )

    if len(crypto_prices_buffer) > 0:
        symb_w_errors = safely_upload_crypto_prices(crypto_prices_buffer, table_prices)
        if len(symb_w_errors) > 0:
            failed_pairs.extend(symb_w_errors)

    if errors_http_count > 0:
        logger_workers.error(
            f"{errors_http_count} for {len(crypto_price_ranges)} cryptos api calls have failed. Failed: {failed_pairs}."
        )

    if len(failed_pairs) > 1:
        raise Exception(
            MISSING_INSTRUMENTS_MSG_TEMPLATE.format(missing_prices=failed_pairs)
        )

    return len(crypto_price_ranges), errors_http_count, failed_pairs


def upload_crypto_prices(crypto_prices: Union[list, pd.DataFrame], table_prices: str):
    # beware that gaps filled prices with volume = 0.0 may override old prices as well
    if isinstance(crypto_prices, list):
        crypto_prices_df = pd.DataFrame(crypto_prices)
    else:
        crypto_prices_df = crypto_prices

    crypto_prices_df.drop_duplicates(["instrument_id", "date"], inplace=True)

    crypto_prices_df["created"] = pd.Timestamp.utcnow()
    PostgresConnector(Databases.delta_main).copy_expert_from_pandas(
        source=crypto_prices_df,
        destination=table_prices,
        update_on_conflict=True,
        constraint_cols=["instrument_id", "date"],
    )


def safely_upload_crypto_prices(crypto_prices: list, table_prices: str) -> list:
    err_instr_id_list = []
    try:
        upload_crypto_prices(crypto_prices=crypto_prices, table_prices=table_prices)
    except Exception as e:
        crypto_prices_df = pd.DataFrame(crypto_prices)
        unique_instrument_ids = list(crypto_prices_df["instrument_id"].unique())
        for instr_id in unique_instrument_ids:
            subset_crypto_prices = crypto_prices_df[
                crypto_prices_df["instrument_id"] == instr_id
            ]
            try:
                upload_crypto_prices(
                    crypto_prices=subset_crypto_prices, table_prices=table_prices
                )
            except Exception as e:
                logger_workers.exception(
                    f"Exception during uploading crypto prices for instrument_ids: {instr_id}"
                )
                err_instr_id_list.append(instr_id)

    return err_instr_id_list


def get_enabled_cryptos_price_range(
    table_instruments: str = "instruments",
    table_prices: str = "stocks_prices",
    max_price_days_range: int = 12,
) -> pd.DataFrame:
    """
    get enabled cryptos with last updated price date or default
    """
    enabled_coinbase_id_to_instrument_id = get_active_coinbase_id_to_instrument()
    coinbase_with_instrument_id = [
        {"coinbase_id": coinbase_id, "instrument_id": instrument_id}
        for coinbase_id, instrument_id in enabled_coinbase_id_to_instrument_id.items()
    ]
    enabled_instrument_ids = tuple(enabled_coinbase_id_to_instrument_id.values())

    price_ranges = pd.DataFrame(
        columns=[
            "instrument_id",
            "coinbase_id",
            "start_date",
            "default_start_date",
            "end_date",
        ],
        data=coinbase_with_instrument_id,
    )

    price_ranges["default_start_date"] = date.today() - timedelta(
        days=max_price_days_range
    )
    price_ranges["end_date"] = date.today() - timedelta(days=1)

    # updating start_date with the last values from db
    latest_dates_sql = PostgresConnector.read_query_from_file(
        Path(Path(__file__).parent, "queries", "crypto_latest_dates.sql"),
        table_prices=table_prices,
    )
    last_dates_from_db = PostgresConnector(Databases.delta_replica).sql_to_pandas(
        latest_dates_sql,
        values=(enabled_instrument_ids,),
    )
    last_dates_from_db["db_last_date"] = pd.to_datetime(
        last_dates_from_db["db_last_date"]
    ).dt.date

    price_ranges = price_ranges.merge(
        last_dates_from_db, how="left", on="instrument_id"
    )
    price_ranges.start_date = np.where(
        price_ranges.default_start_date <= price_ranges.db_last_date,
        price_ranges.db_last_date,
        price_ranges.default_start_date,
    )
    price_ranges.drop(["db_last_date", "default_start_date"], axis=1, inplace=True)
    return price_ranges


def _fetch_crypto_price(
    coinbase_id: str,
    start_date: datetime,
    end_date: datetime,
    timeframe_seconds: int,
) -> Tuple[list, int]:
    days_delta = (end_date - start_date).days
    max_days_range = _coinbase_max_price_days_range(timeframe_seconds)

    resulting_prices = []
    errors_http = 0
    while days_delta > 0:
        this_iteration_end_datetime = start_date + timedelta(days=max_days_range)
        if this_iteration_end_datetime > end_date:
            this_iteration_end_datetime = end_date

        response = fetch_cryptos_coinbase_prices(
            coinbase_id,
            start_date.strftime("%Y-%m-%d"),
            this_iteration_end_datetime.strftime("%Y-%m-%d"),
            timeframe_seconds,
        )

        if response.success:
            resulting_prices.extend(response.body)
        else:
            errors_http += 1
            logger_workers.error(
                f"_fetch_crypto_price error for symbol: {coinbase_id}, start_date: {start_date.strftime('%Y-%m-%d')}",
            )

        start_date = this_iteration_end_datetime
        days_delta = (end_date - start_date).days
    return (resulting_prices, errors_http)


def _coinbase_max_price_days_range(timeframe_seconds: int) -> int:
    if timeframe_seconds == 86400:
        max_days_range = 240
    elif timeframe_seconds == 3600:
        max_days_range = 12
    else:
        raise Exception(f"Unsupported timeframe_seconds: {timeframe_seconds}")
    return max_days_range


def _coinbase_candle_to_price(
    symbol: str, candle: list, currency: str, instrument_id: int
) -> dict:
    return {
        "instrument_id": instrument_id,
        "symbol": symbol,
        "date": datetime.utcfromtimestamp(candle[0]).replace(tzinfo=pytz.UTC),
        "open": 0,
        "high": 0,
        "low": 0,
        "close": candle[4] * 100,
        "volume": candle[5] * 100,
        "currency": currency,
    }


def update_stocks_prices_weekly_from_daily_crypto(
    table_stocks_prices_daily="stocks_prices_daily",
    table_stocks_prices_weekly="stocks_prices_weekly",
):
    postgres = PostgresConnector(Databases.delta_main)
    postgres_replica = PostgresConnector(Databases.delta_replica)

    coinbase_id_to_instrument = get_active_coinbase_id_to_instrument()
    instrument_ids = tuple(coinbase_id_to_instrument.values())

    query = PostgresConnector.read_query_from_file(
        Path(
            Path(__file__).parents[2],
            "common",
            "queries",
            "prices_get_weekly_from_daily.sql",
        ),
        table_stocks_prices_daily=table_stocks_prices_daily,
    )
    df_weekly = postgres_replica.sql_to_pandas(
        query,
        values=[instrument_ids],
    )

    # shouldn't be needed after we make instrument_id non-nullable
    # https://pandas.pydata.org/docs/user_guide/integer_na.html
    df_weekly["instrument_id"] = df_weekly["instrument_id"].astype(pd.Int64Dtype())

    df_weekly["created"] = pd.Timestamp.utcnow()
    postgres.copy_expert_from_pandas(
        source=df_weekly,
        destination=table_stocks_prices_weekly,
        update_on_conflict=True,
        constraint_cols=["instrument_id", "date"],
    )

    return f"Uploaded {len(df_weekly)} entries for {df_weekly.symbol.nunique()} unique symbols"


def coinbase_adjust_live_prices_all_instruments_handler(
    window_start: str, window_end: str
):
    """
    max count of aggregations per request is 300
    so to get minutely this has to be batched over periods of 60s * 300 = 5h
    """
    if any(arg is None for arg in (window_start, window_end)):
        raise ValueError("Task arguments are required! window_start and window_end.")

    time_ranges = pd.date_range(window_start, window_end, freq="5H")
    time_ranges = [dt.strftime("%Y-%m-%d %H:%M") for dt in time_ranges] + [window_end]

    for crypto in get_active_cryptos():
        instrument_prices = []
        for i in range(len(time_ranges) - 1):
            ws = time_ranges[i]
            we = time_ranges[i + 1]

            # sleep time already hardcoded in fetch_cryptos_coinbase_prices
            prices = fetch_cryptos_coinbase_prices(
                coinbase_id=crypto["coinbase_id"],
                start_date=ws,
                end_date=we,
                timeframe_seconds=60,
            )

            prices = [
                _coinbase_candle_to_price(
                    symbol=crypto["symbol"],
                    candle=price,
                    currency=crypto["currency"],
                    instrument_id=crypto["id"],
                )
                for price in prices.body
            ]
            prices = pd.DataFrame(prices)
            instrument_prices.append(prices)

        instrument_prices = pd.concat(instrument_prices)
        instrument_prices.drop_duplicates(inplace=True)
        PostgresConnector(Databases.delta_main).copy_expert_from_pandas(
            instrument_prices,
            DeltaTables.stocks_prices_live_coinbase,
            update_on_conflict=True,
            constraint_cols=["instrument_id", "date"],
        )


if __name__ == "__main__":
    update_stocks_prices_weekly_from_daily_crypto()

    print(
        fetch_cryptos_prices(
            "instruments",
            "stocks_prices_daily",
            86400,  # 1d in seconds
            max_price_days_range=1827,
            default_start_date="2025-11-28",
            with_gaps_filling=True,
        )
    )
