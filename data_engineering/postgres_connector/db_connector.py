import json
import time
from functools import partial, singledispatchmethod
from io import BytesIO, StringIO
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import psycopg2
import psycopg2.errors
import psycopg2.extras
import sqlparse
from core.common.global_data_classes import PG_NULL, CrossDBJoinType, Databases
from core.common.logging_base import logger_common as logging
from core.common.ssm_env.env_dataclasses import MappedEnvironments
from core.common.ssm_env.settings import DB_PARAMS
from core.common.utils import find_absolute_path
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

psycopg2.extensions.register_adapter(np.int64, psycopg2._psycopg.AsIs)


class PostgresConnector:
    """
    Connector for PostgreSQL DB type
    destination: fully qualified name - schema.table
    """

    def __init__(
        self,
        db: Databases = Databases.backend_replica,
        conn_params: Dict = None,
        options: Optional[str] = None,
        for_maintainance: bool = False,
        log_queries: bool = True,
    ):
        """
        Factory to create db connector for specific db
        """
        self.db = db
        self.for_maintainance = for_maintainance
        self.conn_string = None
        self.log_queries = log_queries
        self.log = (
            logging.debug
            if MappedEnvironments.we_are_in_gitpod_ci() is True
            else logging.warning
        )

        if isinstance(conn_params, dict) and len(conn_params) > 0:
            self.conn_params = conn_params
            self.conn_string = " ".join(
                [f"{k}={v}" for k, v in self.conn_params.items()]
            )

        else:
            try:
                conn_params = DB_PARAMS[db]
            except KeyError:
                raise ValueError(
                    f"Wrong db prameter passed: {db}. Must be in Databases dataclass"
                )

            # Set the connection parameters
            self.conn_params = conn_params
            self.conn_string = " ".join(
                [f"{k}={v}" for k, v in self.conn_params.items()]
            )

        self.options = options
        logging.debug(f"conn options: {self.options}")

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options_str: Optional[str]):
        if options_str is None:
            options_str = ""
        if "-c statement_timeout=" in options_str:
            self._options = options_str
        else:  # set timeout if it is not provided by user
            if self.db in (
                Databases.backend_replica,
                Databases.delta_replica,
            ):
                self._options = f"{options_str} -c statement_timeout={2*60*1000}"  # 2 minutes for read queries
            elif self.db == Databases.delta_main:
                self._options = f"{options_str} -c statement_timeout={10*60*1000}"  # 10 minutes for write queries
            else:
                self._options = f"{options_str} -c statement_timeout={2*60*1000}"  # 2 minutes for undefined db connections

    def get_connection(self):
        return psycopg2.connect(self.conn_string, options=self.options)

    def execute_and_log_query(
        self,
        curs: psycopg2.extras.DictCursor,
        query: str,
        values: Optional[List] = None,
    ) -> None:
        _query = query
        if values is not None:
            query = curs.mogrify(query, values)

        start_time = time.time()
        curs.execute(query)
        exec_time = time.time() - start_time

        if self.log_queries is True:
            self.log(
                "SQL Query",
                extra={
                    "pool": self.db,
                    "executionTime": round(exec_time * 1000, 2),  # ms
                    "query": _query,
                    "queryWithValues": curs.query.decode(),
                    "rowCount": curs.rowcount,
                    "values": values,
                },
            )

    @classmethod
    def read_query_from_file(
        self, sql_path: Union[str, Path], raw=False, **kwargs
    ) -> str:
        """
        This method allows you to read query from file and replace placeholders with kwargs
        If you prefer to replace placeholders yourself, set raw=True
        arguments:
            sql_path: path to file with query; can be relative to project root or absolute
            raw: if True, kwargs are ignored
            kwargs: placeholders to replace in query
        returns:
            query: str
        """

        if raw is True and len(kwargs) > 0:
            raise ValueError("If raw=True, kwargs should not be provided")

        absolute_path = find_absolute_path(sql_path)
        raw_query = Path(absolute_path).read_text()
        commented_query = f"-- {absolute_path}\n{raw_query}"
        if raw is True:
            query = commented_query
        else:
            query = commented_query.format(**kwargs)

        return query

    def build_result(
        self,
        curs: psycopg2.extras.DictCursor,
        query: str,
        include_columns: bool = False,
    ):
        result = []

        if include_columns is True:
            if len(curs.description) > 0:
                result.append([desc[0] for desc in curs.description])

        if curs.rowcount > 0:
            # curs.rowcount becomes -1 when the exception is thrown
            rowcount = curs.rowcount
            try:
                result.extend(curs.fetchall())
            # only INSERT, UPDATE, DELETE have rowcount > 0 but no fetchall()
            except psycopg2.ProgrammingError as error:
                # more limited handling if needed
                # if str(error) != "no results to fetch":
                #     raise error
                logging.debug(f"{rowcount} rows were affected")
                result.append(rowcount)
            else:
                # everything which is not INSERT, UPDATE, DELETE and have >0 rows,
                # will go here; edge case: RETURNING *
                self.check_and_log_read_from_main_db(query)
        else:
            logging.debug("No results to fetch")

        # this part is only for backwards compatibility - expecting None instead of []
        if len(result) == 0:
            return None

        return result

    def execute_query(
        self,
        query: Union[str, Path],
        values: Union[List, Tuple, Dict, None] = None,
        include_columns: bool = False,
    ) -> Optional[List]:
        """
        values: should be iterable with list of params

        Examples:
        # list of
        self.execute_query(
            "SELECT * FROM instruments WHERE symbol IN %s",
            values=(("BTC", ),)
        )

        # single arg
        self.execute_query(
            "SELECT * FROM instruments WHERE symbol = %s",
            values=("BTC",)
        )

        # few arguments
        self.execute_query(
            "SELECT * FROM instruments WHERE symbol = %s AND id != %s",
            values=("BTC", 5)
        )

        # named arguments
        self.execute_query(
            "SELECT * FROM instruments WHERE symbol IN %(symbols)s AND id NOT IN %(not_in_ids)s",
            values={"symbols": ("BTC", "ETH"), "not_in_ids": (1, 2)}
        )
        """
        conn = self.get_connection()
        result = []

        if isinstance(query, Path):
            query = query.read_text()

        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
                self.execute_and_log_query(curs, query, values)
                conn.commit()

                result = self.build_result(
                    curs=curs, query=query, include_columns=include_columns
                )

        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            conn.rollback()
            conn.close()
            raise error
        finally:
            conn.close()

        return result

    def sql_to_list(
        self, query: str, values: Union[List, Tuple, Dict, None] = None
    ) -> List[Dict]:
        self.check_and_log_read_from_main_db(query)
        result = self.execute_query(query, values=values)
        return [] if result is None else result

    def sql_to_pandas(
        self, query: Union[str, Path], values: List = None
    ) -> pd.DataFrame:
        # DO NOT USE pd.read_sql() -> causes rollbacks on empty dataframes
        res = self.execute_query(query=query, values=values, include_columns=True)
        if len(set(res[0])) < len(res[0]):
            raise KeyError(
                f"""
            The SQL query below contains duplicated column names {res[0]}:
            {query}
            Please fix the SQL query.
            """
            )
        return pd.DataFrame(res[1:], columns=res[0])

    def sql_to_csv(self, query: str, filepath: Union[str, BytesIO] = None, **kwargs):
        res = self.sql_to_pandas(query)
        res.to_csv(path_or_buf=filepath, **kwargs)
        return res

    def sql_to_dict(self, query: str, orient="dict") -> Dict:
        return self.sql_to_pandas(query).to_dict(orient)

    def get_table_metadata(self, table_name: str, table_schema: str = None):
        """Retrieve info from the information_schema"""
        query = f"""
            SELECT *
            FROM information_schema.columns
            WHERE table_name='{table_name}'
        """
        if table_schema is not None:
            query += f""" AND table_schema='{table_schema}' """
        return self.sql_to_pandas(query)

    @singledispatchmethod
    def upload_to_db(self, source, destination: str, pre_truncate: bool = False):
        raise NotImplementedError("Input data format not supported!")

    @upload_to_db.register
    def _(self, source: list, destination: str, pre_truncate: bool = False):
        if len(source) > 0 and not isinstance(source[0], tuple):
            logging.warning(
                """
                This method expects a list of tuples. Each tuple should contain values
                for each column (explicit None when missing) with proper types!
                For unordered, please use a DF or a dict() as source!
                """
            )
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor = conn.cursor()
                query = "INSERT INTO %s VALUES %%s ON CONFLICT DO NOTHING" % (
                    destination
                )

                if pre_truncate is True:
                    # Truncate table before Insert
                    query = f"TRUNCATE {destination}; " + query
                    logging.debug("TRUNCATE statement added before Insert")

                psycopg2.extras.execute_values(cursor, query, source)
                conn.commit()
                cursor.close()
                logging.debug("Data uploaded to DB")
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            conn.rollback()
            conn.close()
            raise error
        finally:
            conn.close()

    @upload_to_db.register
    def _(
        self,
        source: pd.DataFrame,
        destination: str,
        enforce_null: bool = False,
        pre_truncate: bool = False,
    ):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor = conn.cursor()
                cols = ",".join(source.columns.tolist())
                query = "INSERT INTO %s(%s) VALUES %%s ON CONFLICT DO NOTHING" % (
                    destination,
                    cols,
                )

                if pre_truncate is True:
                    # Truncate table before Insert
                    query = f"TRUNCATE {destination}; " + query
                    logging.debug("TRUNCATE statement added before Insert")

                if enforce_null is True:
                    # cast pd nans to proper PG nulls
                    source.replace([None, np.nan], PG_NULL, inplace=True)
                values = [tuple(x) for x in source.to_numpy()]
                psycopg2.extras.execute_values(cursor, query, values)
                conn.commit()
                cursor.close()
                logging.debug("Data uploaded to DB")
        except psycopg2.ProgrammingError as error:
            conn.rollback()
            conn.close()
            raise IOError(
                f"""{str(error)}
            Tip #1: check if (pandas) column names match the destination table.
            Tip #2: check if all (pandas) columns are easily serializable.
            For example, pandas should store json.dumps not python dict's."""
            )
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            conn.close()
            raise error
        finally:
            conn.close()

    @upload_to_db.register
    def _(
        self,
        source: dict,
        destination: str,
        orient="columns",
        pre_truncate: bool = False,
    ):
        df = pd.DataFrame.from_dict(source, orient=orient)
        return self.upload_to_db(df, destination, pre_truncate)

    @upload_to_db.register
    def _(self, source: str, destination: str, pre_truncate: bool = False, **kwargs):
        df = pd.read_csv(source, **kwargs)
        return self.upload_to_db(df, destination, pre_truncate)

    @upload_to_db.register
    def _(self, source: Path, destination: str, pre_truncate: bool = False, **kwargs):
        return self.upload_to_db(str(source), destination, pre_truncate, **kwargs)

    def sanitise_query(self, raw_query: str) -> str:
        query_lines = raw_query.splitlines()
        query_lines = [
            line.strip() for line in query_lines if not line.strip().startswith("--")
        ]
        sanitised_query = "\n".join(query_lines)
        min_valid_query_set_len = len(set("SELECT"))
        if len(set(sanitised_query)) >= min_valid_query_set_len:
            return sanitised_query
        else:
            return None

    def multiqueries_split(self, multiqueries: str) -> List[str]:
        queries = []
        raw_queries = sqlparse.split(multiqueries)
        for query in raw_queries:
            sanitised_query = self.sanitise_query(query)
            if sanitised_query is not None:
                queries.append(sanitised_query)
        return queries

    def safe_exec_multiquery(self, queries: list):
        """
        Executes multiple queries in a single cursor and commits at the end.
        Rollbacks if one query is unsuccessful - needed e.g. for migrations
        """
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as curs:
                for query in queries:
                    self.execute_and_log_query(curs, query)
                # commit at the end of loop
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            conn.rollback()
            logging.error(
                f"Safe multiquery execution was rolled back because of error: {str(error)}"
            )
            conn.close()
            raise error
        finally:
            conn.close()

    def vacuum_full(self, table_name: str):
        """Perform a VACUUM FULL on given table,
        that must be done out of a transaction block"""

        conn = self.get_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        try:
            with conn.cursor() as cursor:
                self.execute_and_log_query(cursor, f"VACUUM FULL {table_name}")

        except (
            Exception,
            psycopg2.DatabaseError,
            psycopg2.errors.InvalidTextRepresentation,
        ) as error:
            conn.rollback()
            logging.error(f"Vacuum Full failed for table {table_name}: {str(error)}")
            conn.close()
            raise error
        finally:
            conn.close()
        return "Done"

    def copy_expert_from_pandas(
        self,
        source: pd.DataFrame,
        destination: str,
        update_on_conflict: bool = False,
        constraint_cols: List = None,
        update_cols: List = None,
        except_filter: str = None,
        quotechar: str = '"',
        sep: str = "\t",
        null_char: str = "",
        pre_truncate: bool = False,
    ):
        """
        Index will be ignored;
        If needed, create a new column named "id" or as named in your table
        Mandatory field: constraint_cols when update_on_conflict is True
        Quote char param for pandas to_csv enforced to support json dumps fields

        If except_filter: str is provided SELECT EXCEPT will be used with
        the except filter

        if pre_truncate is True, the table is truncated before Inserting
        """

        conn = self.get_connection()

        buffer = StringIO()
        source.to_csv(
            buffer,
            index=False,
            header=None,
            quotechar=quotechar,
            sep=sep,
        )
        buffer.seek(0)

        inp_cols = source.columns.tolist()
        inp_cols_str = ", ".join(inp_cols)

        temp_destination = "temp"
        # remove the clone from Write-Ahead-Logs
        sql_create_temp_table = f"""
            CREATE TEMPORARY TABLE IF NOT EXISTS {temp_destination}
            (LIKE {destination} INCLUDING ALL) ON COMMIT DROP
        """

        if update_on_conflict is True:
            constraint_cols_str = ", ".join(constraint_cols)
            if update_cols is None:
                update_cols = list(set(inp_cols).difference(constraint_cols))
            excluded_cols_str = ", ".join(
                [f"{col} = EXCLUDED.{col}" for col in update_cols]
            )

            if except_filter is not None:
                except_query = (
                    f"EXCEPT SELECT {inp_cols_str} FROM {destination} {except_filter}"
                )
            else:
                except_query = ""

            sql_merge = f"""
            INSERT INTO {destination} ({inp_cols_str})
            SELECT {inp_cols_str} FROM {temp_destination}

            {except_query}

            ON CONFLICT ({constraint_cols_str}) DO UPDATE
            SET {excluded_cols_str}
            """
        else:
            sql_merge = f"""
            INSERT INTO {destination}
            SELECT * FROM {temp_destination}
            ON CONFLICT DO NOTHING
            """

        try:
            logging.info("Started uploading from the input stream")
            with conn.cursor() as cursor:
                cursor.execute(sql_create_temp_table)
                # cause single quote in psql is double single quote ''
                if quotechar == "'":
                    sql_quote_char = "''"
                else:
                    sql_quote_char = quotechar
                cursor.copy_expert(
                    sql=f"""
                        COPY {temp_destination} ({inp_cols_str})
                        FROM STDIN WITH CSV DELIMITER
                        '{sep}' NULL '{null_char}' QUOTE '{sql_quote_char}';
                        """,
                    file=buffer,
                )

                if pre_truncate is True:
                    # Truncate table before Insert
                    cursor.execute(f"TRUNCATE {destination}")
                    logging.debug(f"{destination} truncated before insert")

                cursor.execute(sql_merge)
                conn.commit()
            logging.info("Finished uploading from the input stream")
        except (
            Exception,
            psycopg2.DatabaseError,
            psycopg2.errors.InvalidTextRepresentation,
        ) as error:
            conn.rollback()
            logging.error(
                f"Copy from input buffer was rolled back because of error: {str(error)}"
            )
            conn.close()
            raise error
        finally:
            conn.close()

    def check_and_log_read_from_main_db(self, query: str):
        """
        Will be removed, once reads from main will be forbidden as an exception
        """
        if "returning " in str(query).lower() or "returning\n" in str(query).lower():
            return

        if self.db == Databases.delta_main and not self.for_maintainance:
            logging.error("Reading from delta_main", extra={"data": {"query": query}})

    def postgres_transaction(self, func):
        conn = self.get_connection()
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                result = func(cursor)
                conn.commit()
                return result
        except:
            conn.rollback()
            conn.close()
            raise

        finally:
            conn.close()

    @staticmethod
    def _update(cursor, source, where_and_columns, destination):
        for row in source:
            column_values = ", ".join([f"{column}=%s" for column in row.keys()])
            column_values_morgified = cursor.mogrify(
                column_values, list(row.values())
            ).decode()

            where = " AND ".join([f"{column} = %s" for column in where_and_columns])
            where_mogrified = cursor.mogrify(
                where, [row[column] for column in where_and_columns]
            ).decode()

            query = f"""
                UPDATE {destination}
                SET {column_values_morgified}
                WHERE {where_mogrified}
            """

            cursor.execute(query)

    def update(
        self,
        source: List[dict],
        destination: str,
        where_and_columns: list,
        cursor=None,
    ):
        f = partial(
            self._update,
            source=source,
            where_and_columns=where_and_columns,
            destination=destination,
        )

        if cursor is not None:
            return f(cursor)
        else:
            return self.postgres_transaction(f)

    @staticmethod
    def _upsert(cursor, source, batch_size, constraint_columns, destination):
        for page_start in range(0, len(source), batch_size):
            column_names = ", ".join(source[0].keys())

            column_values_placeholder = f"({', '.join(['%s'] * len(source[0]))})"
            page = source[page_start : page_start + batch_size]
            column_values_mogrified = [
                cursor.mogrify(column_values_placeholder, tuple(row.values())).decode()
                for row in page
            ]
            column_values = ",".join(column_values_mogrified)

            constraint_query = "ON CONFLICT DO NOTHING"
            if len(constraint_columns) > 0:
                constraints = ", ".join(constraint_columns)
                update_on_conflict_values = ", ".join(
                    [f"EXCLUDED.{key}" for key in source[0].keys()]
                )
                constraint_query = f"""
                ON CONFLICT ({constraints}) DO
                UPDATE SET ({column_names}) = ({update_on_conflict_values})
                """

            query = f"""
                INSERT INTO {destination} ({column_names})
                VALUES {column_values}
                {constraint_query}
            """
            cursor.execute(query)

    def upsert(
        self,
        source: List[dict],
        destination: str,
        constraint_columns: list = [],
        batch_size=200,
        cursor=None,
    ):
        f = partial(
            self._upsert,
            source=source,
            batch_size=batch_size,
            constraint_columns=constraint_columns,
            destination=destination,
        )

        if cursor is not None:
            return f(cursor)
        else:
            return self.postgres_transaction(f)


