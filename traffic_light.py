import mesa

class TrafficLight(mesa.Agent):
    STARVATION_THRESHOLD = 10
    STARVATION_BONUS = 50
    
    def __init__(self, model, street_name: str, junction_id: str):
        super().__init__(model)
        self.street_name = street_name
        self.junction_id = junction_id
        self.vehicle_count: int = 0
        self.waiting_time: int = 0
        self.status: str = "RED"
        self.total_green_steps: int = 0
        self.total_passed_vehicles: int = 0
    
    def update_vehicle_count(self, count: int):
        self.vehicle_count = max(0, count)
    
    def calculate_priority_score(self) -> float:
        base_score = (self.vehicle_count * 2) + (self.waiting_time * 0.5)
        starvation_bonus = (
            self.STARVATION_BONUS
            if self.waiting_time >= self.STARVATION_THRESHOLD
            else 0
        )
        return base_score + starvation_bonus
    
    def set_green(self):
        self.status = "GREEN"
        self.total_green_steps += 1
    
    def set_red(self):
        self.status = "RED"
    
    def pass_vehicles(self, capacity: int):
        passed = min(self.vehicle_count, capacity)
        self.vehicle_count -= passed
        self.total_passed_vehicles += passed
        if self.vehicle_count == 0:
            self.waiting_time = 0
    
    def step(self):
        if self.status == "RED" and self.vehicle_count > 0:
            self.waiting_time += 1
    
    def __repr__(self):
        priority = self.calculate_priority_score()
        starving = "[STARVING]" if self.waiting_time >= self.STARVATION_THRESHOLD else ""
        return (
            f"Junction: {self.junction_id}, "
            f"Street: {self.street_name}, "
            f"Vehicles: {self.vehicle_count}, "
            f"Wait: {self.waiting_time}, "
            f"Status: {self.status}, "
            f"Priority: {priority:.1f} {starving}"
        )
