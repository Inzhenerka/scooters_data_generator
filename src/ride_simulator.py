import datetime
import logging
from simpy import Environment
import networkx as nx
from pydantic import BaseModel
from src.planner import SimulationPlan, Ride
from src.faker_providers.weather import WeatherCondition
from src.faker_providers.parking import Parking
from src.faker_providers.scooter import Scooter
from src.faker_providers.person import Person
from src.city_utils import CityZone


class RideDetails(BaseModel):
    id: int
    person_id: int
    scooter_id: int
    start_parking_id: int
    end_parking_id: int
    desired_start_datetime: datetime.datetime
    start_datetime: datetime.datetime
    end_datetime: datetime.datetime
    distance_m: float
    duration_s: int
    promo_code: bool
    find_available_time_s: int
    find_available_attempts: int


class RideRoute(BaseModel):
    ride_id: int
    points: list[tuple[float, float]]
    speed_avg: float


class CanceledRide(BaseModel):
    ride_id: int
    person_id: int
    start_parking_id: int
    start_datetime: datetime.datetime
    find_available_time_s: int
    find_available_attempts: int


class ParkingSearchResult(BaseModel):
    parking: Parking | None
    attempts: int
    duration_s: int


class SimulationState(BaseModel):
    start_datetime: datetime.datetime
    parking: dict[int, Parking]
    persons: dict[int, Person]
    scooters: dict[int, Scooter]
    ride_details: list[RideDetails] = []
    cancelled_rides: list[CanceledRide] = []


