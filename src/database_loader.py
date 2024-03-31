import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from pydantic import BaseModel
from src.data_manager import DataManager
from src.ride_simulator import SimulationState
from src.database import Database


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
    last_name: str
    email: str
    phone: str
    birth_date: datetime.date


class DatabaseLoader:
    _data_manager: DataManager
    _database: Database

    def __init__(self, database: Database):
        self._data_manager = DataManager()
        self._database = database
        pd.options.display.width = 0

    def prepare_data(self, state: SimulationState):
        trips: list[Trip] = self._prepare_trips(state)
        self._dump_models_to_parquet(trips, 'trips.parquet')

    def create_table_from_parquet(self, table_name: str, schema_name: str, file_name: str):
        df = self._data_manager.load_parquet(file_name)
        self._database.create_table_from_df(table_name, schema_name, df)

    def load_data(self):
        self.create_table_from_parquet('trips', 'dbt_scooters', 'trips.parquet')
        self.create_table_from_parquet('parking', 'dbt_scooters', 'parking.parquet')
        self.create_table_from_parquet('scooters', 'dbt_scooters', 'scooters.parquet')
        self.create_table_from_parquet('zones', 'dbt_scooters', 'zones.parquet')
        self.create_table_from_parquet('rides', 'dbt_scooters', 'rides.parquet')
        self.create_table_from_parquet('events', 'dbt_scooters', 'events.parquet')

    def _prepare_trips(self, state: SimulationState) -> list[Trip]:
        trips: list[Trip] = []
        for r in state.ride_details:
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
                distance=r.distance_m
            )
            trips.append(trip)
        return trips

    def _prepare_users(self, state: SimulationState) -> list[User]:
        users: list[User] = []
        for p in state.persons.values():
            user = User(
                id=p.id,
                first_name=p.first_name,
                last_name=p.last_name,
                email=p.email,
                phone=p.phone,
                birth_date=p.birth_date
            )
            users.append(user)
        return users

    def _dump_models_to_parquet(self, data: list[BaseModel], file_name: str):
        data_dict: list[dict] = [d.model_dump() for d in data]
        df = pd.DataFrame(data_dict)
        self._data_manager.dump_parquet(df, file_name)
