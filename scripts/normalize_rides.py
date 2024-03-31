import datetime
from zoneinfo import ZoneInfo
import pandas as pd
from pydantic import BaseModel
from src.data_manager import DataManager
from src.ride_simulator import SimulationState




pd.options.display.width = 0
dm = DataManager()
state: SimulationState = dm.load_pickle('sim_state_2.pickle')

trips: list[Trip] = []
for r in state.ride_details:
    trip = Trip(
        id=r.id,
        user_id=r.person_id,
        scooter_hw_id=state.scooters[r.scooter_id].hardware_id,
        started_at=r.start_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow')),
        finished_at=r.end_datetime.replace(tzinfo=ZoneInfo('Europe/Moscow')),
        start_lat=state.parking[r.start_parking_id].coordinates[0],
        start_lon=state.parking[r.start_parking_id].coordinates[1],
        finish_lat=state.parking[r.end_parking_id].coordinates[0],
        finish_lon=state.parking[r.end_parking_id].coordinates[1],
        distance=r.distance_m
    )
    trips.append(trip)
trips_dict: list[dict] = [r.model_dump() for r in trips]
df = pd.DataFrame(trips_dict)
dm.dump_parquet(df, 'trips.parquet')
