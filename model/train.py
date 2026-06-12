"""
train.py — Script Training YOLOv8 TomatoScan v2

Cara pakai:
  1. Download dataset: https://www.kaggle.com/datasets/vasantharank/...
  2. Isi path di dataset/data.yaml
  3. Jalankan: python model/train.py
"""

import os, sys, shutil

try:
    from ultralytics import YOLO
except ImportError:
    print("[ERROR] ultralytics belum terinstall.")
    print("        Jalankan: pip install ultralytics")
    sys.exit(1)

BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_YAML = os.path.join(BASE_DIR, 'dataset_tomat', 'data.yaml')
MODEL_DIR = os.path.join(BASE_DIR, 'model')

CONFIG = {
    'model':    'yolov8n.pt',
    'data':     DATA_YAML,
    'epochs':   50,
    'imgsz':    640,
    'batch':    16,
    'patience': 10,
    'project':  MODEL_DIR,
    'name':     'tomatoscan_v2',
    'exist_ok': True,
    'pretrained': True,
    'verbose':  True,
}

def validate_dataset():
    if not os.path.exists(DATA_YAML):
        print(f"[ERROR] data.yaml tidak ditemukan: {DATA_YAML}")
        return False
    with open(DATA_YAML) as f:
        if 'GANTI_DENGAN_PATH' in f.read():
            print("[ERROR] Isi path dataset di dataset/data.yaml terlebih dahulu.")
            return False
    print(f"[OK] data.yaml ditemukan")
    return True

def train():
    print("=" * 55)
    print("  TomatoScan v2 — Training YOLOv8")
    print("=" * 55)

    if not validate_dataset():
        sys.exit(1)

    os.makedirs(MODEL_DIR, exist_ok=True)
    model = YOLO(CONFIG['model'])
    model.train(**CONFIG)

    best_src = os.path.join(MODEL_DIR, CONFIG['name'], 'weights', 'best.pt')
    best_dst = os.path.join(MODEL_DIR, 'best.pt')
    if os.path.exists(best_src):
        shutil.copy2(best_src, best_dst)
        print(f"\n[DONE] Model disalin ke: {best_dst}")
    else:
        print(f"\n[WARNING] best.pt tidak ditemukan, cari di folder model/tomatoscan_v2/weights/")

if __name__ == '__main__':
    train()