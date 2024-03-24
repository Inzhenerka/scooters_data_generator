from src.data_manager import DataManager
from src.city_utils import CityZone
from src.vis.plot_city_zone import plot_city_zone


dm = DataManager()
cad_zone = CityZone.model_validate(dm.load_pickle('cad_zone.pickle'))
plot_city_zone(cad_zone, 'moscow_cad.html')
