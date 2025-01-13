from collections import Counter
import networkx as nx
from src.data_manager import DataManager
from src.ride_simulator import SimulationState, RideDetails, Scooter
from src.planner import SimulationPlan
from src.city_utils import CityZone

dm = DataManager()
plan: SimulationPlan = dm.load_pickle('simulation_plan.pickle')
state: SimulationState = dm.load_pickle('sim_state_3.pickle')
scooters: list[Scooter] = []
models: list[str] = []
for p in plan.parking:
    scooters.extend(p.scooters)
    models.extend([s.hardware_id for s in p.scooters])
c = Counter(models)
print(f'Scooters: {len(scooters)}')
parking = sorted(state.parking.values(), key=lambda x: len(x.scooters), reverse=False)
for p in parking:
    print(f'Parking {p.id} has {len(p.scooters)} scooters')
