from typing import Literal
import math
import datetime
from faker.providers import BaseProvider
from pydantic import BaseModel
import phonenumbers
from src.faker_providers.parking import Parking


class Person(BaseModel):
    id: int
    sex: Literal['F', 'M']
    birth_date: datetime.date
    first_name: str
    last_name: str
    phone: str
    promo_codes: int
    work_trips: bool
    home_parking_id: int | None
    work_parking_id: int | None
    work_start_hour: float
    work_end_hour: float
    occasional_workday_trip_chance: int
    occasional_weekend_trip_chance: int
    skip_trip_chance: int
    find_available_time_limit_s: int
    speed_average: float


class PersonProvider(BaseProvider):

    def __init__(self, generator):
        super().__init__(generator)
        self._person_id: int = 1

    def person(self, parking: list[Parking], base_year: int) -> Person:
        sex: Literal['F', 'M'] = self.random_element(['F', 'M'])
        if sex == 'M':
            first_name: str = self.generator.first_name_male()
            last_name: str = self.generator.last_name_male()
        else:
            first_name = self.generator.first_name_female()
            last_name = self.generator.last_name_female()
        work_trips: bool = self.generator.boolean(chance_of_getting_true=30)
        if work_trips:
            work_parking_id: int | None = self.random_element(parking).id
            home_parking_id: int | None = self.random_element(parking).id
        else:
            work_parking_id = None
            home_parking_id = None
        age: int = self._age(18, 99)
        birth_date: datetime.date = self._birth_date(age, base_year)
        person_id = self._person_id
        self._person_id += 1
        return Person(
            id=person_id,
            sex=sex,
            birth_date=birth_date,
            first_name=first_name,
            last_name=last_name,
            phone=self._phone(),
            promo_codes=self.random_int(0, 3),
            work_trips=work_trips,
            home_parking_id=home_parking_id,
            work_parking_id=work_parking_id,
            work_start_hour=self.random_int(800, 1000) / 100,
            work_end_hour=self.random_int(1700, 1900) / 100,
            occasional_workday_trip_chance=self.randomize_nb_elements(10),
            occasional_weekend_trip_chance=self.random_int(0, 20),
            skip_trip_chance=self.randomize_nb_elements(10),
            find_available_time_limit_s=self.random_int(0, 10 * 60),
            speed_average=self.random_int(500, 1500) / 100
        )

    def _phone(self) -> str:
        phone: str = self.generator.phone_number()
        if phone.startswith('8'):
            phone = '+7' + phone[1:]
        phone_number = phonenumbers.parse(phone, 'RU')
        phone = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
        return phone

    def _birth_date(self, age: int, base_year: int) -> datetime.date:
        base_date: datetime.date = datetime.date(base_year, 1, 1)
        date: datetime.date = self.generator.date_object()
        year_diff: int = date.year - base_date.year
        date = date - datetime.timedelta(days=year_diff * 365) - datetime.timedelta(days=age * 365)
        return date

    def _age(self, age_min: int, age_max: int) -> int:
        p = math.exp(-self.generator.random.uniform(0, 5))
        # Map this probability linearly to the age range
        age: int = int(p * (age_max - age_min + 1) + age_min)
        # Return the age, ensuring it falls within the desired range
        return max(min(age, age_max), age_min)
