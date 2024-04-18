from typing import Literal
import datetime
from zoneinfo import ZoneInfo
import logging
import pandas as pd
from pydantic import BaseModel
from faker import Faker
from src.data_manager import DataManager
from src.ride_simulator import SimulationState, RideRoute
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
    price: int


class Route(BaseModel):
    trip_id: int
    points: str
    speed_avg: float


class Payment(BaseModel):
    id: int
    trip_id: int
    price: int
    tariff: int
    promo: bool


class User(BaseModel):
    id: int
    first_name: str
    last_name: str | None
    phone: str
    sex: Literal['F', 'M'] | None
    birth_date: datetime.date


class Event(BaseModel):
    user_id: int
    timestamp: datetime.datetime
    type_id: int


class DatabaseLoader:
    _data_manager: DataManager
    _database: Database
    _fake: Faker
    _logger: logging.Logger

    def __init__(self, database: Database, fake: Faker):
        self._data_manager = DataManager()
        self._database = database
        self._fake = fake
        self._logger = logging.getLogger(__class__.__name__)
        pd.options.display.width = 0

    def prepare_data(self, state_file: str, routes_file: str, tariff: Tariff):
        self._logger.info('Loading state from %s', state_file)
        state: SimulationState = self._data_manager.load_pickle(state_file)
        self._logger.info('Loading routes from %s', routes_file)
        routes: list[RideRoute] = self._data_manager.load_pickle(routes_file)
        self._logger.info('Preparing trips and payments')
        trips, payments = self._prepare_trips_and_payments(state, tariff=tariff)
        self._dump_models_to_parquet(trips, 'trips.parquet')
        self._dump_models_to_parquet(payments, 'payments.parquet')
        self._logger.info('Preparing users')
        users: list[User] = self._prepare_users(state)
        self._dump_models_to_parquet(users, 'users.parquet')
        self._logger.info('Preparing events')
        events: list[Event] = self._prepare_events(state)
        self._dump_models_to_parquet(events, 'events.parquet')
        self._logger.info('Preparing routes')
        routes: list[Route] = self._prepare_routes(routes)
        self._dump_models_to_parquet(routes, 'routes.parquet')

    def create_table_from_parquet(self, table_name: str, schema_name: str, file_name: str):
        self._logger.info('Loading data from %s', file_name)
        df = self._data_manager.load_parquet(file_name)
        self._logger.info('Creating table %s in schema %s', table_name, schema_name)
        self._database.create_table_from_df(table_name, schema_name, df)

    def load_data(self, schema_name: str):
        self.create_table_from_parquet('trips', schema_name, 'trips.parquet')
        # self.create_table_from_parquet('payments', schema_name, 'payments.parquet')
        self.create_table_from_parquet('users', schema_name, 'users.parquet')
        self.create_table_from_parquet('events', schema_name, 'events.parquet')
        # self.create_table_from_parquet('routes', schema_name, 'routes.parquet')

    def create_version_table(self, schema_name: str, data_version: str):
        df = pd.DataFrame([{
            'version': data_version,
            'updated_at': pd.Timestamp.now(tz='UTC')
        }])
        self._database.create_table_from_df('version', schema_name, df)

    def _prepare_trips_and_payments(self, state: SimulationState, tariff: Tariff) -> tuple[list[Trip], list[Payment]]:
        trips: list[Trip] = []
        payments: list[Payment] = []
        for r in state.ride_details:
            trip_start_hour: int = r.start_datetime.hour
            if tariff.day_start_hour <= trip_start_hour < tariff.night_start_hour:
                tariff_price: float = tariff.day
            else:
                tariff_price = tariff.night
            if r.promo_code:
                price: int = 0
            else:
                price = int(r.duration_s / 60 * tariff_price * 100)
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
                price=price
            )
            payment = Payment(
                id=len(payments) + 1,
                trip_id=r.id,
                price=price,
                tariff=int(tariff_price * 100),
                promo=r.promo_code
            )
            trips.append(trip)
            payments.append(payment)
        return trips, payments

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

    def _prepare_events(self, state: SimulationState) -> list[Event]:
        events: list[Event] = []
        for r in state.ride_details:
            if r.start_datetime == r.desired_start_datetime:
                start_datetime: datetime.datetime = r.start_datetime + datetime.timedelta(seconds=10)
            else:
                start_datetime = r.start_datetime
            events.append(Event(
                user_id=r.person_id,
                timestamp=r.desired_start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow'))
                .astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
                type_id=0  # start_search
            ))
            events.append(Event(
                user_id=r.person_id,
                timestamp=start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow'))
                .astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
                type_id=1  # book_scooter
            ))
            events.append(Event(
                user_id=r.person_id,
                timestamp=r.end_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow'))
                .astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
                type_id=2  # release_scooter
            ))
        for cr in state.cancelled_rides:
            events.append(Event(
                user_id=cr.person_id,
                timestamp=cr.start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow'))
                .astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
                type_id=0  # start_search
            ))
            events.append(Event(
                user_id=cr.person_id,
                timestamp=cr.start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow'))
                          .astimezone(ZoneInfo('UTC')).replace(tzinfo=None) + datetime.timedelta(
                    seconds=cr.find_available_time_s),
                type_id=3  # cancel_search
            ))
        # Introduce duplicates
        num_duplicates: int = int(len(events) * 0.05)
        events_to_duplicate = self._fake.random.choices(events, k=num_duplicates)
        events.extend(events_to_duplicate)
        events = sorted(events, key=lambda e: e.timestamp)
        return events

    def _prepare_routes(self, routes_in: list[RideRoute]) -> list[Route]:
        routes: list[Route] = []
        for r in routes_in:
            points: list[tuple[float, float]] = r.points.copy()
            if len(points) == 1:
                points.extend(points)
            points_str: str = ''
            for p in points:
                points_str += f'{p[0]} {p[1]},'
            route = Route(
                trip_id=r.ride_id,
                points=f'LINESTRING({points_str[:-1]})',
                speed_avg=r.speed_avg
            )
            routes.append(route)
        return routes

    def _dump_models_to_parquet(self, data: list[BaseModel], file_name: str):
        data_dict: list[dict] = [d.model_dump() for d in data]
        df = pd.DataFrame(data_dict)
        self._data_manager.dump_parquet(df, file_name)
