import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import requests
from core.common.global_data_classes import PG_NULL, Databases
from core.common.ssm_env.settings import ENV_KLAUS_TOKEN
from core.db.db_connector import PostgresConnector


class KlausData:
    """
    Class to pull data using Klaus API
    and convert it to pandas df according to the resource type.
    """

    def __init__(self):
        self.route: str = "https://kibbles.klausapp.com/api/v1/payment/"
        self.authorization: str = ENV_KLAUS_TOKEN
        self.account_id: str = "11111"
        self.workspace_id: str = "workspace/11111"
        self.delta_replica_pg_conn = PostgresConnector(db=Databases.db_replica)

    def _pull_data_resource(self, resource: str, from_date, to_date) -> dict:

        path = os.path.join(self.route, self.account_id, self.workspace_id, resource)
        headers = {
            "Authorization": "Bearer " + self.authorization,
            "Accept": "application/json",
        }

        params = {
            "selfReview": "exclude",
            "direction": "received",
            "step": "week",
            "fromDate": datetime.fromisoformat(from_date)
            .replace(tzinfo=timezone.utc)
            .isoformat(),
            "toDate": datetime.fromisoformat(to_date)
            .replace(tzinfo=timezone.utc)
            .isoformat(),
        }

        r = requests.get(path, headers=headers, params=params)
        r.raise_for_status()

        try:
            r = r.decode("utf-8")
        except AttributeError:
            pass

        return json.loads(r.text)

    def get_reviews_df(
        self,
        resource: str = "reviews?",
        from_date: str = "2022-12-26",
        to_date: str = "2023-01-02",
        columns=[
            "review_id",
            "reviewer_email",
            "reviewee_email",
            "score",
            "created_at",
            "tags",
            "review_link",
            "external_link",
        ],
    ) -> pd.DataFrame:
        results = self._pull_data_resource(resource, from_date, to_date)
        df = pd.json_normalize(results["reviews"])

        # check if there were reviews made
        if df.empty:
            return None

        # delete unsused columns
        df.drop(
            columns=[
                "firstComment",
                "reviewer",
                "reviewee",
                "categories",
                "rootCauses",
                "reviewTime",
            ],
            inplace=True,
        )

        # rename columns
        df.rename(
            columns={
                "reviewId": "review_id",
                "reviewLink": "review_link",
                "externalLink": "external_link",
                "reviewerEmail": "reviewer_email",
                "revieweeEmail": "reviewee_email",
                "created": "created_at",
            },
            inplace=True,
        )

        # check number of columns
        if len(df.columns) != len(columns):
            raise IndexError("Wrong number of columns")

        # check column names
        if sorted(df.columns.tolist()) != sorted(columns):
            raise NameError("Wrong column name")

        # handle NULLs
        df = df.replace(np.nan, PG_NULL)

        return df


if __name__ == "__main__":
    kd = KlausData()
    df = kd.get_reviews_df(from_date="2023-12-03", to_date="2023-12-09")
    print(df.head())