class RideSimulator:
    _env: Environment
    _state: SimulationState
    _logger: logging.Logger

    def __init__(self):
        self._logger = logging.getLogger(__class__.__name__)

    def simulate_rides(
            self,
            plan: SimulationPlan,
            city_zone: CityZone,
            rides_limit: int | None = None
    ) -> SimulationState:
        start_dt: datetime.datetime = datetime.datetime.combine(plan.start_date, datetime.datetime.min.time())
        all_scooters: list[Scooter] = []
        for p in plan.parking:
            all_scooters.extend(p.scooters)
        self._state = SimulationState(
            start_datetime=start_dt,
            parking={p.id: p for p in plan.parking},
            persons={p.id: p for p in plan.persons},
            scooters={s.id: s for s in all_scooters}
        )
        self._logger.info(f'Loaded {len(plan.parking)} parking, {len(plan.persons)} persons')
        self._env = Environment()
        # Start generating users with an initial number of users
        self._env.process(self._simulate_rides_process(plan, city_zone, rides_limit))
        simulation_time: int = int((plan.end_date - plan.start_date).total_seconds())
        self._env.run(until=simulation_time)
        return self._state

    def _simulate_rides_process(self, plan: SimulationPlan, city_zone: CityZone, rides_limit: int | None):
        while True:
            if len(plan.rides) == 0:
                break
            now: datetime.datetime = self._get_current_datetime()
            rides_to_start: list[Ride] = []
            r1: Ride = plan.rides[0]
            while now >= r1.datetime:
                rides_to_start.append(plan.rides.pop(0))
                if len(plan.rides) == 0:
                    break
                r1 = plan.rides[0]
            if rides_to_start:
                for ride in rides_to_start:
                    self._env.process(self._start_ride(now, ride, city_zone))
            if rides_limit is not None and len(self._state.ride_details) >= rides_limit:
                break
            yield self._env.timeout(1)

    def _get_current_datetime(self) -> datetime.datetime:
        return self._state.start_datetime + datetime.timedelta(seconds=self._env.now)

    def _start_ride(
            self,
            now: datetime.datetime,
            ride: Ride,
            city_zone: CityZone
    ):
        self._logger.info(
            f'[{len(self._state.ride_details)}] User {ride.person_id} is trying to start a ride {ride.id} at {ride.start_parking_id}'
        )
        desired_start_time: datetime.datetime = now
        person: Person = self._state.persons[ride.person_id]
        start_parking: Parking = self._state.parking[ride.start_parking_id]
        start_parking_search_result: ParkingSearchResult = yield self._env.process(
            self._find_parking_with_scooter(start_parking, person)
        )
        found_start_parking: Parking | None = start_parking_search_result.parking
        if found_start_parking is None or len(found_start_parking.scooters) <= 0:
            self._state.cancelled_rides.append(CanceledRide(
                ride_id=ride.id,
                person_id=ride.person_id,
                start_parking_id=ride.start_parking_id,
                start_datetime=desired_start_time,
                find_available_time_s=start_parking_search_result.duration_s,
                find_available_attempts=start_parking_search_result.attempts
            ))
            self._logger.error(f'  [X] Person {person.id} did not find scooter and cancels ride {ride.id}')
        else:
            self._logger.info(f'  -> Person {person.id} found a scooter at parking {found_start_parking.id}')
            scooter: Scooter = found_start_parking.scooters.pop(0)
            start_time: datetime.datetime = self._get_current_datetime()
            end_parking: Parking = self._state.parking[ride.end_parking_id]
            end_parking_search_result: ParkingSearchResult = self._find_parking_for_scooter(end_parking, person)
            end_parking = end_parking_search_result.parking
            distance_m: float = nx.shortest_path_length(
                city_zone.graph, found_start_parking.graph_node, end_parking.graph_node, weight='length'
            )
            duration_s: int = int(distance_m / (person.speed_average * 1000 / 3600))
            end_time: datetime.datetime = start_time + datetime.timedelta(seconds=duration_s)
            self._logger.info(f'Trip: {start_time} - {end_time}. {duration_s / 60} min, {distance_m / 1000} km')
            ride_details_id: int = len(self._state.ride_details) + 1
            use_promo_code: bool = person.promo_codes > 0
            if use_promo_code:
                self._logger.info(f'  -> Person {person.id} used promo code')
                person.promo_codes -= 1
            ride_details = RideDetails(
                id=ride_details_id,
                person_id=ride.person_id,
                scooter_id=scooter.id,
                start_parking_id=found_start_parking.id,
                end_parking_id=end_parking.id,
                desired_start_datetime=desired_start_time,
                start_datetime=start_time,
                end_datetime=end_time,
                distance_m=distance_m,
                duration_s=duration_s,
                promo_code=use_promo_code,
                find_available_time_s=start_parking_search_result.duration_s,
                find_available_attempts=start_parking_search_result.attempts,
            )
            self._state.ride_details.append(ride_details)
            yield self._env.timeout(duration_s)
            scooter.distance_m += distance_m
            end_parking.scooters.append(scooter)

    def _find_parking_with_scooter(self, start_parking: Parking, person: Person) -> ParkingSearchResult:
        closest_parking: list[Parking] = [self._state.parking[p] for p in start_parking.closest_parking_id]
        attempts: int = 0
        duration_s: int = 0
        parking: Parking | None = None
        while parking is None:
            if len(start_parking.scooters) > 0:
                parking = start_parking
            else:
                closest_parking.sort(key=lambda p: len(p.scooters), reverse=True)
                if len(closest_parking) > 0 and len(closest_parking[0].scooters) > 0:
                    parking = closest_parking[0]
                    attempts += 1
                else:
                    wait_time_s: int = 10
                    yield self._env.timeout(wait_time_s)
                    duration_s += wait_time_s
            if duration_s > person.find_available_time_limit_s:
                break
        if parking and parking.id != start_parking.id:
            self._logger.warning(f'  -> Person {person.id} is moving to parking {parking.id} to get a scooter')
        return ParkingSearchResult(
            parking=parking,
            attempts=attempts,
            duration_s=duration_s
        )

    def _find_parking_for_scooter(self, end_parking: Parking, person: Person) -> ParkingSearchResult:
        attempts: int = 0
        parking: Parking = end_parking
        if len(end_parking.scooters) > end_parking.max_capacity:
            closest_parking: list[Parking] = [self._state.parking[p] for p in end_parking.closest_parking_id]
            closest_parking.sort(key=lambda p: len(p.scooters))
            if len(closest_parking) > 0:
                parking = closest_parking[0]
                attempts += 1
                self._logger.warning(f'  -> Person {person.id} will ride to parking {parking.id}')
        return ParkingSearchResult(
            parking=parking,
            attempts=attempts,
            duration_s=0
        )

    @staticmethod
    # Example function to print ride details
    def print_ride_details(rides: list[RideDetails]):
        for details in rides:
            print(
                f"User {details.person_id}: Start at {details.start_parking_id} ({details.start_datetime}), "
                f"End at {details.end_parking_id} ({details.end_datetime}), "
                f"Duration: {details.duration_s / 60} min, Wait Time: {details.find_available_time_s}"
            )
