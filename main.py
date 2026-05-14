from junction_configs import four_way_junction, u_turn_junction, merge_junction, three_way_junction
from traffic_model import TrafficModel

if __name__ == "__main__":

    junction_configs = [
        four_way_junction,
        u_turn_junction,
        merge_junction,
        three_way_junction
    ]

    model = TrafficModel(
        junction_configs=junction_configs,
        seed=42
    )

    for step in range(20):
        print(f"\n=========== STEP {step + 1} ==========")

        model.step()
        model.print_status()