import networkx as nx
from src.data_manager import DataManager
from src.ride_simulator import SimulationState, RideDetails
from src.city_utils import CityZone

dm = DataManager()
state: SimulationState = dm.load_pickle('sim_state_2.pickle')
parking = sorted(state.parking.values(), key=lambda x: len(x.scooters), reverse=False)
for p in parking:
    print(f'Parking {p.id} has {len(p.scooters)} scooters')
