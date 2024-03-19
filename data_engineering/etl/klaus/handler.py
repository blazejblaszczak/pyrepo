from datetime import datetime, timedelta

from core.common.global_data_classes import Databases
from core.db.db_connector import PostgresConnector
from machine_learning.analytics.etls.klaus.api_conn import KlausData

reviews = "reviews"


def reviews_handler(
    destination=reviews, window_start=None, window_end=None
):
    delta_pg_conn = PostgresConnector(db=Databases.db_main)

    if window_start is None:
        window_start = (datetime.today() - timedelta(days=7)).strftime("%Y-%m-%d")

    if window_end is None:
        window_end = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    k = KlausData()
    df = k.get_reviews_df(from_date=window_start, to_date=window_end)

    if df is None:
        return "No agent reviews in last week"

    else:
        delta_pg_conn.upload_to_db(df, destination)
        msg = f"{len(df)} quality reviews were uploaded to {destination}!"
        return msg


if __name__ == "__main__":
    reviews_handler()
