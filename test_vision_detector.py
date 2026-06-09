from vision_detector import VisionDetector

street_sources = {
    "North_Main": None,   
    "South_Main": None,
    "East_Road":  None,
    "West_Road":  None,
}

detector = VisionDetector(
    street_sources=street_sources,
    use_simulated=True,   
    verbose=True,         
)

print(f"\nDedektör: {detector}\n")

for step in range(1, 6):
    print(f"--- Adım {step} ---")
    sensor_data = detector.detect_all()
    print(f"sensor_data: {sensor_data}\n")
detector.release()
