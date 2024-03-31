import csv
from pydantic import BaseModel
from faker.providers import BaseProvider
import random


class Scooter(BaseModel):
    id: int
    hardware_id: str
    distance_m: float


class ScooterProvider(BaseProvider):

    def __init__(self, generator, hardware_ids: list[str]):
        super().__init__(generator)
        self.hardware_ids = hardware_ids
        self.scooter_id: int = 1

    def scooter(self) -> Scooter:
        hardware_id = self.random_element(self.hardware_ids)
        mileage = random.uniform(0, 100)
        scooter_id: int = self.scooter_id
        self.scooter_id += 1
        return Scooter(
            id=scooter_id,
            hardware_id=hardware_id,
            distance_m=mileage
        )
