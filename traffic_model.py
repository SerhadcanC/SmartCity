import mesa
from junction_controller import JunctionController
from traffic_light import TrafficLight

class TrafficModel(mesa.Model):
    
    def __init__(self, junction_configs: list, seed=None):
        super().__init__(rng=seed)
        self.traffic_lights: list[TrafficLight] = []
        self.junctions: list[JunctionController] = []
        self._create_junctions(junction_configs)
    
    def _create_junctions(self, junction_configs: list):
        
        for config in junction_configs:
            junction_id   = config["junction_id"]
            junction_type = config["junction_type"]
            street_names  = config["street_names"]
            conflict_map  = config["conflict_map"]
            green_capacity       = config.get("green_capacity", 4)
            allow_parallel_green = config.get("allow_parallel_green", False)
            min_green_interval   = config.get("min_green_interval", 0)
            lights: list[TrafficLight] = []
            
            for street_name in street_names:
                light = TrafficLight(
                    model=self,
                    street_name=street_name,
                    junction_id=junction_id,
                )
                lights.append(light)
                self.traffic_lights.append(light)
            junction = JunctionController(
                junction_id=junction_id,
                junction_type=junction_type,
                traffic_lights=lights,
                conflict_map=conflict_map,
                green_capacity=green_capacity,
                allow_parallel_green=allow_parallel_green,
                min_green_interval=min_green_interval,
            )
            self.junctions.append(junction)
    
    def update_sensor_data(self, sensor_data: dict):
        for light in self.traffic_lights:
            if light.street_name in sensor_data:
                light.update_vehicle_count(sensor_data[light.street_name])
    
    def step(self):
        for light in self.traffic_lights:
            light.step()
        for junction in self.junctions:
            junction.step()
    
    def print_status(self):
        for junction in self.junctions:
            print(junction)
            for light in junction.traffic_lights:
                print("   ", light)
    
    def print_summary(self):
        print(f"\n{'-' * 55}")
        for junction in self.junctions:
            print(f"Kavsak: {junction.junction_id} ({junction.junction_type})")
            for light in junction.traffic_lights:
                print(
                    f"  {light.street_name:<20} | "
                    f"Gecen arac: {light.total_passed_vehicles:>4} | "
                    f"Yesil adim: {light.total_green_steps:>3} | "
                    f"Bekleyen: {light.vehicle_count:>3}"
                )
        print(f"{'-' * 55}")
