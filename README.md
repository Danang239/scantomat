# 🍅 TomatoScan v2

Aplikasi deteksi penyakit daun tomat berbasis kecerdasan buatan menggunakan model **YOLOv8** dan **Flask**. Mendukung 10 kelas penyakit dari dataset PlantVillage (vasantharank/Kaggle) dengan saran penanganan dari **Groq AI (LLaMA 3.1)**.

## 📊 Performa Model

| Metrik | Nilai |
|---|---|
| mAP50 | **98.3%** |
| mAP50-95 | **86.6%** |
| Precision | **93.4%** |
| Recall | **94.3%** |
| Epoch Terbaik | 36 / 50 |

## 🌿 10 Kelas yang Dapat Dideteksi

| # | Nama Kelas | Nama Indonesia | Tingkat Bahaya |
|---|---|---|---|
| 0 | Tomato Bacterial Spot | Bercak Bakteri | Sedang |
| 1 | Tomato Early blight | Hawar Awal | Sedang |
| 2 | Tomato Late blight | Hawar Daun Akhir | Tinggi |
| 3 | Tomato Leaf Mold | Jamur Daun | Sedang |
| 4 | Tomato Septoria leaf spot | Bercak Septoria | Sedang |
| 5 | Tomato Spider mites | Tungau Laba-laba | Sedang |
| 6 | Tomato Target Spot | Bercak Target | Sedang |
| 7 | Tomato Yellow Leaf Curl Virus | Virus Keriting Kuning | Tinggi |
| 8 | Tomato healthy | Daun Sehat | Sehat |
| 9 | Tomato mosaic virus | Virus Mosaik | Tinggi |

## ⚙️ Tech Stack

- **Model AI** : YOLOv8s (Ultralytics)
- **Backend** : Python 3.12 + Flask
- **AI Saran** : Groq API (LLaMA 3.1)
- **Image Processing** : OpenCV + Pillow
- **PDF Export** : ReportLab
- **Dataset** : PlantVillage YOLOv8 — vasantharank (Kaggle)

## 📁 Struktur Folder

```
TomatoScan/
├── backend/
│   ├── app.py              ← Flask server utama
│   ├── predictor.py        ← Inferensi YOLOv8 + bounding box
│   ├── disease_info.py     ← Database 10 penyakit
│   ├── ai_advice.py        ← Saran AI via Groq
│   └── pdf_generator.py    ← Export laporan PDF
├── frontend/
│   ├── templates/
│   │   ├── index.html      ← Halaman upload
│   │   ├── result.html     ← Halaman hasil deteksi
│   │   ├── about.html      ← Halaman tentang proyek
│   │   ├── history.html    ← Riwayat deteksi lokal
│   │   └── 404.html        ← Halaman error
│   └── static/
│       ├── css/style.css   ← Stylesheet utama
│       ├── js/main.js      ← Script frontend
│       └── uploads/        ← Foto yang diupload user
├── model/
│   ├── train.py            ← Script training YOLOv8
│   └── best.pt             ← Model terlatih (generate setelah training)
├── dataset/
│   ├── data.yaml           ← Konfigurasi dataset
│   ├── train/              ← Dataset training
│   ├── valid/              ← Dataset validasi
│   └── test/               ← Dataset pengujian
├── requirements.txt
└── README.md
```

## 🚀 Instalasi & Menjalankan

### Prasyarat
- Python 3.12
- GPU NVIDIA (opsional, untuk training lebih cepat)
- Virtual environment (disarankan)

### 1. Clone & Setup Environment

```bash
# Buat virtual environment
py -3.12 -m venv .venv

# Aktifkan (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Aktifkan (Linux / macOS)
source .venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
pip install -r requirements.txt
```

> Jika tidak punya GPU NVIDIA, skip perintah torch CUDA dan langsung:
> ```bash
> pip install -r requirements.txt
> ```

### 3. Download & Siapkan Dataset

1. Download dataset dari Kaggle:
   👉 https://www.kaggle.com/datasets/vasantharank/tomato-leaf-disease-detection-yolov8-dataset

2. Ekstrak dan letakkan isinya ke folder `dataset/` dengan struktur:

```
dataset/
├── train/
│   ├── images/
│   └── labels/
├── valid/
│   ├── images/
│   └── labels/
└── test/
    ├── images/
    └── labels/
```

> Jika folder dari Kaggle bernama `validation`, rename menjadi `valid`.

### 4. Training Model

```bash
python model/train.py
```

File `model/best.pt` akan otomatis tersimpan setelah selesai.
Estimasi waktu: **1–2 jam** dengan GPU, lebih lama dengan CPU.

> Untuk uji coba cepat, ubah `"epochs": 100` menjadi `"epochs": 5` di `model/train.py`.

### 5. Set API Key Groq (Opsional)

Dapatkan API key gratis di: https://console.groq.com

```bash
# Windows PowerShell
$env:GROQ_API_KEY="gsk_xxxxxxxxxxxxxx"

# Linux / macOS
export GROQ_API_KEY=gsk_xxxxxxxxxxxxxx
```

> Jika tidak di-set, aplikasi tetap berjalan dengan saran penanganan dari database lokal.

### 6. Jalankan Aplikasi

```bash
python backend/app.py
```

Buka browser: **http://localhost:5000**

## 📖 Cara Penggunaan

1. **Upload foto** daun tomat di halaman utama
2. **Atur confidence** threshold sesuai kebutuhan (default 25%)
3. Klik **Analisis Sekarang**
4. Lihat hasil deteksi lengkap dengan:
   - Bounding box pada gambar
   - Nama penyakit dan tingkat bahaya
   - Deskripsi dan gejala penyakit
   - Saran penanganan dari Groq AI
5. **Unduh** hasil sebagai foto atau laporan PDF
6. Lihat **riwayat** deteksi sebelumnya di menu Riwayat

## 📦 Dependencies

```
ultralytics>=8.0.0
flask>=3.0.0
pillow>=10.0.0
opencv-python>=4.8.0
numpy>=1.24.0
torch>=2.0.0
torchvision>=0.15.0
werkzeug>=3.0.0
pyyaml>=6.0.0
reportlab>=4.0.0
requests>=2.31.0
pandas>=2.0.0
```

## ⚠️ Disclaimer

Hasil deteksi TomatoScan bersifat **indikatif** dan tidak menggantikan diagnosis dari ahli pertanian atau penyuluh lapangan. Selalu konsultasikan hasil dengan tenaga ahli sebelum mengambil tindakan penanganan.

---

*TomatoScan v2 — YOLOv8 + PlantVillage Dataset + Groq AI*
