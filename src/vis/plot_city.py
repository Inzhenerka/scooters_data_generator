import folium
from networkx import MultiDiGraph
import osmnx as ox
from folium.plugins import MarkerCluster
from src.transport_mos import SlowZone
from shapely.geometry import Point, Polygon
from src.city_utils import CityZone, ZoneParking


def _speed_to_color(speed: int, min_speed: int, max_speed: int):
    speed = max(min(speed, max_speed), min_speed)
    ratio = (speed - min_speed) / (max_speed - min_speed)
    red = int((1 - ratio) * 255)
    green = int(ratio * 255)
    blue = 0  # Keeping blue constant as 0
    return f'#{red:02x}{green:02x}{blue:02x}'


def get_city_center(city_zone: CityZone) -> Point:
    return city_zone.polygon.centroid


def plot_city_zone(city_zone: CityZone, file: str = 'city_zone.html'):
    slow_zones: list[SlowZone] = city_zone.slow_zones
    zone_polygon: Polygon = city_zone.polygon
    parking: list[ZoneParking] = city_zone.parking

    print('Parking', len(parking))
    print('Slow zones', len(slow_zones))

    fm = folium.Map(location=zone_polygon.centroid.coords[0], zoom_start=12)

    folium.Polygon(
        locations=list(zone_polygon.exterior.coords), color='blue', fill=True, fill_color='cyan'
    ).add_to(fm)

    speeds: list[int] = [slow_zone.speed_limit for slow_zone in slow_zones]
    for slow_zone in slow_zones:
        color: str = _speed_to_color(slow_zone.speed_limit, min(speeds), max(speeds))
        folium.Polygon(
            slow_zone.coordinates, color=color, fill=True, fill_color=color, popup=str(slow_zone.speed_limit) + ' km/h'
        ).add_to(fm)

    parking_cluster = MarkerCluster().add_to(fm)
    for p in parking:
        folium.Marker(p.coordinates, popup=p.name).add_to(parking_cluster)

    fm.save(file)


def plot_city_graph(city_graph: MultiDiGraph, file: str = 'city_graph.png'):
    fig, ax = ox.plot_graph(city_graph, show=False, close=False)
    fig.savefig(file, dpi=300)
