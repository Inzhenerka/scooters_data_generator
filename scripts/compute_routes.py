import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import networkx as nx
from pydantic import BaseModel
from src.data_manager import DataManager
from src.ride_simulator import SimulationState, RideDetails, RideRoute
from src.city_utils import CityZone

TRIPS_MAX: int = 1000000
BATCH_SIZE: int = 350
num_processes = 1
start_date = datetime.date(2023, 8, 7)
end_date = datetime.date(2023, 8, 7)


def calculate_routes(batch: list[RideDetails], state: SimulationState, city_zone: CityZone) -> list:
    results = []
    for rd in batch:
        print(f'Processing ride: {rd.id}')
        start_node = state.parking[rd.start_parking_id].graph_node
        end_node = state.parking[rd.end_parking_id].graph_node
        route = nx.shortest_path(city_zone.graph, start_node, end_node, weight='length')
        person = state.persons[rd.person_id]
        results.append((route, person.speed_average, rd.id))
    return results


def main():
    dm = DataManager()
    state: SimulationState = dm.load_pickle('sim_state_3.pickle')
    city_zone: CityZone = dm.load_pickle('city_zone.pickle')

    routes_geojson: dict = {
        "type": "FeatureCollection",
        "features": []
    }
    futures = []
    routes: list[RideRoute] = []

    ride_details: list[RideDetails] = state.ride_details
    ride_details = [
        ride for ride in ride_details
        if start_date <= ride.start_datetime.date() <= end_date
    ]
    print(len(ride_details))

    # with ProcessPoolExecutor(max_workers=num_processes) as executor:
    #     batches = [ride_details[i:i + BATCH_SIZE] for i in range(1, TRIPS_MAX, BATCH_SIZE)]
    #
    #     for batch in batches:
    #         futures.append(executor.submit(calculate_routes, batch, state, city_zone))
    #
    #     # Process results as they complete
    #     for future in as_completed(futures):
    #         batch_results = future.result()
    #         for route, speed_avg, ride_id in batch_results:
    #             # Extract coordinates for the route
    #             coordinates = [
    #                 (city_zone.graph.nodes[node]['lon'], city_zone.graph.nodes[node]['lat']) for node in route
    #             ]
    #             # Add route to GeoJSON
    #             feature = {
    #                 "type": "Feature",
    #                 "geometry": {
    #                     "type": "LineString",
    #                     "coordinates": coordinates
    #                 },
    #                 "properties": {
    #                     "speed_avg": speed_avg
    #                 }
    #             }
    #             routes_geojson["features"].append(feature)
    #             routes.append(RideRoute(
    #                 ride_id=ride_id,
    #                 points=coordinates,
    #                 speed_avg=speed_avg
    #             ))
    for route, speed_avg, ride_id in calculate_routes(ride_details, state, city_zone):
        coordinates = [
            (city_zone.graph.nodes[node]['lon'], city_zone.graph.nodes[node]['lat']) for node in route
        ]
        routes.append(RideRoute(
            ride_id=ride_id,
            points=coordinates,
            speed_avg=speed_avg
        ))
    print('Routes calculated')
    # dm.dump_json(routes_geojson, 'routes.geojson')
    dm.dump_pickle(routes, 'routes.pickle')


if __name__ == '__main__':
    main()
