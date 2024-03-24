import datetime
from faker import Faker
from pydantic import BaseModel
from src.faker_providers.person import Person
from src.faker_providers.weather import WeatherCondition


class Ride(BaseModel):
    user_id: int
    datetime: datetime.datetime
    start_coordinates: tuple[float, float] | None = None
    end_coordinates: tuple[float, float] | None = None


class RidePlanner:
    _persons: list[Person]
    _fake: Faker
    _WEEKDAY_NIGHT_CHANCE: int = 3
    _WEEKEND_NIGHT_CHANCE: int = 7
    _WORK_TRIP_STD_S: int = 60 * 10
    _RAIN_SKIP_CHANCE: int = 50

    def __init__(self, persons: list[Person], fake: Faker):
        self._persons = persons
        self._fake = fake

    def plan_rides(
            self,
            start_date: datetime.date,
            end_date: datetime.date
    ) -> list[Ride]:
        rides: list[Ride] = []
        for day in range((end_date - start_date).days + 1):
            date: datetime.date = start_date + datetime.timedelta(days=day)
            weather: WeatherCondition = self._fake.weather()
            for person in self._persons:
                if date.weekday() < 5:
                    if self._fake.boolean(chance_of_getting_true=person.occasional_workday_trip_chance):
                        if not self._check_skip_trip(person, weather):
                            dt: datetime.datetime = self._fake.datetime_within_day(
                                date, night_chance=self._WEEKDAY_NIGHT_CHANCE
                            )
                            self._add_ride(rides, person.id, dt)
                else:
                    if self._fake.boolean(chance_of_getting_true=person.occasional_weekend_trip_chance):
                        if not self._check_skip_trip(person, weather):
                            dt: datetime.datetime = self._fake.datetime_within_day(
                                date, night_chance=self._WEEKEND_NIGHT_CHANCE
                            )
                            self._add_ride(rides, person.id, dt)
                if person.work_trips:
                    dt_work: datetime.datetime = self._fake.datetime_near(
                        self._datetime_from_hour(date, person.work_start_hour), std_seconds=self._WORK_TRIP_STD_S
                    )
                    dt_home: datetime.datetime = self._fake.datetime_near(
                        self._datetime_from_hour(date, person.work_end_hour), std_seconds=self._WORK_TRIP_STD_S
                    )
                    if not self._check_skip_trip(person, weather):
                        self._add_ride(rides, person.id, dt_work, person.home_coordinates, person.work_coordinates)
                    if not self._check_skip_trip(person, weather):
                        self._add_ride(rides, person.id, dt_home, person.work_coordinates, person.home_coordinates)
        return rides

    def _add_ride(
            self,
            rides: list[Ride],
            person_id: int,
            dt: datetime.datetime,
            start_coordinates: tuple[float, float] | None = None,
            end_coordinates: tuple[float, float] | None = None
    ):
        if start_coordinates is None:
            start_coordinates = self._fake.location().coordinates
        if end_coordinates is None:
            end_coordinates = self._fake.location().coordinates
        rides.append(Ride(
            user_id=person_id,
            datetime=dt,
            start_coordinates=start_coordinates,
            end_coordinates=end_coordinates
        ))

    def _check_skip_trip(self, person: Person, weather: WeatherCondition) -> bool:
        if weather == WeatherCondition.RAIN:
            skip_trip_chance: int = self._RAIN_SKIP_CHANCE
        else:
            skip_trip_chance = person.skip_trip_chance
        return self._fake.boolean(chance_of_getting_true=skip_trip_chance)

    @staticmethod
    def _datetime_from_hour(date: datetime.date, hour: float) -> datetime.datetime:
        return datetime.datetime.combine(date, datetime.datetime.min.time()) + datetime.timedelta(hours=hour)
