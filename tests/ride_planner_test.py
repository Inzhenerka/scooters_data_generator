import datetime
from faker import Faker
from shapely.geometry import Polygon
from src.faker_providers.location import LocationProvider
from src.faker_providers.person import PersonProvider, Person
from src.faker_providers.weather import WeatherProvider, WeatherCondition
from src.faker_providers.datetime import DatetimeProvider
from src.ride_planner import RidePlanner
from src.data_manager import DataManager
from src.city_utils import CityZone
from src.vis.statistics import date_histogram, hour_histogram


dm = DataManager()
cad_zone = CityZone.model_validate(dm.load_pickle('cad_zone.pickle'))
cad_polygon: Polygon = cad_zone.polygon

fake = Faker('ru_RU')
Faker.seed(0)

location_provider = LocationProvider(generator=fake, polygon=cad_polygon)
fake.add_provider(location_provider)
fake.add_provider(PersonProvider)
fake.add_provider(WeatherProvider)
fake.add_provider(DatetimeProvider)

persons = [fake.person() for _ in range(100)]

rp = RidePlanner(persons=persons, fake=fake)
rides = rp.plan_rides(
    start_date=datetime.date(2023, 6, 1),
    end_date=datetime.date(2023, 8, 31)
)
print(rides)
print(len(rides))

date_histogram([ride.datetime for ride in rides])
hour_histogram([ride.datetime for ride in rides])
