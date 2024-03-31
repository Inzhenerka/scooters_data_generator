import logging
from src.planner import SimulationPlan
from src.data_manager import DataManager
from src.city_utils import CityZone
from src.ride_simulator import RideSimulator, SimulationState

logging.basicConfig(level=logging.INFO)

dm = DataManager()
plan: SimulationPlan = dm.load_pickle('simulation_plan.pickle')
city_zone: CityZone = dm.load_pickle('city_zone.pickle')

rm = RideSimulator()
state: SimulationState = rm.simulate_rides(
    plan=plan,
    city_zone=city_zone,
    rides_limit=None
)
dm.dump_pickle(state, 'sim_state_3.pickle')
# rm.print_ride_details(state.rides)
print(len(state.ride_details))
print(max(*[len(p.scooters) for _, p in state.parking.items()]))
