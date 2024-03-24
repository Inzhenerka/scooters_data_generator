from pydantic import BaseModel, ConfigDict
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from src.transport_mos import BicycleParking, SlowZone
from src.data_manager import DataManager
from src.city_utils import CityZone, make_city_zone


dm = DataManager()
cad_polygon: Polygon = dm.load_pickle('cad_polygon.pickle')
bicycle_parking: list[BicycleParking] = dm.load_pickle('bicycle_parking.pickle')
slow_zones: list[SlowZone] = dm.load_pickle('slow_zones.pickle')

cad_zone: CityZone = make_city_zone(
    zone_polygon=cad_polygon,
    bicycle_parking=bicycle_parking,
    slow_zones=slow_zones
)

dm.dump_pickle(cad_zone.model_dump(), 'cad_zone.pickle')
