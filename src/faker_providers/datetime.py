from typing import Literal
from collections import OrderedDict
import datetime
from enum import StrEnum
from faker.providers import BaseProvider


class WeatherCondition(StrEnum):
    RAIN = "rain"
    SUN = "sun"
    CLOUDS = "clouds"


class DatetimeProvider(BaseProvider):

    def datetime_within_day(
            self,
            date: datetime.date,
            night_chance: int = 50,
            day_start_hour: int = 6,
            night_start_hour: int = 22
    ):
        day_chance: int = 100 - night_chance
        periods: list[tuple[Literal['day', 'night'], int, int]] = [
            ('day', day_start_hour, night_start_hour),
            ('night', night_start_hour, 24),
            ('night', 0, day_start_hour)
        ]

        # Choose period based on weights
        chosen_period = self._random_element(periods, weights=[day_chance, night_chance / 2, night_chance / 2])[0]
        period_name: Literal['day', 'night']
        period_name, start_hour, end_hour = chosen_period

        # Generate a random hour, minute, and second within the chosen period
        if period_name == 'night' and start_hour == night_start_hour:
            # For the night period that starts after the day period and goes to midnight
            hour: int = self.generator.random_int(start_hour, end_hour - 1)
        else:
            hour = self.generator.random_int(start_hour, end_hour - 1) if start_hour != end_hour else start_hour
        minute: int = self.generator.random_int(0, 59)
        second: int = self.generator.random_int(0, 59)

        # Handle the case for night time rolling over to the next day
        if period_name == 'night' and start_hour == 0:
            date += datetime.timedelta(days=1)

        # Construct and return the datetime
        return datetime.datetime.combine(
            date, datetime.datetime.min.time()
        ) + datetime.timedelta(hours=hour, minutes=minute, seconds=second)

    def datetime_near(self, dt: datetime.datetime, std_seconds: int):
        # Generate a normally distributed offset in seconds using Faker's random generator
        offset_seconds: int = int(self.generator.random.gauss(mu=0, sigma=std_seconds))
        # Create a timedelta based on the offset
        offset = datetime.timedelta(seconds=offset_seconds)
        # Add the offset to the given datetime to get the random datetime
        random_datetime = dt + offset
        return random_datetime

    def _random_element(self, elements: any, weights: list[float]) -> any:
        return self.generator.random_elements(
            elements=OrderedDict(zip(elements, weights)),
            length=1,
            use_weighting=True)
