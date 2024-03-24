import random
import os
import osmnx as ox
import numpy as np
import networkx as nx
import folium
import pickle

ox.settings.use_cache = True
ox.settings.log_console = True

if os.path.isfile('graph.pickle'):
    moscow_graph = pickle.load(open('graph.pickle', 'rb'))
else:
    moscow_graph = ox.graph_from_place('Moscow, Russia', network_type='drive')
    print('MOSCOW MAP CREATED')
    pickle.dump(moscow_graph, open('graph.pickle', 'wb'))
    # ox.plot_graph(moscow_graph)

# Define the center of Moscow and a 2km radius for the city center
center_point = (55.7522, 37.6156)
distance = 5000  # 2km in meters
# Create a graph from OSM within the 2km radius around the center point
G = ox.graph_from_point(center_point, dist=distance, network_type='drive')
print('GRAPH CREATED')
# Get a list of nodes in the graph
nodes = list(G.nodes)
# Select two random nodes from the list for start and end points
start_node = np.random.choice(nodes)
end_node = np.random.choice(nodes)
# Ensure the end_node is different from the start_node
while end_node == start_node:
    end_node = np.random.choice(nodes)
# Print the selected nodes
print(f"Start Node: {start_node}")
print(f"End Node: {end_node}")
route = nx.shortest_path(moscow_graph, start_node, end_node, weight='length')

route_map = folium.Map(location=center_point, zoom_start=12)  # Center map on Moscow
ox.plot_route_folium(moscow_graph, route, route_map)
route_map.save('moscow_scooter_trip.html')
# Calculate the length of the route in meters
route_length = sum(ox.utils_graph.get_route_edge_attributes(G, route, 'length'))
print(f"Total route length: {route_length} meters")
