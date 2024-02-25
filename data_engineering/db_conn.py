import os
import mysql.connector
from sqlalchemy import create_engine

from dotenv import load_dotenv


class MySQLconnector:
    # Connector for MySQL DB type

    def __init__(self):

        # Load environment vars
        load_dotenv()
        self.DB_HOST=os.getenv('DB_HOST')
        self.DB_NAME=os.getenv('DB_NAME')
        self.DB_PASSWORD=os.getenv('DB_PASSWORD')
        self.DB_USER=os.getenv('DB_USER')

    def upload_df_to_db(self, destination_table, df):

        # Prepare config vars
        db_config = {
            'host': self.DB_HOST,
            'user': self.DB_USER,
            'password': self.DB_PASSWORD,
            'database': self.DB_NAME
        }

        # Connect to MySQL using sqlalchemy
        engine = create_engine(f"mysql+mysqlconnector://{db_config['user']}:{db_config['password']}@{db_config['host']}/{db_config['database']}")

        # Insert the DataFrame into the MySQL table
        df.to_sql(name=destination_table, con=engine, if_exists='append', index=False)

        # Close the engine connection
        engine.dispose()
