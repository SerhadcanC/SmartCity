import random
import os

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[VisionDetector] UYARI: 'ultralytics' kutuphanesi bulunamadi.")
    print("[VisionDetector] Gercek YOLO icin: pip install ultralytics")
    print("[VisionDetector] Simule mod kullanilacak.\n")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
COCO_VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    1: "bicycle",
}

TRACKED_CLASSES = {2} 

class SimulatedCamera:
    def __init__(self, street_name: str, seed: int = None):
        self.street_name = street_name
        self._rng = random.Random(seed)
        self._density_profile = self._rng.uniform(0.1, 1.0)
    def capture(self) -> "SimulatedFrame":
        base = int(self._density_profile * 15)
        noise = self._rng.randint(-2, 2)
        vehicle_count = max(0, base + noise)
        return SimulatedFrame(self.street_name, vehicle_count)
    def release(self):
        pass  

class SimulatedFrame:
    def __init__(self, street_name: str, vehicle_count: int):
        self.street_name = street_name
        self._vehicle_count = vehicle_count
        self.is_simulated = True
    @property
    def simulated_count(self) -> int:
        return self._vehicle_count

class VisionDetector:
    def __init__(
        self,
        street_sources: dict,
        use_simulated: bool = True,
        model_path: str = "yolo11n.pt",
        confidence_threshold: float = 0.4,
        tracked_classes: set = None,
        verbose: bool = False,
    ):
        self.street_sources = street_sources
        self.use_simulated = use_simulated
        self.confidence_threshold = confidence_threshold
        self.tracked_classes = tracked_classes if tracked_classes else TRACKED_CLASSES
        self.verbose = verbose
        self.model_path = model_path
        self._model = None
        self._cameras = {}
        self._setup()
    
    def _setup(self):
        if self.use_simulated:
            self._setup_simulated_cameras()
        else:
            self._setup_real_cameras()
            self._load_yolo_model()
    
    def _setup_simulated_cameras(self):
        for street_name in self.street_sources:
            self._cameras[street_name] = SimulatedCamera(street_name)
        print(f"[VisionDetector] Simule mod aktif. {len(self._cameras)} yol tanimlandi.")
    
    def _setup_real_cameras(self):
        if not CV2_AVAILABLE:
            raise ImportError(
                "Gercek kamera modu icin OpenCV gerekli: pip install opencv-python"
            )
        for street_name, source in self.street_sources.items():
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"[VisionDetector] UYARI: '{street_name}' kaynagi acilamadi -> {source}")
            self._cameras[street_name] = cap
        print(f"[VisionDetector] Gercek kamera modu aktif. {len(self._cameras)} kaynak yuklendi.")
    
    def _load_yolo_model(self):
        if not YOLO_AVAILABLE:
            raise ImportError(
                "YOLO kullanımı için ultralytics gerekli: pip install ultralytics"
            )
        print(f"[VisionDetector] YOLO modeli yukleniyor: {self.model_path}")
        self._model = YOLO(self.model_path)
        print(f"[VisionDetector] Model hazir.")
    
    def _detect_from_simulated(self, street_name: str) -> int:
        camera: SimulatedCamera = self._cameras[street_name]
        frame = camera.capture()
        count = frame.simulated_count
        if self.verbose:
            print(f"   [SIM] {street_name}: {count} arac tespit edildi (simule)")
        return count
    
    def _detect_from_real(self, street_name: str) -> int:
        cap: "cv2.VideoCapture" = self._cameras[street_name]
        if not cap.isOpened():
            if self.verbose:
                print(f"   [REAL] {street_name}: Kamera kapalı, 0 döndürülüyor.")
            return 0
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                return 0
        results = self._model(frame, verbose=False)
        count = 0
        for result in results:
            boxes = result.boxes
            if boxes is None:
                continue
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if cls_id in self.tracked_classes and conf >= self.confidence_threshold:
                    count += 1
                    if self.verbose:
                        cls_name = COCO_VEHICLE_CLASSES.get(cls_id, "unknown")
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        print(
                            f"   [REAL] {street_name}: {cls_name} "
                            f"(conf={conf:.2f}) tespit edildi."
                        )
        if self.verbose:
            print(f"   [REAL] {street_name}: Toplam {count} araç.")
        return count
    
    def detect_street(self, street_name: str) -> int:
        if street_name not in self._cameras:
            print(f"[VisionDetector] UYARI: '{street_name}' tanimli degil.")
            return 0
        if self.use_simulated:
            return self._detect_from_simulated(street_name)
        else:
            return self._detect_from_real(street_name)
    
    def detect_all(self) -> dict:
        sensor_data = {}
        for street_name in self._cameras:
            sensor_data[street_name] = self.detect_street(street_name)
        return sensor_data
    
    def release(self):
        for street_name, camera in self._cameras.items():
            camera.release()
        print("[VisionDetector] Tum kamera kaynaklari serbest birakildi.")
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
    
    def __repr__(self):
        mode = "Simule" if self.use_simulated else "Gercek"
        return (
            f"VisionDetector(mod={mode}, "
            f"yollar={list(self._cameras.keys())}, "
            f"model={self.model_path})"
        )
