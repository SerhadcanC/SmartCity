from junction_configs import four_way_junction, u_turn_junction, merge_junction, three_way_junction
from traffic_model import TrafficModel
from vision_detector import VisionDetector

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
    
    # Tüm kavşaklardaki yolları toplayıp kamera simülatörüne verelim
    street_sources = {}
    for config in junction_configs:
        for street in config["street_names"]:
            street_sources[street] = None # None = Simüle kamera

    detector = VisionDetector(street_sources=street_sources, use_simulated=True)

    for step in range(20):
        print(f"\n=========== STEP {step + 1} ==========")
        
        # 1. Kameradan/YOLO'dan araç sayılarını al
        sensor_data = detector.detect_all()
        
        # 2. Bu veriyi modele vererek simülasyonu 1 adım ilerlet
        model.update_sensor_data(sensor_data)
        model.step()
        
        model.print_status()