from typing import Any, Literal
import requests
from pydantic import BaseModel


class ParkingGeometry(BaseModel):
    type: Literal['Point']
    coordinates: tuple[float, float]


class ParkingProperties(BaseModel):
    hintContent: str
    balloonContentHeader: str
    vote: list
    ratingColor: str
    ratingOffsetTop: str
    ratingOffsetLeft: str
    ratingHeight: str
    rating: float
    type: None


class BicycleParkingFeature(BaseModel):
    id: int
    type: Literal['Feature']
    geometry: ParkingGeometry
    properties: ParkingProperties


class BicycleParkingDataset(BaseModel):
    type: Literal['FeatureCollection']
    collectionName: Literal['BicycleParking']
    needClusterized: bool
    features: list[BicycleParkingFeature]
    commonOptions: dict[str, Any]


class SlowZonesGeometry(BaseModel):
    type: Literal['Polygon']
    coordinates: list[list[tuple[float, float]]]


class SlowZonesProperties(BaseModel):
    speed_limit: int


class SlowZonesFeature(BaseModel):
    id: int
    type: Literal['Feature']
    properties: SlowZonesProperties
    geometry: SlowZonesGeometry
    options: dict


class SlowZonesDataset(BaseModel):
    type: Literal['FeatureCollection']
    features: list[SlowZonesFeature]


class BicycleParking(BaseModel):
    name: str
    geometry_type: Literal['Point']
    coordinates: tuple[float, float]


class SlowZone(BaseModel):
    id: int
    speed_limit: int
    geometry_type: Literal['Polygon']
    coordinates: list[list[tuple[float, float]]]


class TransportMos:
    _BICYCLE_PARKING_URL: str = 'https://transport.mos.ru/ru/map/get?action=get_coords&type=bicycle_parking'
    _SLOW_ZONES_URL: str = 'https://transport.mos.ru/map/getSlowZones'
    _TIMEOUT: int = 10
    _HEADERS: dict = {
        'User-Agent': 'Chrome/102.0.0.0 Safari/537.36'
    }

    def get_bicycle_parking(self) -> list[BicycleParking]:
        res = requests.get(self._BICYCLE_PARKING_URL, headers=self._HEADERS, timeout=self._TIMEOUT)
        data_raw: dict = res.json()
        data = BicycleParkingDataset.model_validate(data_raw)
        parking: list[BicycleParking] = [BicycleParking(
            name=f.properties.hintContent,
            geometry_type=f.geometry.type,
            coordinates=(f.geometry.coordinates[1], f.geometry.coordinates[0])
        ) for f in data.features]
        return parking

    def get_slow_zones(self):
        res = requests.get(self._SLOW_ZONES_URL, headers=self._HEADERS, timeout=self._TIMEOUT)
        data_raw: dict = res.json()
        data = SlowZonesDataset.model_validate(data_raw)
        zones: list[SlowZone] = [SlowZone(
            id=f.id,
            speed_limit=f.properties.speed_limit,
            geometry_type=f.geometry.type,
            coordinates=f.geometry.coordinates
        ) for f in data.features]
        return zones
