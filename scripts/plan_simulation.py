import datetime
from faker import Faker
import pandas as pd
from src.faker_providers.location import LocationProvider
from src.faker_providers.person import PersonProvider
from src.faker_providers.weather import WeatherProvider
from src.faker_providers.datetime import DatetimeProvider
from src.faker_providers.parking import ParkingProvider
from src.faker_providers.scooter import ScooterProvider
from src.planner import Planner, SimulationPlan
from src.data_manager import DataManager
from src.city_utils import CityZone

dm = DataManager()
models: pd.DataFrame = dm.load_csv('models.csv')
city_zone: CityZone = dm.load_pickle('city_zone.pickle')

fake = Faker('ru_RU')
Faker.seed(0)

location_provider = LocationProvider(generator=fake, city_graph=city_zone.graph)
parking_provider = ParkingProvider(generator=fake, zone_parking=city_zone.parking)
scooter_provider = ScooterProvider(generator=fake, hardware_ids=models['hardware_id'].tolist())
fake.add_provider(location_provider)
fake.add_provider(PersonProvider)
fake.add_provider(WeatherProvider)
fake.add_provider(DatetimeProvider)
fake.add_provider(parking_provider)
fake.add_provider(scooter_provider)

planner = Planner(fake=fake)

simulation_plan: SimulationPlan = planner.plan_simulation(
    start_date=datetime.date(2023, 6, 1),
    end_date=datetime.date(2023, 8, 31),
    persons_count=2000,
    max_parking_capacity=15
)

print(f'Persons: {len(simulation_plan.persons)}')
print(f'Weather: {len(simulation_plan.weather)}')
print(f'Rides: {len(simulation_plan.rides)}')
print(f'Parking: {len(simulation_plan.parking)}')
print(f'Scooters: {sum([len(p.scooters) for p in simulation_plan.parking])}')

dm.dump_pickle(simulation_plan, 'simulation_plan.pickle')
