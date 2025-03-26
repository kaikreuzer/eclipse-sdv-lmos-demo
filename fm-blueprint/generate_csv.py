import csv
import random
import math
import argparse

class VehicleState:
    def __init__(self):
        # Initialisierung mit Standardwerten
        self.working_state_driver1 = random.choice(["REST", "DRIVE", "WORK"])
        self.working_state_driver2 = random.choice(["REST", "DRIVER_AVAILABLE"])
        self.is_card_present_driver1 = random.choice([True, False])
        self.is_card_present_driver2 = random.choice([True, False])
        
        # Set initial driving state - 90% chance to start driving
        self.is_driving_period = random.random() < 0.9
        
        # Fahrzyklus-Management - much shorter driving periods, more frequent rests
        self.driving_cycle_counter = 0
        self.driving_duration = random.randint(20, 45)  # Even shorter driving duration (was 40-70)
        self.rest_duration = random.randint(8, 30)      # More variable rest duration
        
        # Basic vehicle data
        # Independent 50% chance for each resource to be low
        low_fuel = random.random() < 0.5  # Direct 50% chance fuel is low
        low_adblue = random.random() < 0.5  # Direct 50% chance AdBlue is low
            
        # Set levels based on what's low
        self.fuel_level = random.uniform(5, 20) if low_fuel else random.uniform(50, 100)
        self.adblue_level = random.uniform(5, 20) if low_adblue else random.uniform(70, 100)
            
        self.traveled_distance = random.randint(54000000, 55000000)
        self.air_temperature = random.uniform(10, 25)
        self.engine_hours = random.uniform(0, 2000)
        self.parking_brake_engaged = not self.is_driving_period
        self.current_weight = random.uniform(1000, 5000)
        
        # SIMPLIFIED APPROACH: Use smooth curve functions for speeds 
        # Initialize time counters
        self.time_counter = 0
        
        # Replace continuous sine waves with more stable speed patterns
        if self.is_driving_period:
            # Initial cruise speed with minimal variation
            self.target_speed = random.uniform(60, 85)
            self.current_speed = self.target_speed
            self.vehicle_speed = self.current_speed
            self.engine_speed = 800 + self.vehicle_speed * 15
            
            # Counters for cruise control behavior
            self.cruise_duration = random.randint(10, 30)  # Shorter periods of constant speed
            self.cruise_counter = 0
            self.transition_duration = 0
            self.transition_counter = 0
            self.in_transition = False
            
            self.working_state_driver1 = "DRIVE"
        else:
            self.base_speed = 0
            self.speed_variation = 0
            self.speed_period = 50
            self.speed_phase = 0
            self.vehicle_speed = 0
            self.engine_speed = 0 if random.random() < 0.7 else 800  # 70% chance engine is off when parked
            self.working_state_driver1 = "REST"
        
        # Initialize GPS coordinates in Central Europe (around Germany/Austria/Czech area)
        # Central European coordinates range roughly:
        # Latitude: 48.0 to 52.0 (North)
        # Longitude: 8.0 to 16.0 (East)
        self.latitude = random.uniform(48.0, 52.0)
        self.longitude = random.uniform(8.0, 16.0)
        
        # Vehicle heading (0-359 degrees, 0=North, 90=East, etc.)
        self.heading = random.uniform(0, 359)
        
        # Set initial GPS update counter
        self.gps_update_counter = 0
        
        # Central European cities to make simulation more realistic
        self.cities = [
            {"name": "Munich", "lat": 48.137154, "lng": 11.576124},
            {"name": "Berlin", "lat": 52.520008, "lng": 13.404954},
            {"name": "Vienna", "lat": 48.208176, "lng": 16.373819},
            {"name": "Prague", "lat": 50.073658, "lng": 14.418540},
            {"name": "Warsaw", "lat": 52.229676, "lng": 21.012229},
            {"name": "Frankfurt", "lat": 50.110924, "lng": 8.682127},
            {"name": "Zurich", "lat": 47.376888, "lng": 8.541694}
        ]
        
        # Randomly pick a starting city and adjust coordinates
        if random.random() < 0.7:  # 70% chance to start in a city
            city = random.choice(self.cities)
            self.latitude = city["lat"] + random.uniform(-0.01, 0.01)  # Small variation
            self.longitude = city["lng"] + random.uniform(-0.01, 0.01)
        
        # Driver rest cycle tracking - much more aggressive now
        self.driver1_active_cycles = 0
        self.driver2_active_cycles = 0
        self.driver1_rest_cycles = 0
        self.driver2_rest_cycles = 0
        
        # Constants for driver breaks - much more frequent breaks
        self.DRIVE_DURATION_BEFORE_BREAK = 60  # ~1 minute drive time before requiring break
        self.DRIVER_BREAK_DURATION = 30       # ~30 second minimum rest duration
        
        # Driver states (can be REST independent of vehicle state)
        self.driver1_needs_break = False
        self.driver2_needs_break = False
        
        # Track when breaks were last enforced
        self.last_driver1_break = 0
        self.last_driver2_break = 0
        self.cycle_count = 0
    
    def update(self):
        # Track total cycles for break timing
        self.cycle_count += 1
        
        # SIMPLIFIED: Check for phase changes first
        self.driving_cycle_counter += 1
        
        # State transitions
        if self.is_driving_period:
            if self.driving_cycle_counter >= self.driving_duration:
                # Transition to rest
                self.is_driving_period = False
                self.driving_cycle_counter = 0
                self.rest_duration = random.randint(10, 30)  # Longer rest
                self.working_state_driver1 = "REST"
                self.working_state_driver2 = "REST"
                # Start slowing down
                self.speed_period = random.uniform(10, 20)  # Faster deceleration
            
            # Random chance for unplanned rest break - significantly increased
            elif random.random() < 0.04:  # 4% chance per cycle (was 1.5%)
                self.is_driving_period = False
                self.driving_cycle_counter = 0
                self.rest_duration = random.randint(5, 20)  # Variable unplanned stops
                self.working_state_driver1 = "REST"
                self.working_state_driver2 = "REST"
                
            # Additional rest triggers based on conditions
            elif self.fuel_level < 15 and random.random() < 0.1:  # Low fuel may trigger rest
                self.is_driving_period = False
                self.driving_cycle_counter = 0
                self.rest_duration = random.randint(15, 25)  # Longer rest for refueling
                self.working_state_driver1 = "REST"
                self.working_state_driver2 = "REST"
                
            # Driver fatigue simulation - longer driving leads to higher rest probability
            elif self.driving_cycle_counter > 15 and random.random() < 0.02:
                self.is_driving_period = False
                self.driving_cycle_counter = 0
                self.rest_duration = random.randint(5, 15)  # Short rest for driver break
                self.working_state_driver1 = "REST"
                self.working_state_driver2 = "REST"
        else:
            if self.driving_cycle_counter >= self.rest_duration:
                # Transition to driving
                self.is_driving_period = True
                self.driving_cycle_counter = 0
                self.driving_duration = random.randint(20, 45)  # Even shorter driving periods (was 40-70)
                self.working_state_driver1 = "DRIVE"
                self.working_state_driver2 = "AVAILABLE"
                
                # Set up a new speed profile
                self.base_speed = random.uniform(60, 85)
                self.speed_variation = random.uniform(5, 15)
                self.speed_period = random.uniform(30, 60)
                self.speed_phase = random.uniform(0, 2*math.pi)
        
        # SIMPLIFIED: 5% chance to start driving immediately if at rest
        if not self.is_driving_period and random.random() < 0.05:
            self.is_driving_period = True
            self.driving_cycle_counter = 0
            self.driving_duration = random.randint(40, 70)  # Shorter driving periods
            self.working_state_driver1 = "DRIVE"
            self.working_state_driver2 = "AVAILABLE"
            
            # Start with a new speed profile
            self.base_speed = random.uniform(60, 85)
            self.speed_variation = random.uniform(5, 15)
            self.speed_period = random.uniform(30, 60)
            self.speed_phase = random.uniform(0, 2*math.pi)
        
        # Speed pattern simulation with periods of constant speed
        if self.is_driving_period:
            if not self.in_transition:
                # Currently cruising at stable speed
                self.cruise_counter += 1
                
                # Add tiny variations to simulate real-world minor fluctuations
                small_adjustment = random.uniform(-0.3, 0.3)
                self.vehicle_speed = max(0, min(100, self.current_speed + small_adjustment))
                
                # Random chance for spontaneous speed change
                if random.random() < 0.05:  # 5% chance per cycle for spontaneous speed change
                    self.in_transition = True
                    self.transition_counter = 0
                    
                    # Quick speed adjustment (like traffic conditions, other vehicles)
                    change_amount = random.uniform(5, 15)
                    direction = 1 if random.random() < 0.5 else -1
                    self.target_speed = self.current_speed + (direction * change_amount)
                    # Keep within reasonable bounds
                    self.target_speed = max(40, min(95, self.target_speed))
                    
                    # Calculate how long the transition should take
                    speed_diff = abs(self.target_speed - self.current_speed)
                    self.transition_duration = int(1 + speed_diff / 3)  # Faster transitions
                
                # Decide if it's time to change speed
                elif self.cruise_counter >= self.cruise_duration:
                    self.in_transition = True
                    self.transition_counter = 0
                    
                    # Decide new target speed
                    prev_target = self.target_speed
                    
                    # Sometimes make larger changes (like highway exit, overtaking)
                    if random.random() < 0.4:  # 40% chance of significant speed change
                        change_amount = random.uniform(15, 25)
                        direction = 1 if random.random() < 0.5 else -1
                        self.target_speed = prev_target + (direction * change_amount)
                        # Keep within reasonable bounds
                        self.target_speed = max(40, min(95, self.target_speed))
                    else:
                        # Small adjustments to current speed
                        self.target_speed = prev_target + random.uniform(-10, 10)
                        # Keep within reasonable bounds
                        self.target_speed = max(40, min(95, self.target_speed))
                        
                    # Calculate how long the transition should take
                    speed_diff = abs(self.target_speed - self.current_speed)
                    self.transition_duration = int(1 + speed_diff / 2)  # 1 cycle per 2 km/h change
            else:
                # Currently in speed transition
                self.transition_counter += 1
                
                # Calculate smooth progression to target speed
                progress = min(1.0, self.transition_counter / self.transition_duration)
                self.current_speed = self.current_speed + ((self.target_speed - self.current_speed) * progress * 0.2)
                
                # Small random variations during transition
                small_adjustment = random.uniform(-0.2, 0.2)
                self.vehicle_speed = max(0, min(100, self.current_speed + small_adjustment))
                
                # Check if transition is complete
                if self.transition_counter >= self.transition_duration:
                    self.in_transition = False
                    self.cruise_counter = 0
                    self.current_speed = self.target_speed
                    self.cruise_duration = random.randint(10, 30)  # Set next cruise duration
            
            # Engine speed follows vehicle speed without feedback loops
            target_rpm = 800 + self.vehicle_speed * 15
            self.engine_speed = target_rpm + random.uniform(-20, 20)  # Small variation in RPM
            
            # Always in DRIVE state when moving with speed >5
            self.working_state_driver1 = "DRIVE" if self.vehicle_speed > 5 else "WORK"
            self.parking_brake_engaged = False
        else:
            # When resting, smoothly decelerate
            if self.vehicle_speed > 0:
                # Decelerate gradually
                self.vehicle_speed = max(0, self.vehicle_speed - 2)
                
                # Engine speed follows accordingly
                self.engine_speed = 800 + self.vehicle_speed * 15
                
                # Still driving until fully stopped
                if self.vehicle_speed > 5:
                    self.working_state_driver1 = "DRIVE"
                else:
                    self.working_state_driver1 = "WORK"
            else:
                # Fully stopped
                self.vehicle_speed = 0
                
                # Either idle or engine off
                if self.engine_speed > 0:
                    # Engine running - either keep idling or turn off
                    if random.random() < 0.1:  # 10% chance to turn off engine per cycle
                        self.engine_speed = max(0, self.engine_speed - 200)
                    else:
                        # Idle fluctuations
                        self.engine_speed = 800 + random.uniform(-20, 20)
                
                self.working_state_driver1 = "REST"
                self.parking_brake_engaged = True
        
        # Adjust fuel consumption (simpler, based directly on current speed)
        if self.engine_speed > 0:
            # Higher consumption at higher speed
            base_consumption = 0.01 + (self.vehicle_speed / 1000)
            self.fuel_level = max(0, self.fuel_level - base_consumption)
            
            # AdBlue consumption (slower than fuel)
            self.adblue_level = max(0, self.adblue_level - base_consumption * 0.7)
        
        # Update distance
        if self.vehicle_speed > 0:
            self.traveled_distance += round(self.vehicle_speed / 3.6)  # km/h to m/s
        
        # Update engine hours
        if self.engine_speed > 0:
            self.engine_hours += 1/3600
        
        # Very small temperature change
        self.air_temperature += random.uniform(-0.1, 0.1)
        self.air_temperature = max(-20, min(40, self.air_temperature))
        
        # Rare weight changes
        if random.random() < 0.01:
            self.current_weight += random.uniform(-30, 30)
            self.current_weight = max(1000, min(5000, self.current_weight))
        
        # Driver card changes
        if random.random() < 0.01:
            self.is_card_present_driver1 = not self.is_card_present_driver1
            
        if random.random() < 0.01:
            self.is_card_present_driver2 = not self.is_card_present_driver2
        
        # Update GPS position when vehicle is moving
        if self.vehicle_speed > 0:
            # Update GPS position every second based on speed
            
            # 1. Occasionally change heading for more realistic path
            if random.random() < 0.05:  # 5% chance to change direction slightly
                self.heading = (self.heading + random.uniform(-20, 20)) % 360
            
            # 2. Calculate distance traveled in this update
            # Speed is km/h, convert to meters per update cycle (assuming ~1 sec per update)
            distance_meters = self.vehicle_speed / 3.6
            
            # 3. Convert heading and distance to lat/lng changes
            # At these latitudes, 1 degree ~= 111km
            lat_change = distance_meters / 111000 * math.cos(math.radians(self.heading))
            # Longitude degrees get shorter as we move north
            lng_factor = math.cos(math.radians(self.latitude))
            lng_change = distance_meters / (111000 * lng_factor) * math.sin(math.radians(self.heading))
            
            # 4. Apply the changes
            self.latitude += lat_change
            self.longitude += lng_change
        
        # Rest periods may include small GPS jitter
        elif random.random() < 0.01:  # Occasional tiny GPS fluctuation when stationary
            self.latitude += random.uniform(-0.00001, 0.00001)
            self.longitude += random.uniform(-0.00001, 0.00001)
        
        # Driver break logic and state management - completely rewritten for consistency
        # Regular 5-minute breaks enforced regardless of vehicle state
        if self.cycle_count - self.last_driver1_break > 300:  # Force break every 5 minutes
            self.driver1_needs_break = True
            self.last_driver1_break = self.cycle_count
        
        if self.cycle_count - self.last_driver2_break > 300:
            self.driver2_needs_break = True
            self.last_driver2_break = self.cycle_count
            
        # Update activity counters for driver1
        if self.working_state_driver1 != "REST":
            self.driver1_active_cycles += 1
            self.driver1_rest_cycles = 0
            
            if self.driver1_active_cycles >= self.DRIVE_DURATION_BEFORE_BREAK:
                self.driver1_needs_break = True
        else:
            self.driver1_rest_cycles += 1
            self.driver1_active_cycles = 0
            
            if self.driver1_needs_break and self.driver1_rest_cycles >= self.DRIVER_BREAK_DURATION:
                self.driver1_needs_break = False
        
        # Update activity counters for driver2
        if self.working_state_driver2 != "REST":
            self.driver2_active_cycles += 1
            self.driver2_rest_cycles = 0
            
            if self.driver2_active_cycles >= self.DRIVE_DURATION_BEFORE_BREAK:
                self.driver2_needs_break = True
        else:
            self.driver2_rest_cycles += 1
            self.driver2_active_cycles = 0
            
            if self.driver2_needs_break and self.driver2_rest_cycles >= self.DRIVER_BREAK_DURATION:
                self.driver2_needs_break = False
        
        # IMPORTANT: Force driver breaks regardless of other logic - highest priority
        if self.driver1_needs_break:
            self.working_state_driver1 = "REST"
        
        if self.driver2_needs_break:
            self.working_state_driver2 = "REST"
            
        # Ensure driver roles are properly defined in all states
        if self.is_driving_period:
            # Primary driver needs to be driving if not on break
            if not self.driver1_needs_break and self.vehicle_speed > 5:
                self.working_state_driver1 = "DRIVE"
            elif not self.driver1_needs_break:
                self.working_state_driver1 = "WORK"  # Vehicle stopped but driver active
            
            # Secondary driver is available or driving depending on primary driver's state
            if not self.driver2_needs_break:
                if self.working_state_driver1 == "REST" and self.vehicle_speed > 5:
                    # If primary driver is resting but vehicle is moving, second driver takes over
                    self.working_state_driver2 = "DRIVE"
                elif self.working_state_driver1 == "REST":
                    # If both vehicle and primary driver are inactive, but secondary isn't on break
                    self.working_state_driver2 = "WORK"
                else:
                    # Default state for secondary driver when not active
                    self.working_state_driver2 = "AVAILABLE"
        else:
            # Vehicle not in driving period - default to REST for both unless otherwise specified
            if not self.driver1_needs_break and self.vehicle_speed <= 0:
                self.working_state_driver1 = "REST"
            
            if not self.driver2_needs_break and self.working_state_driver2 != "DRIVE":
                self.working_state_driver2 = "REST"
        
        # Additionally, driver swap logic for long drives
        if random.random() < 0.01 and self.is_driving_period and self.vehicle_speed > 20:  # 1% chance per cycle
            # Switch driving duties between drivers if possible
            if self.working_state_driver1 == "DRIVE" and not self.driver2_needs_break:
                # First driver takes a break, second driver takes over
                self.working_state_driver1 = "REST"
                self.working_state_driver2 = "DRIVE"
                self.driver1_active_cycles = 0  # Reset counter
                self.last_driver1_break = self.cycle_count  # Record break time
            elif self.working_state_driver2 == "DRIVE" and not self.driver1_needs_break:
                # Second driver takes a break, first driver takes over
                self.working_state_driver2 = "REST"
                self.working_state_driver1 = "DRIVE"
                self.driver2_active_cycles = 0  # Reset counter
                self.last_driver2_break = self.cycle_count  # Record break time
    
    def get_values(self):
        return {
            "working_state_driver1": self.working_state_driver1,
            "working_state_driver2": self.working_state_driver2,
            "is_card_present_driver1": self.is_card_present_driver1,
            "is_card_present_driver2": self.is_card_present_driver2,
            "vehicle_speed": round(self.vehicle_speed, 1),
            "engine_speed": round(self.engine_speed),
            "fuel_level": round(self.fuel_level, 1),
            "traveled_distance": self.traveled_distance,
            "air_temperature": round(self.air_temperature, 1),
            "engine_hours": round(self.engine_hours, 3),
            "parking_brake_engaged": self.parking_brake_engaged,
            "adblue_level": round(self.adblue_level, 1),
            "current_weight": round(self.current_weight),
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "driver1_needs_break": self.driver1_needs_break,
            "driver2_needs_break": self.driver2_needs_break,
            "driver1_active_cycles": self.driver1_active_cycles,
            "driver2_active_cycles": self.driver2_active_cycles,
            "driver1_rest_cycles": self.driver1_rest_cycles,
            "driver2_rest_cycles": self.driver2_rest_cycles,
        }

