import simpy
import random


class RideDetails:
    def __init__(self, user_id, start_parking, start_time, end_parking=None, end_time=None, wait_time_start=None,
                 wait_time_end=None):
        self.user_id = user_id
        self.start_parking = start_parking
        self.start_time = start_time
        self.end_parking = end_parking
        self.end_time = end_time
        self.duration = None  # To be calculated once the ride ends
        self.wait_time_start = wait_time_start
        self.wait_time_end = wait_time_end

    def calculate_duration(self):
        if self.end_time and self.start_time:
            self.duration = self.end_time - self.start_time


class ScooterParking:
    """Defines a scooter parking with a limited number of scooters."""

    def __init__(self, env, name, capacity, coordinates, initial_scooters):
        self.env = env
        self.name = name
        self.capacity = capacity
        self.scooters = simpy.Container(env, capacity, initial_scooters)
        self.coordinates = coordinates


ride_details_list = []  # Global list to store ride details


def try_start_ride(env, user_id, parking, city):
    """Attempts to start a ride, considering parking availability."""
    print(f'[{env.now}] User {user_id} is trying to start a ride at {parking.name}.')
    start_time = env.now
    ride_details = RideDetails(user_id, parking.name, start_time)
    ride_details.wait_time_start = env.now  # Record wait start time

    while True:
        if parking.scooters.level > 0:
            yield parking.scooters.get(1)  # Take one scooter
            print(f'[{env.now}] User {user_id} started a ride from {parking.name}.')
            ride_duration = random.randint(5, 45)  # Random ride duration
            yield env.timeout(ride_duration)  # Simulate riding time

            # Try to return the scooter
            if parking.scooters.level < parking.capacity:
                yield parking.scooters.put(1)  # Return the scooter
                print(f'[{env.now}] User {user_id} returned a scooter to {parking.name}. Ride: {ride_duration}')
                ride_details.wait_time_end = env.now  # Record wait end time
                ride_details.end_parking = parking.name  # Or new_parking.name if changed
                ride_details.end_time = env.now
                ride_details.calculate_duration()  # Calculate total ride duration
                ride_details_list.append(ride_details)
                break  # Successfully returned the scooter
            else:
                print(f'[{env.now}] Parking {parking.name} is full. User {user_id} is waiting.')
                yield env.timeout(10)  # Wait for 10 minutes
                # Choose another parking to return the scooter
                new_parking = random.choice([p for p in city if p != parking])
                print(f'[{env.now}] User {user_id} is moving to {new_parking.name} to return the scooter.')
                parking = new_parking  # Change the target parking
        else:
            if env.now - start_time > 10:  # Wait no more than 10 minutes
                print(f'[{env.now}] User {user_id} could not find a scooter at {parking.name} and leaves.')
                break  # Exit the simulation for this user
            else:
                yield env.timeout(1)  # Check again in 1 minute


def generate_users(env, city, initial_users, interval=1):
    """Generates an initial number of users and additional users at a specified interval."""
    # Immediately generate the initial users
    for user_id in range(1, initial_users + 1):
        selected_parking = random.choice(city)  # Randomly select a parking
        env.process(try_start_ride(env, user_id, selected_parking, city))

    # Continuously generate new users
    user_id = initial_users + 1
    while True:
        selected_parking = random.choice(city)  # Randomly select a parking
        env.process(try_start_ride(env, user_id, selected_parking, city))
        user_id += 1
        yield env.timeout(interval)  # Wait before generating the next user


# Example function to print ride details
def print_ride_details(ride_details_list):
    for details in ride_details_list:
        print(f"User {details.user_id}: Start at {details.start_parking} ({details.start_time}), "
              f"End at {details.end_parking} ({details.end_time}), "
              f"Duration: {details.duration}, Wait Time: {details.wait_time_end - details.wait_time_start}")


# Initialize simulation environment
env = simpy.Environment()

# Create a list of scooter parkings
city = [
    ScooterParking(env, 'Parking A', 10, (0, 0), 10),
    ScooterParking(env, 'Parking B', 10, (1, 1), 10),
    ScooterParking(env, 'Parking C', 10, (2, 2), 8),
]

INITIAL_USERS = 150  # Specify the initial number of users

# Start generating users with an initial number of users
env.process(generate_users(env, city, INITIAL_USERS, interval=1))

# Run the simulation for a specified amount of time
simulation_time = 120  # minutes
env.run(until=simulation_time)
# Call this function after the simulation
print_ride_details(ride_details_list)
print(len(ride_details_list))
