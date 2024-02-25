import pandas as pd
import numpy as np
import chardet

from db_conn import MySQLconnector


def csv_to_df(csv_path):

    # Check CSV file encoding
    with open(csv_path, 'rb') as f:
        result = chardet.detect(f.read())

    # Save CSV as dataframe
    df = pd.read_csv(csv_path, encoding=result['encoding'])

    # Add additional columns and cast transaction_timestamp_gmt column to timestamp
    df['transaction_type'] = np.where(df['transaction_amount']>=0, 'purchase', 'refund')
    df['is_valid'] = np.where(df['status_code']!=4, True, False)
    df['transaction_timestamp_gmt'] = pd.to_datetime(df['transaction_timestamp_gmt'])

    return df


def transactions_handler(file_path):

    # Create dataframe that will be loaded to DB
    df = csv_to_df(csv_path=file_path)

    # Create connector to MySQL DB and load dataframe data to destination table
    mysql_conn = MySQLconnector()
    mysql_conn.upload_df_to_db(destination_table='transactions', df=df)

    # Return information about uploaded rows
    msg = f"{len(df)} rows were uploaded to transactions table"

    return msg


if __name__ == '__main__':

    # df_test = csv_to_df("data/mycsv.csv")
    # print(df_test.head())

    msg = transactions_handler(file_path="data/mycsv.csv")
    print(msg)
