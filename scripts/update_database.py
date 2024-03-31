import os
from dotenv import load_dotenv
from src.database import Database, ConnectionParameters

DATA_VERSION = '1.0.0'
SCHEMA_NAME = 'dbt_scooters'

load_dotenv()
db = Database()

jdbc_url: str = os.environ['JDBC_URL']
conn_params: ConnectionParameters = db.parse_jdbc_url(jdbc_url)

db.connect(conn_params)
db.create_schema(SCHEMA_NAME)
db.create_version_table(SCHEMA_NAME, DATA_VERSION)
db.create_table_from_parquet('trips', SCHEMA_NAME, 'trips.parquet')
