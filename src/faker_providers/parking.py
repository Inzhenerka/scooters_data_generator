from pydantic import BaseModel
from faker.providers import BaseProvider
import random


class Parking(BaseModel):
    id: int
    coordinates: tuple[float, float]
    capacity: int
    initial_scooters: int


class ParkingProvider(BaseProvider):

    def __init__(self, generator, coordinates: list[tuple[float, float]]):
        super().__init__(generator)
        self.available_coordinates = coordinates.copy()
        self.parking_id: int = 1

    def parking(self) -> Parking:
        # Ensure there's at least one coordinate available
        if not self.available_coordinates:
            raise ValueError('No available coordinates left for new parking.')
        coordinates_index = random.randint(0, len(self.available_coordinates) - 1)
        coordinates: tuple[float, float] = self.available_coordinates.pop(coordinates_index)
        capacity: int = self.random_element([6, 8, 10, 12])
        initial_scooters: int = self.random_int(min=0, max=capacity)
        parking_id: int = self.parking_id
        self.parking_id += 1
        return Parking(
            id=parking_id,
            coordinates=coordinates,
            capacity=capacity,
            initial_scooters=initial_scooters
        )
