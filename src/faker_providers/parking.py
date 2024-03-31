from pydantic import BaseModel
from faker.providers import BaseProvider
from src.faker_providers.scooter import Scooter
from src.city_utils import ZoneParking
import random


class Parking(BaseModel):
    id: int
    coordinates: tuple[float, float]
    graph_node: int
    max_capacity: int
    scooters: list[Scooter]
    closest_parking_id: list[int]


class ParkingProvider(BaseProvider):

    def __init__(self, generator, zone_parking: list[ZoneParking]):
        super().__init__(generator)
        self._total_parking_num: int = len(zone_parking)
        self._available_parking = zone_parking.copy()

    def parking(self, max_capacity: int = 20) -> Parking:
        if not self._available_parking:
            raise ValueError('No available coordinates left for new parking.')
        coordinates_index = random.randint(0, len(self._available_parking) - 1)
        zone_parking: ZoneParking = self._available_parking.pop(coordinates_index)
        initial_scooters_num: int = self.random_int(min=0, max=max_capacity)
        initial_scooters: list[Scooter] = [self.generator.scooter() for _ in range(initial_scooters_num)]
        return Parking(
            id=zone_parking.id,
            coordinates=zone_parking.coordinates,
            graph_node=zone_parking.graph_node,
            max_capacity=max_capacity,
            scooters=initial_scooters,
            closest_parking_id=zone_parking.closest_parking_id
        )

    def total_parking_num(self) -> int:
        return self._total_parking_num