# Set up argument parser for command line options
parser = argparse.ArgumentParser(description='Generate vehicle data CSV file.')
parser.add_argument('--output', '-o', type=str, default='signalsFmsRecording.csv',
                    help='Output CSV file name (default: signalsFmsRecording.csv)')
args = parser.parse_args()

# Generate and write data to a new CSV file
with open(args.output, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["field", "signal", "value", "delay"])  # Header
    
    # Generate and write VIN only once at the beginning
    vin = f"YV2E4C3A5VB{random.randint(100000, 999999)}"
    
    # Create a vehicle state object
    vehicle = VehicleState()
    
    for _ in range(280):  # Adjust number of rows as needed
        vehicle.update()
        values = vehicle.get_values()

        writer.writerow(["current", "Vehicle.VehicleIdentification.VIN", vin, round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver1.WorkingState", values["working_state_driver1"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver2.WorkingState", values["working_state_driver2"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver1.IsCardPresent", str(values["is_card_present_driver1"]), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver2.IsCardPresent", str(values["is_card_present_driver2"]), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.VehicleSpeed", values["vehicle_speed"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Powertrain.FuelSystem.Tank.First.RelativeLevel", values["fuel_level"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.TraveledDistanceHighRes", values["traveled_distance"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Powertrain.CombustionEngine.DieselExhaustFluid.Level", int(round(values["adblue_level"])), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Speed", values["vehicle_speed"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Powertrain.CombustionEngine.Speed", values["engine_speed"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Chassis.ParkingBrake.IsEngaged", str(values["parking_brake_engaged"]), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Exterior.AirTemperature", values["air_temperature"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Powertrain.CombustionEngine.EngineHours", values["engine_hours"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.CurrentOverallWeight", values["current_weight"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.CurrentLocation.Latitude", values["latitude"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.CurrentLocation.Longitude", values["longitude"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver1.NeedsBreak", 
                        str(values["driver1_needs_break"]), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver2.NeedsBreak", 
                        str(values["driver2_needs_break"]), round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver1.ActiveCycles", 
                        values["driver1_active_cycles"], round(random.uniform(0, 1), 4)])
        writer.writerow(["current", "Vehicle.Tachograph.Driver.Driver2.ActiveCycles", 
                        values["driver2_active_cycles"], round(random.uniform(0, 1), 4)])

print(f"CSV file '{args.output}' generated successfully.")
