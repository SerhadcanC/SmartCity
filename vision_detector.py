"""
vision_detector.py
------------------
YOLO11n tabanlı araç tespit modülü.

Görev:
    Her yol (street) için bağlı kamera kaynağından (simüle/gerçek)
    araç sayısını tespit eder ve sensor_data sözlüğü olarak döndürür.

Kullanım:
    detector = VisionDetector(street_sources, use_simulated=True)
    sensor_data = detector.detect_all()
    # -> {"North_Main": 3, "East_Road": 7, ...}

Gerçek kaynağa geçmek için:
    use_simulated=False yapılır ve street_sources içindeki
    değerler video dosya yolu veya kamera index'i olur.
"""

import random
import os

try:
    from ultralytics import YOLO
    YOLO_AVAILABLE = True
except ImportError:
    YOLO_AVAILABLE = False
    print("[VisionDetector] UYARI: 'ultralytics' kütüphanesi bulunamadı.")
    print("[VisionDetector] Gerçek YOLO için: pip install ultralytics")
    print("[VisionDetector] Simüle mod kullanılacak.\n")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False


# COCO veri setindeki araç sınıfları (class id -> isim)
# Hangi sınıfların sayılacağı TRACKED_CLASSES ile belirlenir.
COCO_VEHICLE_CLASSES = {
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck",
    1: "bicycle",
}

# Yalnızca bu sınıflar sayılacak.
# Proje kararına göre sadece "car" tutuldu.
TRACKED_CLASSES = {2}  # 2 = car


class SimulatedCamera:
    """
    Gerçek bir kamera yerine sahte araç yoğunluğu üreten simülatör.
    Her 'çekim' (capture) için 0-15 arası rastgele araç sayısı döndürür.
    Gerçek kamera/video ile değiştirildiğinde bu sınıf devre dışı kalır.
    """

    def __init__(self, street_name: str, seed: int = None):
        self.street_name = street_name
        self._rng = random.Random(seed)
        # Yolun karakteri: yoğun mu, sakin mi? (0.0 - 1.0)
        self._density_profile = self._rng.uniform(0.1, 1.0)

    def capture(self) -> "SimulatedFrame":
        """
        Simüle edilmiş bir kare döndürür.
        Gerçek kaynak kullanımında cv2.VideoCapture.read() ile değiştirilir.
        """
        # Yoğunluk profiline göre araç sayısı üret
        base = int(self._density_profile * 15)
        noise = self._rng.randint(-2, 2)
        vehicle_count = max(0, base + noise)
        return SimulatedFrame(self.street_name, vehicle_count)

    def release(self):
        pass  # Gerçek kamerada cv2.VideoCapture.release() çağrılır


class SimulatedFrame:
    """
    Simüle edilmiş kare. Araç sayısını doğrudan saklar.
    Gerçek kullanımda bu bir numpy array (OpenCV frame) olur.
    """

    def __init__(self, street_name: str, vehicle_count: int):
        self.street_name = street_name
        self._vehicle_count = vehicle_count
        self.is_simulated = True

    @property
    def simulated_count(self) -> int:
        return self._vehicle_count


class VisionDetector:
    """
    YOLO11n tabanlı araç tespit motoru.

    Parametreler:
        street_sources (dict):
            Her sokak ismine karşılık gelen veri kaynağı.
            Simüle modda: {"North_Main": None, "East_Road": None, ...}
            Gerçek modda: {"North_Main": "videos/north.mp4", ...}
                          {"Cam1": 0, "Cam2": 1, ...}  <- kamera index

        use_simulated (bool):
            True  -> SimulatedCamera kullanılır (test için)
            False -> Gerçek video/kamera kaynağı kullanılır

        model_path (str):
            YOLO model dosya yolu. Varsayılan: "yolo11n.pt"
            İlk çalıştırmada model otomatik indirilir.

        confidence_threshold (float):
            Tespitin geçerli sayılması için minimum güven skoru (0.0-1.0)

        tracked_classes (set):
            Sayılacak COCO sınıf id'leri. Varsayılan: {2} (sadece car)

        verbose (bool):
            True -> Her tespitte detaylı çıktı verir
    """

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
        print(f"[VisionDetector] Simüle mod aktif. {len(self._cameras)} yol tanımlandı.")

    def _setup_real_cameras(self):
        if not CV2_AVAILABLE:
            raise ImportError(
                "Gerçek kamera modu için OpenCV gerekli: pip install opencv-python"
            )
        for street_name, source in self.street_sources.items():
            cap = cv2.VideoCapture(source)
            if not cap.isOpened():
                print(f"[VisionDetector] UYARI: '{street_name}' kaynağı açılamadı -> {source}")
            self._cameras[street_name] = cap
        print(f"[VisionDetector] Gerçek kamera modu aktif. {len(self._cameras)} kaynak yüklendi.")

    def _load_yolo_model(self):
        if not YOLO_AVAILABLE:
            raise ImportError(
                "YOLO kullanımı için ultralytics gerekli: pip install ultralytics"
            )
        print(f"[VisionDetector] YOLO modeli yükleniyor: {self.model_path}")
        self._model = YOLO(self.model_path)
        print(f"[VisionDetector] Model hazır.")


    def _detect_from_simulated(self, street_name: str) -> int:
        
        camera: SimulatedCamera = self._cameras[street_name]
        frame = camera.capture()
        count = frame.simulated_count

        if self.verbose:
            print(f"   [SIM] {street_name}: {count} araç tespit edildi (simüle)")

        return count

    def _detect_from_real(self, street_name: str) -> int:
        
        cap: "cv2.VideoCapture" = self._cameras[street_name]

        if not cap.isOpened():
            if self.verbose:
                print(f"   [REAL] {street_name}: Kamera kapalı, 0 döndürülüyor.")
            return 0

        ret, frame = cap.read()

        # Video bittiyse başa sar (loop)
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                return 0

        # YOLO inference
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
            print(f"[VisionDetector] UYARI: '{street_name}' tanımlı değil.")
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
        """Tüm kamera kaynaklarını serbest bırakır."""
        for street_name, camera in self._cameras.items():
            camera.release()
        print("[VisionDetector] Tüm kamera kaynakları serbest bırakıldı.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def __repr__(self):
        mode = "Simüle" if self.use_simulated else "Gerçek"
        return (
            f"VisionDetector(mod={mode}, "
            f"yollar={list(self._cameras.keys())}, "
            f"model={self.model_path})"
        )
