import pickle
from src.transport_mos import TransportMos, SlowZone, BicycleParking

tm = TransportMos()
slow_zones: list[SlowZone] = tm.get_slow_zones()
bicycle_parking: list[BicycleParking] = tm.get_bicycle_parking()

with open('slow_zones.pickle', 'wb') as f:
    pickle.dump(slow_zones, f)
with open('bicycle_parking.pickle', 'wb') as f:
    pickle.dump(bicycle_parking, f)
