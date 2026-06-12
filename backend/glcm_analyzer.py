import os
import cv2
import numpy as np

try:
    from skimage.feature import graycomatrix, graycoprops
    SKIMAGE_AVAILABLE = True
except ImportError:
    SKIMAGE_AVAILABLE = False
    print('[WARNING] scikit-image tidak tersedia, GLCM dinonaktifkan.')


def _sanitize_bbox(img, bbox: list) -> list | None:
    """
    Membersihkan koordinat bounding box agar tetap berada di dalam ukuran gambar.
    """
    if img is None or not bbox:
        return None

    x1, y1, x2, y2 = bbox
    h, w = img.shape[:2]

    x1 = max(0, int(x1))
    y1 = max(0, int(y1))
    x2 = min(w, int(x2))
    y2 = min(h, int(y2))

    if (x2 - x1) < 10 or (y2 - y1) < 10:
        return None

    return [x1, y1, x2, y2]


def _save_static_image(output_dir: str, filename: str, image) -> str | None:
    """
    Menyimpan gambar ke folder upload dan mengembalikan path relatif Flask static.
    Contoh return: uploads/glcm_gray_daun.jpg
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        save_path = os.path.join(output_dir, filename)
        success = cv2.imwrite(save_path, image)

        if not success:
            print(f'[WARNING] GLCM Visual: Gagal menyimpan {save_path}')
            return None

        return f'uploads/{filename}'

    except Exception as e:
        print(f'[WARNING] GLCM Visual save error: {e}')
        return None


def _normalize_to_uint8(image) -> np.ndarray:
    """
    Normalisasi array numerik ke rentang 0-255 uint8.
    """
    normalized = cv2.normalize(image, None, 0, 255, cv2.NORM_MINMAX)
    return normalized.astype(np.uint8)


def _safe_colormap(name: str, fallback=cv2.COLORMAP_JET):
    """
    Mengambil colormap OpenCV dengan fallback agar aman di berbagai versi OpenCV.
    """
    return getattr(cv2, name, fallback)


def analyze_glcm(image_path: str, bbox: list) -> dict | None:
    """
    Analisis tekstur GLCM pada area bounding box.

    Fitur yang digunakan:
        1. kontras
        2. dissimilarity
        3. homogenitas
        4. energi
        5. entropy

    Args:
        image_path : path absolut gambar asli
        bbox       : [x1, y1, x2, y2] koordinat bounding box

    Return dict:
        kontras       : float
        dissimilarity : float
        homogenitas   : float
        energi        : float
        entropy       : float
        bbox          : list [x1, y1, x2, y2]
        status        : 'ok'
    """
    if not SKIMAGE_AVAILABLE:
        return None

    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f'[WARNING] GLCM: Gagal membaca gambar {image_path}')
            return None

        clean_bbox = _sanitize_bbox(img, bbox)
        if not clean_bbox:
            print('[WARNING] GLCM: bbox kosong atau area terlalu kecil')
            return None

        x1, y1, x2, y2 = clean_bbox

        # Crop area bounding box
        crop = img[y1:y2, x1:x2]

        # Konversi ke grayscale
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        # Resize ke 64x64 agar ukuran analisis konsisten
        gray = cv2.resize(gray, (64, 64))

        # Hitung GLCM
        # distances=[1] = jarak 1 piksel
        # angles=[0, π/4, π/2, 3π/4] = 4 arah
        glcm = graycomatrix(
            gray,
            distances=[1],
            angles=[0, np.pi / 4, np.pi / 2, 3 * np.pi / 4],
            levels=256,
            symmetric=True,
            normed=True,
        )

        # Ekstrak 4 fitur dari graycoprops — rata-rata dari 4 arah
        kontras       = float(graycoprops(glcm, 'contrast').mean())
        dissimilarity = float(graycoprops(glcm, 'dissimilarity').mean())
        homogenitas   = float(graycoprops(glcm, 'homogeneity').mean())
        energi        = float(graycoprops(glcm, 'energy').mean())

        # Entropy dihitung manual dari matriks GLCM
        glcm_safe = glcm + 1e-12
        entropy = float(-(glcm_safe * np.log2(glcm_safe)).sum(axis=(0, 1)).mean())

        return {
            'status'       : 'ok',
            'kontras'      : round(kontras,       4),
            'dissimilarity': round(dissimilarity, 4),
            'homogenitas'  : round(homogenitas,   4),
            'energi'       : round(energi,        4),
            'entropy'      : round(entropy,       4),
            'bbox'         : [x1, y1, x2, y2],
        }

    except Exception as e:
        print(f'[WARNING] GLCM error: {e}')
        return None


def save_glcm_crop(image_path: str, bbox: list, output_dir: str) -> str | None:
    """
    Simpan crop area bounding box yang digunakan untuk analisis GLCM.

    Args:
        image_path : path absolut gambar asli
        bbox       : [x1, y1, x2, y2] koordinat bounding box
        output_dir : folder tujuan penyimpanan crop
                     contoh: frontend/static/uploads

    Return:
        path relatif untuk static Flask.
        contoh: uploads/glcm_crop_nama_file.jpg
    """
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f'[WARNING] GLCM Crop: Gagal membaca gambar {image_path}')
            return None

        clean_bbox = _sanitize_bbox(img, bbox)
        if not clean_bbox:
            print('[WARNING] GLCM Crop: bbox kosong atau area terlalu kecil')
            return None

        x1, y1, x2, y2 = clean_bbox
        crop = img[y1:y2, x1:x2]

        base_name = os.path.splitext(os.path.basename(image_path))[0]
        crop_name = f'glcm_crop_{base_name}.jpg'

        return _save_static_image(output_dir, crop_name, crop)

    except Exception as e:
        print(f'[WARNING] GLCM Crop error: {e}')
        return None


def save_glcm_visuals(image_path: str, bbox: list, output_dir: str) -> dict:
    """
    Membuat visualisasi proses GLCM dari area bounding box.

    Visual yang dibuat:
        grayscale        : crop hasil konversi grayscale
        quantized        : grayscale yang disederhanakan level warnanya
        glcm_heatmap     : heatmap matriks co-occurrence
        contrast_map     : visual area dengan perubahan intensitas tinggi
        dissimilarity_map: visual ketidaksamaan antar piksel
        homogeneity_map  : visual area yang lebih seragam
        energy_map       : visual keteraturan tekstur lokal
        entropy_map      : visual kompleksitas tekstur

    Return:
        dict berisi path relatif untuk static Flask.
        contoh:
        {
            'grayscale': 'uploads/glcm_gray_x.jpg',
            'contrast_map': 'uploads/glcm_contrast_x.jpg'
        }
    """
    visuals = {}

    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f'[WARNING] GLCM Visual: Gagal membaca gambar {image_path}')
            return visuals

        clean_bbox = _sanitize_bbox(img, bbox)
        if not clean_bbox:
            print('[WARNING] GLCM Visual: bbox kosong atau area terlalu kecil')
            return visuals

        x1, y1, x2, y2 = clean_bbox
        base_name = os.path.splitext(os.path.basename(image_path))[0]

        crop = img[y1:y2, x1:x2]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)

        # Ukuran visual dibuat lebih besar agar enak dilihat di website.
        gray_visual = cv2.resize(gray, (256, 256), interpolation=cv2.INTER_AREA)

        # 1. Grayscale
        gray_name = f'glcm_gray_{base_name}.jpg'
        gray_rel = _save_static_image(output_dir, gray_name, gray_visual)
        if gray_rel:
            visuals['grayscale'] = gray_rel

        # 2. Quantized gray level
        # GLCM membaca relasi level keabuan. Visual ini menunjukkan level intensitas
        # yang disederhanakan agar perubahan tekstur lebih terlihat.
        levels = 16
        step = 256 // levels
        quantized = ((gray_visual // step) * step).astype(np.uint8)

        quantized_name = f'glcm_quantized_{base_name}.jpg'
        quantized_rel = _save_static_image(output_dir, quantized_name, quantized)
        if quantized_rel:
            visuals['quantized'] = quantized_rel

        # 3. GLCM matrix heatmap
        # Matriks ini menunjukkan seberapa sering pasangan intensitas piksel muncul
        # berdampingan pada arah horizontal.
        q = (gray_visual // step).astype(np.uint8)
        matrix = np.zeros((levels, levels), dtype=np.float32)

        for row in range(q.shape[0]):
            for col in range(q.shape[1] - 1):
                i = int(q[row, col])
                j = int(q[row, col + 1])
                matrix[i, j] += 1
                matrix[j, i] += 1

        if matrix.max() > 0:
            matrix = matrix / matrix.max()

        # Log transform agar nilai kecil tetap terlihat.
        matrix_log = np.log1p(matrix * 255.0)
        matrix_img = _normalize_to_uint8(matrix_log)
        matrix_img = cv2.resize(matrix_img, (256, 256), interpolation=cv2.INTER_NEAREST)
        matrix_img = cv2.applyColorMap(matrix_img, _safe_colormap('COLORMAP_TURBO'))

        matrix_name = f'glcm_matrix_{base_name}.jpg'
        matrix_rel = _save_static_image(output_dir, matrix_name, matrix_img)
        if matrix_rel:
            visuals['glcm_heatmap'] = matrix_rel

        # 4. Contrast map
        # Semakin terang/menyala, semakin besar perubahan intensitas lokal.
        laplacian = cv2.Laplacian(gray_visual, cv2.CV_64F)
        contrast_map = np.absolute(laplacian)
        contrast_map = _normalize_to_uint8(contrast_map)
        contrast_map = cv2.applyColorMap(contrast_map, _safe_colormap('COLORMAP_INFERNO'))

        contrast_name = f'glcm_contrast_{base_name}.jpg'
        contrast_rel = _save_static_image(output_dir, contrast_name, contrast_map)
        if contrast_rel:
            visuals['contrast_map'] = contrast_rel

        # 5. Dissimilarity map
        # Menggunakan perbedaan intensitas dengan piksel tetangga kanan dan bawah.
        shifted_right = np.roll(gray_visual, -1, axis=1)
        shifted_down = np.roll(gray_visual, -1, axis=0)

        diff_right = cv2.absdiff(gray_visual, shifted_right)
        diff_down = cv2.absdiff(gray_visual, shifted_down)
        dissimilarity_map = cv2.addWeighted(diff_right, 0.5, diff_down, 0.5, 0)
        dissimilarity_map = _normalize_to_uint8(dissimilarity_map)
        dissimilarity_map = cv2.applyColorMap(dissimilarity_map, _safe_colormap('COLORMAP_PLASMA'))

        dissimilarity_name = f'glcm_dissimilarity_{base_name}.jpg'
        dissimilarity_rel = _save_static_image(output_dir, dissimilarity_name, dissimilarity_map)
        if dissimilarity_rel:
            visuals['dissimilarity_map'] = dissimilarity_rel

        # 6. Homogeneity map
        # Area halus/seragam dibuat lebih terang.
        blur = cv2.GaussianBlur(gray_visual, (9, 9), 0)
        diff_blur = cv2.absdiff(gray_visual, blur)
        homogeneity_map = 255 - _normalize_to_uint8(diff_blur)
        homogeneity_map = cv2.applyColorMap(homogeneity_map, _safe_colormap('COLORMAP_VIRIDIS'))

        homogeneity_name = f'glcm_homogeneity_{base_name}.jpg'
        homogeneity_rel = _save_static_image(output_dir, homogeneity_name, homogeneity_map)
        if homogeneity_rel:
            visuals['homogeneity_map'] = homogeneity_rel

        # 7. Energy map
        # Pendekatan visual: area dengan deviasi lokal rendah dianggap lebih teratur.
        gray_float = gray_visual.astype(np.float32)
        mean = cv2.GaussianBlur(gray_float, (11, 11), 0)
        mean_sq = cv2.GaussianBlur(gray_float ** 2, (11, 11), 0)
        variance = np.maximum(mean_sq - mean ** 2, 0)
        local_std = np.sqrt(variance)

        energy_map = 255 - _normalize_to_uint8(local_std)
        energy_map = cv2.applyColorMap(energy_map, _safe_colormap('COLORMAP_OCEAN'))

        energy_name = f'glcm_energy_{base_name}.jpg'
        energy_rel = _save_static_image(output_dir, energy_name, energy_map)
        if energy_rel:
            visuals['energy_map'] = energy_rel

        # 8. Entropy map
        # Visual kompleksitas tekstur. Area dengan variasi lokal tinggi dibuat lebih terang.
        entropy_raw = _normalize_to_uint8(local_std)
        entropy_map = cv2.applyColorMap(entropy_raw, _safe_colormap('COLORMAP_MAGMA'))

        entropy_name = f'glcm_entropy_{base_name}.jpg'
        entropy_rel = _save_static_image(output_dir, entropy_name, entropy_map)
        if entropy_rel:
            visuals['entropy_map'] = entropy_rel

        return visuals

    except Exception as e:
        print(f'[WARNING] GLCM Visual error: {e}')
        return visuals


def interpret_glcm(glcm_result: dict) -> dict:
    """
    Interpretasi nilai GLCM menjadi deskripsi tekstual.

    Fitur yang diinterpretasikan:
        1. kontras
        2. dissimilarity
        3. homogenitas
        4. energi
        5. entropy
    """
    if not glcm_result or glcm_result.get('status') != 'ok':
        return {}

    kontras       = glcm_result['kontras']
    dissimilarity = glcm_result['dissimilarity']
    homogenitas   = glcm_result['homogenitas']
    energi        = glcm_result['energi']
    entropy       = glcm_result['entropy']

    # Interpretasi kontras
    if kontras < 50:
        interp_kontras = 'Rendah — tekstur halus dan seragam'
    elif kontras < 200:
        interp_kontras = 'Sedang — tekstur bervariasi'
    else:
        interp_kontras = 'Tinggi — tekstur kasar dan tidak seragam'

    # Interpretasi dissimilarity
    if dissimilarity < 5:
        interp_dissimilarity = 'Rendah — perbedaan antar piksel kecil'
    elif dissimilarity < 15:
        interp_dissimilarity = 'Sedang — terdapat variasi tekstur'
    else:
        interp_dissimilarity = 'Tinggi — tekstur sangat tidak seragam'

    # Interpretasi homogenitas
    if homogenitas > 0.7:
        interp_homogenitas = 'Tinggi — piksel berdekatan sangat mirip'
    elif homogenitas > 0.5:
        interp_homogenitas = 'Sedang — piksel berdekatan cukup mirip'
    else:
        interp_homogenitas = 'Rendah — piksel berdekatan berbeda jauh'

    # Interpretasi energi
    if energi > 0.05:
        interp_energi = 'Tinggi — pola tekstur berulang dan teratur'
    elif energi > 0.02:
        interp_energi = 'Sedang — pola tekstur cukup teratur'
    else:
        interp_energi = 'Rendah — pola tekstur tidak beraturan'

    # Interpretasi entropy
    if entropy < 5:
        interp_entropy = 'Rendah — tekstur sederhana dan teratur'
    elif entropy < 7:
        interp_entropy = 'Sedang — kompleksitas tekstur sedang'
    else:
        interp_entropy = 'Tinggi — tekstur kompleks dan tidak beraturan'

    return {
        'kontras'      : interp_kontras,
        'dissimilarity': interp_dissimilarity,
        'homogenitas'  : interp_homogenitas,
        'energi'       : interp_energi,
        'entropy'      : interp_entropy,
    }