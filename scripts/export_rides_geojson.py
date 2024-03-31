from concurrent.futures import ProcessPoolExecutor, as_completed
import networkx as nx
from src.data_manager import DataManager
from src.ride_simulator import SimulationState, RideDetails
from src.city_utils import CityZone

TRIPS_MAX: int = 10000


def calculate_routes(batch: list[RideDetails], state: SimulationState, city_zone: CityZone) -> list:
    results = []
    for rd in batch:
        print(f'Processing ride: {rd.id}')
        start_node = state.parking[rd.start_parking_id].graph_node
        end_node = state.parking[rd.end_parking_id].graph_node
        route = nx.shortest_path(city_zone.graph, start_node, end_node, weight='length')
        person = state.persons[rd.person_id]
        results.append((route, person.speed_average))
    return results


def main():
    dm = DataManager()
    state: SimulationState = dm.load_pickle('sim_state_2.pickle')
    city_zone: CityZone = dm.load_pickle('city_zone.pickle')

    print(len(state.ride_details))

    routes_geojson: dict = {
        "type": "FeatureCollection",
        "features": []
    }
    futures = []
    num_processes = 8

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        batch_size = 500  # Adjust based on experimentation
        batches = [state.ride_details[i:i + batch_size] for i in range(1, TRIPS_MAX, batch_size)]

        for batch in batches:
            futures.append(executor.submit(calculate_routes, batch, state, city_zone))

        # Process results as they complete
        for future in as_completed(futures):
            batch_results = future.result()
            for route, speed_avg in batch_results:
                # Extract coordinates for the route
                coordinates = [(city_zone.graph.nodes[node]['lon'], city_zone.graph.nodes[node]['lat']) for node in
                               route]
                # Add route to GeoJSON
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coordinates
                    },
                    "properties": {
                        "speed_avg": speed_avg
                    }
                }
                routes_geojson["features"].append(feature)

    dm.dump_json(routes_geojson, 'routes.geojson')


if __name__ == '__main__':
    main()
