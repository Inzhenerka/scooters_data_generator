import pandas as pd
from src.faker_providers.person import PersonProvider, Person
from src.planner import Planner, Ride, DailyWeather
from src.data_manager import DataManager
from src.vis.statistics import date_histogram, hour_histogram


dm = DataManager()
# persons: list[Person] = dm.load_pickle('persons.pickle')
weather: list[DailyWeather] = dm.load_pickle('weather.pickle')
df = pd.DataFrame([w.model_dump() for w in weather])
dm.dump_parquet(data=df, file_name='weather.parquet')
dm.dump_text(data=df.to_json(
    orient='records', index=False, date_format='iso', indent=2
), file_name='weather.json')
