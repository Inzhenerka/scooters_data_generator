from faker.providers import BaseProvider
from pydantic import BaseModel
from networkx import MultiDiGraph


class Location(BaseModel):
    coordinates: tuple[float, float]


class LocationProvider(BaseProvider):

    def __init__(self, generator, city_graph: MultiDiGraph):
        super().__init__(generator)
        self._city_graph: MultiDiGraph = city_graph

    def location_node(self) -> int:
        nodes: list[int] = list(self._city_graph.nodes)
        return self.random_element(nodes)
