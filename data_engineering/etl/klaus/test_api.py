import json
from pathlib import Path

import responses
from core.common.global_data_classes import Databases
from core.db.db_connector import PostgresConnector
from etl.klaus.handler import (
    reviews_handler,
)

test_data_folder = Path(Path(__file__).parent, "test_data_api")
reviews_table = "reviews"


@responses.activate
def test_klaus_reviews():
    conn = PostgresConnector(Databases.db_main)

    def cleanup():
        conn.execute_query(f"TRUNCATE {reviews_table};")

    cleanup()

    with open(test_data_folder / "reviews.json") as r:
        resp = json.load(r)
    responses.add(
        responses.GET,
        "https://kibbles.klausapp.com/api/v1/payment/11111/workspace/11111/reviews?",
        json=resp,
        status=200,
    )

    msg = reviews_handler()
    assert isinstance(msg, str)

    df = conn.sql_to_pandas(f"SELECT * FROM {reviews_table};")

    cleanup()

    assert df.shape == (3, 9)

    assert set(df["reviewer_email"]) == {
        "cris@gmail.com",
        "jacek@gmail.com",
        "batman@gmail.com",
    }
