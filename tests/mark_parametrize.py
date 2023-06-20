import pandas as pd
import pytest
from function_folder import (
    performance_data,
)


@pytest.mark.parametrize(
    "df_input,df_expected",
    [
        (
            pd.DataFrame(
                [
                    [pd.to_datetime("2023-05-01"), 1000, 0.00, 0],
                    [pd.to_datetime("2023-05-04"), 1500, 0.50, 500],
                    [pd.to_datetime("2023-05-08"), 2000, 1.00, 1000],
                    [pd.to_datetime("2023-05-11"), 2500, 1.50, 1500],
                    [pd.to_datetime("2023-05-15"), 3000, 2.00, 2000],
                ],
                columns=[
                    "ts",
                    "portfolio_user_coin",
                    "performance_ratio",
                    "performance_user_coin",
                ],
            ),
            pd.DataFrame(
                [
                    [pd.to_datetime("2023-05-08"), "100.0%", "-0.71%"],
                    [pd.to_datetime("2023-05-15"), "100.0%", "-0.04%"],
                ],
                columns=["date", "ratio_change_str", "sp500_change_str"],
            ),
        ),
    ],
)
def test_performance_data_df(df_input, df_expected):
    # Check data type correctness
    df_output = performance_data(df_input)
    assert df_output.equals(df_expected)


@pytest.mark.parametrize(
    "df_input,error",
    [
        (
            pd.DataFrame(
                [
                    [pd.to_datetime("2023-05-01"), 1000, 0.00, 0],
                    [pd.to_datetime("2023-05-04"), 1500, 0.50, 500],
                    [pd.to_datetime("2023-05-08"), 2000, 1.00, 1000],
                ],
                columns=[
                    "date",
                    "portfolio_user_coin",
                    "performance_ratio",
                    "performance_user_coin",
                ],
            ),
            KeyError,
        ),
        (
            pd.DataFrame(
                [
                    ["2023-05-01", "1000", "0.00", "0"],
                    ["2023-05-04", "1500", "0.50", "500"],
                    ["2023-05-08", "2000", "1.00", "1000"],
                ],
                columns=[
                    "ts",
                    "portfolio_user_coin",
                    "performance_ratio",
                    "performance_user_coin",
                ],
            ),
            ValueError,
        ),
        (pd.DataFrame(), KeyError),
    ],
)
def test_performance_data_df_raises(df_input, error):
    # Check potential errors
    with pytest.raises(error):
        performance_data(df_input)
