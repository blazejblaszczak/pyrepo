from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from core.common.global_data_classes import Databases
from core.db.db_connector import PostgresConnector


def app_time_batch_run(
    window_start: str = None,
    window_end: str = None,
    user_list: list = None,
):

    write_conn = PostgresConnector(db=Databases.db_main)
    query_path = Path(Path(__file__).parent, "app_time.sql")
    query = write_conn.read_query_from_file(query_path, raw=True)
    query = query.format(
        window_start=window_start, window_end=window_end, user_list=user_list
    )

    df = write_conn.sql_to_pandas(query)

    return df


def app_time_handler(
    window_start: str = None, window_end: str = None, batch_size: int = 1000
):

    if window_start is None:
        window_start = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")

    if window_end is None:
        window_end = datetime.today().strftime("%Y-%m-%d")

    db_read = PostgresConnector(db=Databases.db_replica)

    query_path = Path(Path(__file__).parent, "users_list.sql")
    query = db_read.read_query_from_file(query_path, raw=True)
    query = query.format(window_start=window_start, window_end=window_end)

    df_users = db_read.sql_to_pandas(query)
    users = df_users["user_id"].tolist()

    dfs_list = []

    for idx in range(0, len(users), batch_size):

        users_batch = users[idx : idx + batch_size]

        df = app_time_batch_run(
            window_start=window_start, window_end=window_end, user_list=users_batch
        )

        dfs_list.append(df)

    df_all = pd.concat(dfs_list)

    msg = f"Updated app_time table with {df_all.shape[0]} records"

    return df_all, msg
