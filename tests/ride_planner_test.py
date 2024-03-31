from src.faker_providers.person import PersonProvider, Person
from src.planner import Planner, Ride, DailyWeather
from src.data_manager import DataManager
from src.vis.statistics import date_histogram, hour_histogram


dm = DataManager()
persons: list[Person] = dm.load_pickle('persons.pickle')
weather: list[DailyWeather] = dm.load_pickle('weather.pickle')
rides: list[Ride] = dm.load_pickle('rides.pickle')

date_histogram([ride.datetime for ride in rides])
hour_histogram([ride.datetime for ride in rides])
