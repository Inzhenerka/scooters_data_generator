import osmnx as ox
from networkx import MultiDiGraph
from geopandas import GeoDataFrame
from shapely import Polygon
from shapely.ops import transform

ox.settings.use_cache = True
ox.settings.log_console = True


def get_region_graph(region: str) -> MultiDiGraph:
    return ox.graph_from_place(region, network_type='drive')


def get_region_polygon(region: str) -> Polygon:
    gdf: GeoDataFrame = ox.geocode_to_gdf(region)
    polygon: Polygon = gdf.loc[0, 'geometry']
    polygon = transform(lambda x, y: (y, x), polygon)
    return polygon
