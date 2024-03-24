from faker.providers import BaseProvider
from pydantic import BaseModel
from shapely.geometry import Polygon, Point
import random


class Location(BaseModel):
    coordinates: tuple[float, float]


class LocationProvider(BaseProvider):

    def __init__(self, generator, polygon: Polygon):
        super().__init__(generator)
        self.polygon = polygon

    def location(self) -> Location:
        min_x, min_y, max_x, max_y = self.polygon.bounds
        while True:
            p = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
            if self.polygon.contains(p):
                return Location(
                    coordinates=(p.x, p.y)
                )