def cross_db_join(
    left_sql: str,
    left_db: Databases,
    right_sql: str,
    right_db: Databases,
    join_type: CrossDBJoinType,
    on: Union[str, list],
    **kwargs,
) -> pd.DataFrame:
    """
    left_sql: query to be executed on the first DB
    left_db: first DB type e.g. Databases.backend_replica, Databases.delta_replica
    right_sql: query to be executed on the second DB
    right_db: second DB type e.g. Databases.backend_replica, Databases.delta_replica
    join_type: desired type of join
    on: column or list of columns on which the join should be applied;
        recommended to use the same column in left_sql and right_sql with 'AS'
    **kwargs: kwargs to be passed to pd.merge for advanced functionality
    https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.merge.html
    """
    left_df = PostgresConnector(db=left_db).sql_to_pandas(left_sql)
    right_df = PostgresConnector(db=right_db).sql_to_pandas(right_sql)
    return left_df.merge(right_df, how=str(join_type), on=on, **kwargs)


def copy_between_dbs(
    source_table: str,
    target_table: str = None,
    source_db: Databases = Databases.delta_replica,
    target_db: Databases = Databases.delta_main,
    filter_query: str = "",
    limit_query: str = "LIMIT 10000",
):
    source_db_conn = PostgresConnector(db=source_db)
    target_db_conn = PostgresConnector(db=target_db)

    if target_table is None:
        target_table = source_table

    source_list = source_db_conn.sql_to_list(
        f"SELECT * FROM {source_table} {filter_query} {limit_query}"
    )

    # Dumps any dictionnary befor re-upload
    for l in source_list:
        for i, e in enumerate(l):
            if isinstance(e, dict):
                l[i] = json.dumps(e)

    # Reupload
    target_db_conn.upload_to_db(source_list, destination=target_table)
