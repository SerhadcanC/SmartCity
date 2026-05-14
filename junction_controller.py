class JunctionController:
    def __init__(
        self,
        junction_id,
        junction_type,
        traffic_lights,
        conflict_map,
        green_capacity=4,
        allow_parallel_green=False
    ):
        self.junction_id = junction_id
        self.junction_type = junction_type
        self.traffic_lights = traffic_lights
        self.conflict_map = conflict_map
        self.green_capacity = green_capacity
        self.allow_parallel_green = allow_parallel_green

        self.current_green_streets = []

        self.lights_by_street = {
            light.street_name: light for light in self.traffic_lights
        }

    def get_conflict_streets(self, street_name):
        return self.conflict_map.get(street_name, [])

    def can_be_green(self, candidate_street, already_green_streets):
        candidate_conflicts = set(self.get_conflict_streets(candidate_street))

        for green_street in already_green_streets:
            if green_street in candidate_conflicts:
                return False

        return True

    def choose_green_lights(self):
        sorted_lights = sorted(
            self.traffic_lights,
            key=lambda light: light.calculate_priority_score(),
            reverse=True
        )

        selected_green_streets = []

        for light in sorted_lights:
            if light.vehicle_count <= 0:
                continue

            if not self.allow_parallel_green:
                selected_green_streets = [light.street_name]
                break

            if self.can_be_green(light.street_name, selected_green_streets):
                selected_green_streets.append(light.street_name)

        return selected_green_streets

    def apply_light_status(self, selected_green_streets):
        for light in self.traffic_lights:
            if light.street_name in selected_green_streets:
                light.set_green()
            else:
                light.set_red()

        self.current_green_streets = selected_green_streets

    def pass_vehicles_from_green_lights(self):
        for street_name in self.current_green_streets:
            light = self.lights_by_street[street_name]
            light.pass_vehicles(self.green_capacity)

    def step(self):
        selected_green_streets = self.choose_green_lights()
        self.apply_light_status(selected_green_streets)
        self.pass_vehicles_from_green_lights()

    def __repr__(self):
        return(
            f"Junction: {self.junction_id}, "
            f"Type: {self.junction_type}, "
            f"Green Lights: {self.current_green_streets}"
        )
