import datetime
from faker import Faker
from pydantic import BaseModel
from src.faker_providers.parking import Parking
from src.faker_providers.person import Person
from src.faker_providers.weather import WeatherCondition


class DailyWeather(BaseModel):
    date: datetime.date
    condition: WeatherCondition


class RidePlannerConfig(BaseModel):
    weekday_night_chance: int = 3
    weekend_night_chance: int = 7
    work_trip_std_s: int = 60 * 10
    rain_skip_chance: int = 50


class Ride(BaseModel):
    id: int
    person_id: int
    datetime: datetime.datetime
    start_parking_id: int | None = None
    end_parking_id: int | None = None


class SimulationPlan(BaseModel):
    start_date: datetime.date
    end_date: datetime.date
    persons: list[Person]
    weather: list[DailyWeather]
    rides: list[Ride]
    parking: list[Parking]


class Planner:
    _fake: Faker

    def __init__(self, fake: Faker):
        self._fake = fake

    def plan_simulation(
            self,
            start_date: datetime.date,
            end_date: datetime.date,
            persons_count: int,
            max_parking_capacity: int = 20
    ) -> SimulationPlan:
        print('Planning parking')
        parking: list[Parking] = self.plan_parking(max_capacity=max_parking_capacity)
        print('Planning persons')
        persons: list[Person] = self.plan_persons(parking=parking, base_year=start_date.year, count=persons_count)
        print('Planning weather')
        weather: list[DailyWeather] = self.plan_weather(start_date=start_date, end_date=end_date)
        print('Planning rides')
        rides: list[Ride] = self.plan_rides(persons=persons, historical_weather=weather, parking=parking)
        return SimulationPlan(
            start_date=start_date,
            end_date=end_date,
            persons=persons,
            weather=weather,
            rides=rides,
            parking=parking
        )

    def plan_persons(self, parking: list[Parking], base_year: int, count: int) -> list[Person]:
        return [self._fake.person(parking=parking, base_year=base_year) for _ in range(count)]

    def plan_parking(self, count: int | None = None, max_capacity: int = 20) -> list[Parking]:
        if count is None:
            count = self._fake.total_parking_num()
        return [self._fake.parking(max_capacity) for _ in range(count)]

    def plan_weather(self, start_date: datetime.date, end_date: datetime.date) -> list[DailyWeather]:
        weather: list[DailyWeather] = []
        for day in range((end_date - start_date).days + 1):
            date: datetime.date = start_date + datetime.timedelta(days=day)
            condition: WeatherCondition = self._fake.weather()
            weather.append(DailyWeather(date=date, condition=condition))
        return weather

    def plan_rides(
            self,
            persons: list[Person],
            historical_weather: list[DailyWeather],
            parking: list[Parking],
            config: RidePlannerConfig | None = None
    ) -> list[Ride]:
        if config is None:
            config = RidePlannerConfig()
        rides: list[Ride] = []
        for weather in historical_weather:
            date: datetime.date = weather.date
            weather_condition: WeatherCondition = weather.condition
            for person in persons:
                if date.weekday() < 5:
                    if self._fake.boolean(chance_of_getting_true=person.occasional_workday_trip_chance):
                        if not self._check_skip_trip(person, weather_condition, config):
                            dt: datetime.datetime = self._fake.datetime_within_day(
                                date, night_chance=config.weekday_night_chance
                            )
                            self._add_ride(rides, person.id, dt, parking)
                else:
                    if self._fake.boolean(chance_of_getting_true=person.occasional_weekend_trip_chance):
                        if not self._check_skip_trip(person, weather_condition, config):
                            dt: datetime.datetime = self._fake.datetime_within_day(
                                date, night_chance=config.weekend_night_chance
                            )
                            self._add_ride(rides, person.id, dt, parking)
                if person.work_trips:
                    dt_work: datetime.datetime = self._fake.datetime_near(
                        self._datetime_from_hour(date, person.work_start_hour), std_seconds=config.work_trip_std_s
                    )
                    dt_home: datetime.datetime = self._fake.datetime_near(
                        self._datetime_from_hour(date, person.work_end_hour), std_seconds=config.work_trip_std_s
                    )
                    if not self._check_skip_trip(person, weather_condition, config):
                        self._add_ride(
                            rides, person.id, dt_work, parking, person.home_parking_id, person.work_parking_id
                        )
                    if not self._check_skip_trip(person, weather_condition, config):
                        self._add_ride(
                            rides, person.id, dt_home, parking, person.work_parking_id, person.home_parking_id
                        )
        rides.sort(key=lambda r: r.datetime)
        return rides

    def _add_ride(
            self,
            rides: list[Ride],
            person_id: int,
            dt: datetime.datetime,
            parking: list[Parking],
            start_parking_id: int | None = None,
            end_parking_id: int | None = None
    ):
        if start_parking_id is None:
            start_parking_id = self._fake.random_element(parking).id
        if end_parking_id is None:
            end_parking_id = self._fake.random_element(parking).id
        ride_id: int = len(rides) + 1
        rides.append(Ride(
            id=ride_id,
            person_id=person_id,
            datetime=dt,
            start_parking_id=start_parking_id,
            end_parking_id=end_parking_id
        ))

    def _check_skip_trip(self, person: Person, weather: WeatherCondition, config: RidePlannerConfig) -> bool:
        if weather == WeatherCondition.RAIN:
            skip_trip_chance: int = config.rain_skip_chance
        else:
            skip_trip_chance = person.skip_trip_chance
        return self._fake.boolean(chance_of_getting_true=skip_trip_chance)

    @staticmethod
    def _datetime_from_hour(date: datetime.date, hour: float) -> datetime.datetime:
        return datetime.datetime.combine(date, datetime.datetime.min.time()) + datetime.timedelta(hours=hour)
