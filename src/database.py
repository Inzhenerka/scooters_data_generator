import re
import ssl

import pandas as pd
import pg8000
from urllib.parse import urlparse
from pydantic import BaseModel
import awswrangler as wr
from src.data_manager import DataManager


class ConnectionParameters(BaseModel):
    host: str
    port: int
    database: str
    user: str
    password: str


class Database:
    _conn: pg8000.Connection

    def connect(self, conn_params: ConnectionParameters):
        ssl_context = ssl.create_default_context()
        self._conn = pg8000.connect(
            host=conn_params.host,
            port=conn_params.port,
            database=conn_params.database,
            user=conn_params.user,
            password=conn_params.password,
            ssl_context=ssl_context
        )
        return self._conn

    def create_table_from_df(self, table_name: str, schema_name: str, df: pd.DataFrame):
        wr_dtype: dict[str, str] = {}
        for column, dtype in df.dtypes.items():
            if hasattr(dtype, 'tz') and dtype.tz is not None:
                wr_dtype[str(column)] = 'timestamptz'
        wr.postgresql.to_sql(
            df=df,
            table=table_name,
            schema=schema_name,
            index=False,
            mode='overwrite',
            dtype=wr_dtype,
            chunksize=1000,
            con=self._conn
        )

    def execute_sql(self, sql: str):
        cursor = self._conn.cursor()
        cursor.execute(sql)
        cursor.close()

    def create_schema(self, schema_name: str):
        self.execute_sql(f'CREATE SCHEMA IF NOT EXISTS {schema_name}')

    @staticmethod
    def parse_jdbc_url(jdbc_url: str) -> ConnectionParameters:
        parsed_url = urlparse(jdbc_url)
        return ConnectionParameters(
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            database=parsed_url.path.lstrip('/'),
            user=parsed_url.username,
            password=parsed_url.password
        )
