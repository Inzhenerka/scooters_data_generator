from pydantic import BaseModel, ConfigDict
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from src.transport_mos import BicycleParking, SlowZone


class CityZone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    polygon: Polygon
    parking: list[BicycleParking]
    slow_zones: list[SlowZone]


def make_city_zone(
        zone_polygon: Polygon,
        bicycle_parking: list[BicycleParking],
        slow_zones: list[SlowZone]
) -> CityZone:
    zone_slow_zones = [sz for sz in slow_zones if zone_polygon.contains(Polygon(sz.coordinates[0], sz.coordinates[1:]))]
    zero_speed_polygon: Polygon = unary_union([
        Polygon(sz.coordinates[0], sz.coordinates[1:]) for sz in zone_slow_zones if sz.speed_limit == 0
    ])

    zone_parking: list[BicycleParking] = [
        p for p in bicycle_parking
        if zone_polygon.contains(Point(p.coordinates)) and not zero_speed_polygon.contains(Point(p.coordinates))
    ]

    city_zone = CityZone(
        polygon=zone_polygon,
        parking=zone_parking,
        slow_zones=zone_slow_zones
    )
    return city_zone
