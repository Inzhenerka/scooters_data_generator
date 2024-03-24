from typing import Literal
from faker.providers import BaseProvider
from pydantic import BaseModel


class Person(BaseModel):
    id: int
    sex: Literal['F', 'M']
    age: int
    first_name: str
    last_name: str
    work_trips: bool
    home_coordinates: tuple[float, float] | None
    work_coordinates: tuple[float, float] | None
    work_start_hour: float
    work_end_hour: float
    occasional_workday_trip_chance: int
    occasional_weekend_trip_chance: int
    skip_trip_chance: int
    find_available_attempts: int
    wait_minutes_max: int
    speed_average: float


class PersonProvider(BaseProvider):

    def __init__(self, generator):
        super().__init__(generator)
        self.person_id: int = 1

    def person(self) -> Person:
        sex: Literal['F', 'M'] = self.random_element(['F', 'M'])
        if sex == 'M':
            first_name: str = self.generator.first_name_male()
            last_name: str = self.generator.last_name_male()
        else:
            first_name = self.generator.first_name_female()
            last_name = self.generator.last_name_female()
        work_trips: bool = self.generator.boolean(chance_of_getting_true=30)
        if work_trips:
            work_coordinates: tuple[float, float] | None = self.generator.location().coordinates
            home_coordinates: tuple[float, float] | None = self.generator.location().coordinates
        else:
            work_coordinates = None
            home_coordinates = None
        person_id = self.person_id
        self.person_id += 1
        return Person(
            id=person_id,
            sex=sex,
            age=self.generator.random_int(min=18, max=60),
            first_name=first_name,
            last_name=last_name,
            work_trips=work_trips,
            home_coordinates=home_coordinates,
            work_coordinates=work_coordinates,
            work_start_hour=self.random_int(800, 1000) / 100,
            work_end_hour=self.random_int(1700, 1900) / 100,
            occasional_workday_trip_chance=self.randomize_nb_elements(10),
            occasional_weekend_trip_chance=self.random_int(0, 20),
            skip_trip_chance=self.randomize_nb_elements(10),
            find_available_attempts=self.random_int(0, 2),
            wait_minutes_max=self.random_int(0, 10),
            speed_average=self.random_int(500, 1500) / 100
        )
