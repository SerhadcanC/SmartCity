from junction_configs import ALL_JUNCTION_CONFIGS
from traffic_model import TrafficModel
from vision_detector import VisionDetector
NUM_STEPS = 20

if __name__ == "__main__":
    model = TrafficModel(
        junction_configs=ALL_JUNCTION_CONFIGS,
        seed=42,
    )
    
    street_sources = {
        street: None  
        for config in ALL_JUNCTION_CONFIGS
        for street in config["street_names"]
    }
    
    detector = VisionDetector(street_sources=street_sources, use_simulated=True)
    
    for step in range(NUM_STEPS):
        print(f"\n{'=' * 50}")
        print(f"  STEP {step + 1:>2} / {NUM_STEPS}")
        print(f"{'=' * 50}")
        sensor_data = detector.detect_all()
        model.update_sensor_data(sensor_data)
        model.step()
        model.print_status()
    
    print(f"\n{'=' * 50}")
    print("  SIMULASYON SONA ERDI - ISTATISTIKLER")
    print(f"{'=' * 50}")
    model.print_summary()
    detector.release()
