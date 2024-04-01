from typing import Literal
import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from pydantic import BaseModel
from faker import Faker
from src.data_manager import DataManager
from src.ride_simulator import SimulationState
from src.database import Database


class Tariff(BaseModel):
    day: float
    night: float
    day_start_hour: int = 6
    night_start_hour: int = 22


class Trip(BaseModel):
    id: int
    user_id: int
    scooter_hw_id: str
    started_at: datetime.datetime
    finished_at: datetime.datetime
    start_lat: float
    start_lon: float
    finish_lat: float
    finish_lon: float
    distance: float
    cost: int


class User(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    phone: str
    sex: Literal['F', 'M'] | None
    birth_date: datetime.date


class DatabaseLoader:
    _data_manager: DataManager
    _database: Database
    _fake: Faker

    def __init__(self, database: Database, fake: Faker):
        self._data_manager = DataManager()
        self._database = database
        self._fake = fake
        pd.options.display.width = 0

    def prepare_data(self, state_file: str, tariff: Tariff):
        state: SimulationState = self._data_manager.load_pickle(state_file)
        trips: list[Trip] = self._prepare_trips(state, tariff=tariff)
        users: list[User] = self._prepare_users(state)
        self._dump_models_to_parquet(trips, 'trips.parquet')
        self._dump_models_to_parquet(users, 'users.parquet')

    def create_table_from_parquet(self, table_name: str, schema_name: str, file_name: str):
        df = self._data_manager.load_parquet(file_name)
        self._database.create_table_from_df(table_name, schema_name, df)

    def load_data(self, schema_name: str):
        self.create_table_from_parquet('trips', schema_name, 'trips.parquet')
        self.create_table_from_parquet('users', schema_name, 'users.parquet')

    def create_version_table(self, schema_name: str, data_version: str):
        df = pd.DataFrame([{
            'version': data_version,
            'updated_at': pd.Timestamp.now(tz='UTC')
        }])
        self._database.create_table_from_df('version', schema_name, df)

    def _prepare_trips(self, state: SimulationState, tariff: Tariff) -> list[Trip]:
        trips: list[Trip] = []
        for r in state.ride_details:
            if r.promo_code:
                cost: int = 0
            else:
                trip_start_hour: int = r.start_datetime.hour
                if tariff.day_start_hour <= trip_start_hour < tariff.night_start_hour:
                    tariff_price: float = tariff.day
                else:
                    tariff_price = tariff.night
                cost = int(r.duration_s / 60 * tariff_price * 100)
            trip = Trip(
                id=r.id,
                user_id=r.person_id,
                scooter_hw_id=state.scooters[r.scooter_id].hardware_id,
                started_at=r.start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow')),
                finished_at=r.end_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow')),
                start_lat=state.parking[r.start_parking_id].coordinates[0],
                start_lon=state.parking[r.start_parking_id].coordinates[1],
                finish_lat=state.parking[r.end_parking_id].coordinates[0],
                finish_lon=state.parking[r.end_parking_id].coordinates[1],
                distance=r.distance_m,
                cost=cost
            )
            trips.append(trip)
        return trips

    def _prepare_users(self, state: SimulationState) -> list[User]:
        users: list[User] = []
        for p in state.persons.values():
            sex: Literal['F', 'M'] | None = p.sex if self._fake.boolean(chance_of_getting_true=90) else None
            last_name: str | None = p.last_name if self._fake.boolean(chance_of_getting_true=60) else None
            user = User(
                id=p.id,
                first_name=p.first_name,
                last_name=last_name,
                phone=p.phone,
                sex=sex,
                birth_date=p.birth_date
            )
            users.append(user)
        return users

    def _dump_models_to_parquet(self, data: list[BaseModel], file_name: str):
        data_dict: list[dict] = [d.model_dump() for d in data]
        df = pd.DataFrame(data_dict)
        self._data_manager.dump_parquet(df, file_name)
