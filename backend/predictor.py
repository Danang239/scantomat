import os
import cv2
import numpy as np
from ultralytics import YOLO

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, '..', 'model', 'best.pt')
UPLOAD_DIR = os.path.join(BASE_DIR, '..', 'frontend', 'static', 'uploads')

CLASS_NAMES = {
    0: 'Tomato Bacterial Spot',
    1: 'Tomato Early blight',
    2: 'Tomato Late blight',
    3: 'Tomato Leaf Mold',
    4: 'Tomato Septoria leaf spot',
    5: 'Tomato Spider mites Two-spotted spider mite',
    6: 'Tomato Target Spot',
    7: 'Tomato Yellow Leaf Curl Virus',
    8: 'Tomato healthy',
    9: 'Tomato mosaic virus',
}

# Warna bounding box per kelas (BGR)
CLASS_COLORS = {
    'Tomato Bacterial Spot'                          : (255, 140,   0),
    'Tomato Early blight'                            : (255, 165,   0),
    'Tomato Late blight'                             : (220,  20,  60),
    'Tomato Leaf Mold'                               : (138,  43, 226),
    'Tomato Septoria leaf spot'                      : ( 64, 164, 223),
    'Tomato Spider mites Two-spotted spider mite'    : (200, 100,  50),
    'Tomato Target Spot'                             : (255, 215,   0),
    'Tomato Yellow Leaf Curl Virus'                  : (  0, 200, 200),
    'Tomato healthy'                                 : ( 50, 205,  50),
    'Tomato mosaic virus'                            : (255,   0, 255),
}
DEFAULT_COLOR = (100, 100, 255)

_model = None


def _load_model():
    global _model
    if not os.path.exists(MODEL_PATH):
        print(f"[WARNING] Model tidak ditemukan: {MODEL_PATH}")
        print("          Jalankan python model/train.py terlebih dahulu.")
        return False
    try:
        _model = YOLO(MODEL_PATH)
        print(f"[INFO] Model berhasil dimuat dari {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"[ERROR] Gagal memuat model: {e}")
        return False


def _draw_boxes(image_path: str, results, class_name: str) -> str:
    """
    Gambar bounding box pada gambar asli dan simpan sebagai file baru.
    Return: path relatif untuk ditampilkan di HTML (misal: uploads/result_xxx.jpg)
    """
    img = cv2.imread(image_path)
    if img is None:
        return None

    boxes = results[0].boxes
    if boxes is not None and len(boxes) > 0:
        for box in boxes:
            cls_id = int(box.cls[0])
            conf   = float(box.conf[0])
            name   = CLASS_NAMES.get(cls_id, f'Kelas {cls_id}')
            color  = CLASS_COLORS.get(name, DEFAULT_COLOR)

            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            label = f"{name.replace('Tomato ', '')} {conf*100:.1f}%"

            # Gambar kotak
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)

            # Background label
            (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img, (x1, y1 - th - 8), (x1 + tw + 6, y1), color, -1)

            # Teks label
            cv2.putText(
                img, label, (x1 + 3, y1 - 4),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA
            )

    # Simpan gambar hasil
    base_name   = os.path.splitext(os.path.basename(image_path))[0]
    result_name = f"result_{base_name}.jpg"
    result_path = os.path.join(UPLOAD_DIR, result_name)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    cv2.imwrite(result_path, img)

    return f"uploads/{result_name}"


def predict_image(image_path: str, conf_threshold: float = 0.25) -> dict | None:
    """
    Jalankan prediksi YOLOv8 pada gambar.

    Return dict:
        class_id        : int
        class_name      : str
        confidence      : float (0-1)
        bbox            : list [x1, y1, x2, y2] koordinat bounding box terbaik
        result_image    : str path relatif gambar dengan bounding box
        all_detections  : list semua deteksi (untuk multi-object)
    """
    global _model
    if _model is None:
        if not _load_model():
            return None

    try:
        results = _model(image_path, conf=conf_threshold, verbose=False)
        if not results:
            return None

        boxes = results[0].boxes
        if boxes is None or len(boxes) == 0:
            # Tidak ada deteksi — tetap generate gambar asli tanpa box
            result_image = _draw_boxes(image_path, results, '')
            return {
                'class_id'      : -1,
                'class_name'    : 'Tomato healthy',
                'confidence'    : 0.0,
                'bbox'          : None,
                'result_image'  : result_image,
                'all_detections': [],
            }

        confidences = boxes.conf.cpu().numpy()
        classes     = boxes.cls.cpu().numpy().astype(int)
        best_idx    = int(confidences.argmax())
        class_id    = int(classes[best_idx])
        class_name  = CLASS_NAMES.get(class_id, f'Kelas {class_id}')

        # Ambil koordinat bounding box deteksi terbaik
        best_box = boxes.xyxy[best_idx].cpu().numpy().tolist()
        bbox     = [int(best_box[0]), int(best_box[1]),
                    int(best_box[2]), int(best_box[3])]

        # Kumpulkan semua deteksi
        all_detections = []
        for i in range(len(boxes)):
            cid  = int(classes[i])
            all_detections.append({
                'class_id'  : cid,
                'class_name': CLASS_NAMES.get(cid, f'Kelas {cid}'),
                'confidence': float(confidences[i]),
            })

        # Generate gambar dengan bounding box
        result_image = _draw_boxes(image_path, results, class_name)

        return {
            'class_id'      : class_id,
            'class_name'    : class_name,
            'confidence'    : float(confidences[best_idx]),
            'bbox'          : bbox,
            'result_image'  : result_image,
            'all_detections': all_detections,
        }

    except Exception as e:
        print(f"[ERROR] Prediksi gagal: {e}")
        return None