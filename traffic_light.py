import mesa

class TrafficLight(mesa.Agent):
    def __init__(self, model, street_name, junction_id):
        super().__init__(model)

        self.street_name = street_name
        self.junction_id = junction_id

        self.vehicle_count = 0
        self.waiting_time = 0
        self.status = "RED"

    def update_vehicle_count(self, count):
        """Update count based on sensor data"""
        self.vehicle_count = count

    def calculate_priority_score(self):
        """priority calculation based on the number of vehicles and waiting time."""
        return (self.vehicle_count * 2) + (self.waiting_time * 0.5)

    def set_green(self):
        self.status = "GREEN"

    def set_red(self):
        self.status = "RED"

    def pass_vehicles(self, capacity):
        passed_cars = min(self.vehicle_count, capacity)
        self.vehicle_count -= passed_cars

        if self.vehicle_count == 0:
            self.waiting_time = 0

    def step(self):
        # vehicle_count is now updated externally by the model before step()
        
        if self.status == "RED" and self.vehicle_count > 0:
            self.waiting_time += 1

    def __repr__(self):
        return(
            f"Junction: {self.junction_id}, "
            f"Street Name: {self.street_name}, "
            f"Vehicle Count: {self.vehicle_count}, "
            f"Waiting Time: {self.waiting_time}, "
            f"Status: {self.status}"
        )
