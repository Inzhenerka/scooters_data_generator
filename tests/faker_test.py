import pandas as pd
from faker import Faker
from shapely.geometry import Polygon
from src.faker_providers.location import LocationProvider
from src.faker_providers.person import PersonProvider, Person
from src.faker_providers.parking import ParkingProvider
from src.faker_providers.scooter import ScooterProvider, Scooter
from src.transport_mos import BicycleParking, SlowZone
from src.data_manager import DataManager
from src.city_utils import CityZone


dm = DataManager()
cad_zone = CityZone.model_validate(dm.load_pickle('cad_zone.pickle'))
cad_polygon: Polygon = cad_zone.polygon
bicycle_parking: list[BicycleParking] = cad_zone.parking
slow_zones: list[SlowZone] = cad_zone.slow_zones
models: pd.DataFrame = dm.load_csv('models.csv')

fake = Faker('ru_RU')
Faker.seed(0)
location_provider = LocationProvider(generator=fake, polygon=cad_polygon)
parking_provider = ParkingProvider(generator=fake, coordinates=[p.coordinates for p in bicycle_parking])
scooter_provider = ScooterProvider(generator=fake, hardware_ids=models['hardware_id'].tolist())

fake.add_provider(location_provider)
fake.add_provider(PersonProvider)
fake.add_provider(parking_provider)
fake.add_provider(scooter_provider)

for i in range(5):
    person: Person = fake.person()
    print(person)

for i in range(5):
    parking = fake.parking()
    print(parking)

for i in range(5):
    scooter: Scooter = fake.scooter()
    print(scooter)
