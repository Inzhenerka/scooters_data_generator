from collections import OrderedDict
from enum import StrEnum
from faker.providers import BaseProvider


class WeatherCondition(StrEnum):
    RAIN = "rain"
    SUN = "sun"
    CLOUDS = "clouds"


class WeatherProvider(BaseProvider):

    def weather(self) -> WeatherCondition:
        choices = [WeatherCondition.SUN, WeatherCondition.RAIN, WeatherCondition.CLOUDS]
        # Define weights based on the probabilities
        weights: list[float] = [0.6, 0.15, 0.25]
        return self.generator.random_elements(
            elements=OrderedDict(zip(choices, weights)),
            length=1,
            use_weighting=True)[0]
