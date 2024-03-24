from src.transport_mos import TransportMos, SlowZone, BicycleParking
from src.data_manager import DataManager

tm = TransportMos()
dm = DataManager()

slow_zones: list[SlowZone] = tm.get_slow_zones()
dm.dump_pickle(slow_zones, 'slow_zones.pickle')

bicycle_parking: list[BicycleParking] = tm.get_bicycle_parking()
dm.dump_pickle(bicycle_parking, 'bicycle_parking.pickle')
