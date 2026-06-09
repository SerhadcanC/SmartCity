class JunctionController:
    
    def __init__(
        self,
        junction_id: str,
        junction_type: str,
        traffic_lights: list,
        conflict_map: dict,
        green_capacity: int = 4,
        allow_parallel_green: bool = False,
        min_green_interval: int = 0,
    ):
        self.junction_id = junction_id
        self.junction_type = junction_type
        self.traffic_lights = traffic_lights
        self.conflict_map = conflict_map
        self.green_capacity = green_capacity
        self.allow_parallel_green = allow_parallel_green
        self.min_green_interval = min_green_interval
        self.current_green_streets: list[str] = []
        self.lights_by_street: dict = {
            light.street_name: light for light in self.traffic_lights
        }
        self._consecutive_green: dict[str, int] = {
            light.street_name: 0 for light in self.traffic_lights
        }
    
    def get_conflict_streets(self, street_name: str) -> list:
        return self.conflict_map.get(street_name, [])
    
    def can_be_green(self, candidate_street: str, already_green_streets: list) -> bool:
        candidate_conflicts = set(self.get_conflict_streets(candidate_street))
        for green_street in already_green_streets:
            if green_street in candidate_conflicts:
                return False
            green_conflicts = set(self.get_conflict_streets(green_street))
            if candidate_street in green_conflicts:
                return False
        return True
    
    def _is_overstaying(self, street_name: str) -> bool:
        if self.min_green_interval <= 0:
            return False
        return self._consecutive_green.get(street_name, 0) >= self.min_green_interval
    
    def choose_green_lights(self) -> list[str]:
        sorted_lights = sorted(
            self.traffic_lights,
            key=lambda light: light.calculate_priority_score(),
            reverse=True,
        )
        selected_green_streets: list[str] = []
        for light in sorted_lights:
            if light.vehicle_count <= 0:
                continue
            if self._is_overstaying(light.street_name) and len(selected_green_streets) == 0:
                pass  
            if not self.allow_parallel_green:
                if not self._is_overstaying(light.street_name):
                    selected_green_streets = [light.street_name]
                    break
            else:
                if self.can_be_green(light.street_name, selected_green_streets):
                    selected_green_streets.append(light.street_name)
        if not selected_green_streets:
            for light in sorted_lights:
                if light.vehicle_count > 0:
                    selected_green_streets = [light.street_name]
                    break
        return selected_green_streets
    
    def apply_light_status(self, selected_green_streets: list[str]):
        for light in self.traffic_lights:
            if light.street_name in selected_green_streets:
                light.set_green()
                self._consecutive_green[light.street_name] = (
                    self._consecutive_green.get(light.street_name, 0) + 1
                )
            else:
                light.set_red()
                self._consecutive_green[light.street_name] = 0
        self.current_green_streets = selected_green_streets
    
    def pass_vehicles_from_green_lights(self):
        for street_name in self.current_green_streets:
            light = self.lights_by_street[street_name]
            light.pass_vehicles(self.green_capacity)
    
    def step(self):
        selected_green_streets = self.choose_green_lights()
        self.apply_light_status(selected_green_streets)
        self.pass_vehicles_from_green_lights()
    
    def get_stats(self) -> dict:
        return {
            "junction_id": self.junction_id,
            "junction_type": self.junction_type,
            "current_green": self.current_green_streets,
            "lights": [
                {
                    "street": l.street_name,
                    "vehicles": l.vehicle_count,
                    "waiting": l.waiting_time,
                    "priority": round(l.calculate_priority_score(), 2),
                    "status": l.status,
                    "total_passed": l.total_passed_vehicles,
                }
                for l in self.traffic_lights
            ],
        }
    
    def __repr__(self):
        return (
            f"Junction: {self.junction_id}, "
            f"Type: {self.junction_type}, "
            f"Green: {self.current_green_streets}"
        )
