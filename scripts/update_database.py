import os
import logging
from dotenv import load_dotenv
from faker import Faker
from src.database import Database, ConnectionParameters
from src.database_loader import DatabaseLoader, Tariff

DATA_VERSION = '1.0.0'
SCHEMA_NAME = 'scooters_raw'

load_dotenv()
logging.basicConfig(level=logging.INFO)
fake = Faker('ru_RU')
Faker.seed(0)
db = Database()
dl = DatabaseLoader(database=db, fake=fake)

jdbc_url: str = os.environ['JDBC_URL']
conn_params: ConnectionParameters = db.parse_jdbc_url(jdbc_url)

db.connect(conn_params)
db.create_schema(SCHEMA_NAME)
dl.create_version_table(SCHEMA_NAME, DATA_VERSION)

tariff = Tariff(day=10, night=5)
print('Preparing data')
dl.prepare_data('sim_state_3.pickle', routes_file='routes.pickle', tariff=tariff)
print('Uploading data to the database')
dl.load_data(SCHEMA_NAME)
# dl.create_table_from_parquet('trips', SCHEMA_NAME, 'trips.parquet')
