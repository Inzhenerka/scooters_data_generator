from src.data_manager import DataManager
from src.geo_utils import get_region_graph, get_region_polygon
from networkx import MultiDiGraph
from shapely import Polygon

REGION: str = 'ЦАО, Москва, Россия'

dm = DataManager()

region_graph: MultiDiGraph = get_region_graph(REGION)
dm.dump_pickle(region_graph, 'cad_graph.pickle')

region_polygon: Polygon = get_region_polygon(REGION)
dm.dump_pickle(region_polygon, 'cad_polygon.pickle')
