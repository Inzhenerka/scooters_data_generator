from logging import getLogger
from pydantic import BaseModel, ConfigDict
import networkx as nx
from networkx import MultiDiGraph
import osmnx as ox
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
import geopandas as gpd
from src.transport_mos import BicycleParking, SlowZone

logger = getLogger(__name__)


class ZoneParking(BaseModel):
    id: int
    name: str
    coordinates: tuple[float, float]
    graph_node: int
    closest_parking_id: list[int]


class CityZone(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    polygon: Polygon
    graph: MultiDiGraph
    parking: list[ZoneParking]
    slow_zones: list[SlowZone]


def prepare_city_zone(
        zone_polygon: Polygon,
        zone_graph: MultiDiGraph,
        bicycle_parking: list[BicycleParking],
        slow_zones: list[SlowZone]
) -> CityZone:
    logger.info('Preparing zero speed zone')
    zone_slow_zones = [sz for sz in slow_zones if zone_polygon.contains(Polygon(sz.coordinates[0], sz.coordinates[1:]))]
    zero_speed_polygon: Polygon = unary_union([
        Polygon(sz.coordinates[0], sz.coordinates[1:]) for sz in zone_slow_zones if sz.speed_limit == 0
    ])

    logger.info('Removing routes from zero speed zone')
    edges_to_remove: list[tuple[int, int, int]] = []
    nodes_to_remove: list[int] = []
    for u, v, key, data in zone_graph.edges(keys=True, data=True):
        u_pos = (zone_graph.nodes[u]['lat'], zone_graph.nodes[u]['lon'])  # or use 'lon', 'lat'
        v_pos = (zone_graph.nodes[v]['lat'], zone_graph.nodes[v]['lon'])
        edge_line = LineString([u_pos, v_pos])
        if zero_speed_polygon.intersects(edge_line):
            edges_to_remove.append((u, v, key))
            nodes_to_remove.extend([u, v])
    edges_to_remove = list(set(edges_to_remove))
    for u, v, key in edges_to_remove:
        zone_graph.remove_edge(u, v, key)
    isolated_nodes = list(nx.isolates(zone_graph))
    for node in isolated_nodes:
        zone_graph.remove_node(node)
    # Identify all weakly connected components
    subgraphs = list(nx.weakly_connected_components(zone_graph))
    # Find the largest subgraph
    largest_subgraph = max(subgraphs, key=len)
    # Remove nodes not in the largest subgraph
    all_nodes = list(zone_graph.nodes())
    nodes_to_remove = set(all_nodes) - set(largest_subgraph)
    for node in nodes_to_remove:
        zone_graph.remove_node(node)

    logger.info('Finding parking in the zone')
    parking: list[BicycleParking] = [
        p for p in bicycle_parking
        if zone_polygon.contains(Point(p.coordinates)) and not zero_speed_polygon.contains(Point(p.coordinates))
    ]

    logger.info('Finding closest graph node for every parking')
    zone_parking: list[ZoneParking] = []
    parking_id: int = 1
    for p in parking:
        logger.info(f'Finding node for parking [{parking_id}/{len(parking)}] {p.name} at {p.coordinates}')
        shapely_coordinates = gpd.GeoSeries(Point(p.coordinates[1], p.coordinates[0]), crs='epsg:4326')
        proj_point: gpd.GeoSeries = shapely_coordinates.to_crs(zone_graph.graph['crs'])
        node: int = ox.nearest_nodes(zone_graph, proj_point.x[0], proj_point.y[0])
        zone_parking.append(ZoneParking(
            id=parking_id,
            name=p.name,
            coordinates=p.coordinates,
            graph_node=node,
            closest_parking_id=[]
        ))
        parking_id += 1

    logger.info('Finding closest parking for every parking')
    for parking1 in zone_parking:
        node = parking1.graph_node
        closest_parking_id: list[int] = [p.id for p in zone_parking if p.graph_node == node and p.id != parking1.id]
        if len(closest_parking_id) < 3:
            successors: list[int] = list(set(zone_graph.successors(node)) | set(zone_graph.predecessors(node)))
            while len(closest_parking_id) < 3 and len(successors) > 0:
                node_id: int = successors.pop(0)
                closest_parking_id.extend([p.id for p in zone_parking if p.graph_node == node_id])
        parking1.closest_parking_id = list(set(closest_parking_id))

    city_zone = CityZone(
        polygon=zone_polygon,
        graph=zone_graph,
        parking=zone_parking,
        slow_zones=zone_slow_zones
    )
    return city_zone
