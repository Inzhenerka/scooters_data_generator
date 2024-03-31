from src.data_manager import DataManager
from src.city_utils import CityZone
from src.vis.plot_city import plot_city_zone, plot_city_graph


dm = DataManager()
cad_zone: CityZone = dm.load_pickle('city_zone.pickle')
file_path: str = dm.get_file_path('moscow_cad.html')
plot_city_zone(cad_zone, file_path)

file_path = dm.get_file_path('moscow_cad_graph.png')
plot_city_graph(cad_zone.graph, file_path)
