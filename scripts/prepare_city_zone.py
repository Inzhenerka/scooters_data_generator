import logging
from shapely.geometry import Polygon, Point
from networkx import MultiDiGraph
from src.transport_mos import BicycleParking, SlowZone
from src.data_manager import DataManager
from src.city_utils import CityZone, prepare_city_zone

logging.basicConfig(level=logging.INFO)

dm = DataManager()
city_polygon: Polygon = dm.load_pickle('cad_polygon.pickle')
city_graph: MultiDiGraph = dm.load_pickle('cad_graph.pickle')
bicycle_parking: list[BicycleParking] = dm.load_pickle('bicycle_parking.pickle')
slow_zones: list[SlowZone] = dm.load_pickle('slow_zones.pickle')

city_zone: CityZone = prepare_city_zone(
    zone_polygon=city_polygon,
    zone_graph=city_graph,
    bicycle_parking=bicycle_parking,
    slow_zones=slow_zones
)

dm.dump_pickle(city_zone, 'city_zone.pickle')
