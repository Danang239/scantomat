DISEASE_DATABASE = {

    # ── 0 ──────────────────────────────────────────────────────
    'Tomato Bacterial Spot': {
        'nama_id':        'Bercak Bakteri',
        'penyebab':       'Bakteri Xanthomonas campestris pv. vesicatoria',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🦠',
        'deskripsi':
            'Penyakit bakterial yang sangat umum pada cuaca lembap dan hangat. '
            'Dapat menyerang daun, batang, maupun buah tomat secara bersamaan.',
        'gejala': [
            'Bercak kecil coklat tua hingga hitam pada permukaan daun',
            'Tepi bercak dikelilingi lingkaran kuning (halo)',
            'Pada serangan parah, daun menguning lalu rontok',
            'Buah dapat memiliki bercak kasar berwarna coklat',
        ],
        'penanganan': [
            'Semprotkan bakterisida berbahan dasar tembaga (copper hydroxide)',
            'Hindari penyiraman dari atas agar air tidak memercik ke daun',
            'Singkirkan dan musnahkan daun yang terinfeksi segera',
            'Lakukan rotasi tanaman setiap musim tanam',
            'Gunakan benih bersertifikat bebas penyakit',
        ],
    },

    # ── 1 ──────────────────────────────────────────────────────
    'Tomato Early blight': {
        'nama_id':        'Hawar Awal',
        'penyebab':       'Jamur Alternaria solani',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🍂',
        'deskripsi':
            'Penyakit jamur yang muncul pada daun tua terlebih dahulu, '
            'kemudian menyebar ke atas. Berkembang pesat pada cuaca lembap '
            'dengan suhu 24–29°C.',
        'gejala': [
            'Bercak coklat gelap dengan pola cincin konsentris seperti papan target',
            'Jaringan kuning di sekeliling bercak',
            'Daun bagian bawah terinfeksi terlebih dahulu',
            'Daun menguning total lalu rontok',
        ],
        'penanganan': [
            'Semprotkan fungisida klorotalonil atau mankozeb setiap 7–10 hari',
            'Pasang mulsa di sekitar batang untuk mengurangi percikan tanah',
            'Pangkas dan buang daun bawah yang terinfeksi',
            'Jaga jarak tanam cukup untuk sirkulasi udara',
            'Hindari menyiram pada sore atau malam hari',
        ],
    },

    # ── 2 ──────────────────────────────────────────────────────
    'Tomato Late blight': {
        'nama_id':        'Hawar Daun Akhir',
        'penyebab':       'Oomycete Phytophthora infestans',
        'tingkat_bahaya': 'Tinggi',
        'emoji':          '⚠️',
        'deskripsi':
            'Penyakit paling destruktif pada tomat. Menyebar sangat cepat '
            'pada kondisi dingin dan basah. Dapat menghancurkan seluruh lahan '
            'dalam hitungan hari jika tidak segera ditangani.',
        'gejala': [
            'Bercak basah berwarna hijau abu-abu hingga coklat gelap',
            'Lapisan jamur putih di bawah daun saat kondisi lembap',
            'Daun cepat membusuk seolah terbakar',
            'Menyerang batang dan buah dalam waktu singkat',
        ],
        'penanganan': [
            'Semprot fungisida sistemik berbahan metalaksil SEGERA',
            'Singkirkan seluruh bagian tanaman yang terinfeksi dan bakar',
            'Hindari kelembapan berlebih, perbaiki drainase lahan',
            'Laporkan ke penyuluh pertanian jika serangan meluas',
            'Gunakan varietas tomat tahan Late Blight musim berikutnya',
        ],
    },

    # ── 3 ──────────────────────────────────────────────────────
    'Tomato Leaf Mold': {
        'nama_id':        'Jamur Daun',
        'penyebab':       'Jamur Fulvia fulva (Cladosporium fulvum)',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🌿',
        'deskripsi':
            'Penyakit jamur yang umum pada kelembapan tinggi di atas 85%, '
            'terutama dalam greenhouse atau area dengan naungan rapat.',
        'gejala': [
            'Bercak kuning pucat di permukaan atas daun',
            'Lapisan jamur beludru hijau-abu di bawah daun',
            'Daun menggulung ke atas lalu mengering',
            'Menyebar dari daun bawah ke atas secara bertahap',
        ],
        'penanganan': [
            'Kurangi kelembapan dengan meningkatkan ventilasi area tanam',
            'Semprot fungisida berbahan tembaga atau mankozeb',
            'Hindari penyiraman malam hari',
            'Pangkas daun yang terinfeksi dan buang jauh dari lahan',
            'Gunakan varietas tomat tahan jamur daun',
        ],
    },

    # ── 4 ──────────────────────────────────────────────────────
    'Tomato Septoria leaf spot': {
        'nama_id':        'Bercak Septoria',
        'penyebab':       'Jamur Septoria lycopersici',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🔵',
        'deskripsi':
            'Penyakit jamur yang sangat umum. Spora menyebar dari tanah ke '
            'daun bawah melalui percikan air hujan atau irigasi.',
        'gejala': [
            'Bercak kecil melingkar: tepi coklat, tengah abu-abu atau putih',
            'Titik gelap kecil di pusat bercak (badan buah jamur)',
            'Daun menguning di sekitar bercak',
            'Daun rontok dari bawah ke atas secara bertahap',
        ],
        'penanganan': [
            'Semprot fungisida klorotalonil, mankozeb, atau tembaga',
            'Singkirkan dan buang jauh semua daun yang terinfeksi',
            'Pasang mulsa tebal di sekitar batang',
            'Hindari kelembapan berlebih pada kanopi daun',
            'Jaga jarak tanam agar sirkulasi udara baik',
        ],
    },

    # ── 5 ──────────────────────────────────────────────────────
    'Tomato Spider mites Two-spotted spider mite': {
        'nama_id':        'Tungau Laba-laba',
        'penyebab':       'Tungau Tetranychus urticae',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🕷️',
        'deskripsi':
            'Hama berupa tungau sangat kecil kurang dari 1 mm. '
            'Berkembang sangat pesat pada kondisi panas dan kering.',
        'gejala': [
            'Titik-titik putih atau kuning (stippling) di permukaan atas daun',
            'Jaring halus di bawah daun atau di antara daun',
            'Daun tampak pucat, kecoklatan, lalu mengering',
            'Tungau merah atau coklat kecil terlihat dengan kaca pembesar',
        ],
        'penanganan': [
            'Semprot air kuat ke bawah daun untuk membersihkan tungau',
            'Gunakan mitisida atau sabun insektisida berbahan minyak neem',
            'Tingkatkan kelembapan udara di sekitar tanaman',
            'Lepaskan predator alami Phytoseiulus persimilis jika tersedia',
            'Rotasi jenis pestisida untuk mencegah resistensi tungau',
        ],
    },

    # ── 6 ──────────────────────────────────────────────────────
    'Tomato Target Spot': {
        'nama_id':        'Bercak Target',
        'penyebab':       'Jamur Corynespora cassiicola',
        'tingkat_bahaya': 'Sedang',
        'emoji':          '🎯',
        'deskripsi':
            'Penyakit jamur yang menyerang daun, batang, dan buah. '
            'Berkembang pada suhu 24–30°C dengan kelembapan tinggi.',
        'gejala': [
            'Bercak coklat dengan lingkaran konsentris seperti sasaran tembak',
            'Halo kuning di sekeliling bercak',
            'Bercak bergabung membentuk area nekrotik luas',
            'Buah dapat memiliki cekungan berwarna coklat',
        ],
        'penanganan': [
            'Gunakan fungisida azoxystrobin atau difenoconazole',
            'Hindari penyiraman sore atau malam hari',
            'Pastikan jarak tanam cukup untuk sirkulasi udara',
            'Bersihkan sisa tanaman setelah panen',
            'Rotasi tanaman untuk memutus siklus hidup jamur',
        ],
    },

    # ── 7 ──────────────────────────────────────────────────────
    'Tomato Yellow Leaf Curl Virus': {
        'nama_id':        'Virus Keriting Kuning',
        'penyebab':       'Tomato Yellow Leaf Curl Virus (TYLCV) via kutu kebul',
        'tingkat_bahaya': 'Tinggi',
        'emoji':          '🌀',
        'deskripsi':
            'Penyakit virus yang ditularkan oleh kutu kebul (Bemisia tabaci). '
            'Satu serangan dapat menghancurkan seluruh lahan jika vektor '
            'tidak dikendalikan dengan cepat.',
        'gejala': [
            'Daun muda menggulung ke atas dan menguning di pinggir',
            'Daun baru mengecil dan terlihat kerdil',
            'Tanaman tumbuh tegak berlebihan',
            'Produksi buah sangat berkurang atau berhenti sama sekali',
        ],
        'penanganan': [
            'Tidak ada obat — kendalikan populasi kutu kebul SEGERA',
            'Gunakan insektisida sistemik imidakloprid untuk kutu kebul',
            'Pasang perangkap kuning lengket untuk monitoring',
            'Cabut dan bakar tanaman terinfeksi agar tidak jadi sumber virus',
            'Gunakan varietas tomat tahan TYLCV musim berikutnya',
        ],
    },

    # ── 8 ──────────────────────────────────────────────────────
    'Tomato healthy': {
        'nama_id':        'Daun Sehat',
        'penyebab':       None,
        'tingkat_bahaya': 'Sehat',
        'emoji':          '✅',
        'deskripsi':
            'Tanaman tomat dalam kondisi prima. Tidak ditemukan tanda-tanda '
            'infeksi penyakit maupun serangan hama.',
        'gejala': [
            'Daun berwarna hijau cerah dan segar',
            'Tidak ada bercak, perubahan warna, atau deformasi',
            'Tekstur dan ukuran daun normal sesuai fase pertumbuhan',
        ],
        'penanganan': [
            'Pertahankan jadwal penyiraman yang teratur',
            'Berikan pupuk NPK sesuai fase pertumbuhan',
            'Lakukan pemantauan visual setiap minggu',
            'Jaga kebersihan area di sekitar tanaman',
            'Lakukan pencegahan preventif dengan fungisida ringan',
        ],
    },

    # ── 9 ──────────────────────────────────────────────────────
    'Tomato mosaic virus': {
        'nama_id':        'Virus Mosaik',
        'penyebab':       'Tomato Mosaic Virus (ToMV)',
        'tingkat_bahaya': 'Tinggi',
        'emoji':          '🧬',
        'deskripsi':
            'Penyakit virus yang ditularkan melalui kontak langsung dan '
            'alat berkebun yang terkontaminasi. Tidak ada obat kimiawi '
            'yang efektif setelah tanaman terinfeksi.',
        'gejala': [
            'Pola mosaik belang-belang kuning-hijau pada daun muda',
            'Daun mengkerut, menggulung, dan bergelombang tidak normal',
            'Pertumbuhan tanaman sangat terhambat (kerdil)',
            'Buah mengecil dan terdapat bercak kuning',
        ],
        'penanganan': [
            'Tidak ada obat — cabut dan bakar tanaman yang terinfeksi segera',
            'Sterilkan semua alat berkebun dengan larutan pemutih 10%',
            'Kendalikan populasi kutu daun sebagai vektor penular',
            'Gunakan hanya benih bersertifikat bebas virus',
            'Cuci tangan sebelum menyentuh tanaman sehat setelah memegang yang sakit',
        ],
    },
}

# ── ALIAS MAPPING ──────────────────────────────────────────────
# Mapping semua variasi nama dari output model YOLO ke key database
_ALIASES = {
    # Exact dari YOLO output (kemungkinan tanpa prefix Tomato)
    'Bacterial Spot':                           'Tomato Bacterial Spot',
    'Early Blight':                             'Tomato Early blight',
    'Early blight':                             'Tomato Early blight',
    'Late Blight':                              'Tomato Late blight',
    'Late blight':                              'Tomato Late blight',
    'Leaf Mold':                                'Tomato Leaf Mold',
    'Leaf mold':                                'Tomato Leaf Mold',
    'Septoria leaf spot':                       'Tomato Septoria leaf spot',
    'Septoria Leaf Spot':                       'Tomato Septoria leaf spot',
    'Spider mites Two-spotted spider mite':     'Tomato Spider mites Two-spotted spider mite',
    'Spider Mites':                             'Tomato Spider mites Two-spotted spider mite',
    'Spider mites':                             'Tomato Spider mites Two-spotted spider mite',
    'Target Spot':                              'Tomato Target Spot',
    'Target spot':                              'Tomato Target Spot',
    'Yellow Leaf Curl Virus':                   'Tomato Yellow Leaf Curl Virus',
    'Tomato Yellow Leaf Curl Virus':            'Tomato Yellow Leaf Curl Virus',
    'healthy':                                  'Tomato healthy',
    'Healthy':                                  'Tomato healthy',
    'mosaic virus':                             'Tomato mosaic virus',
    'Mosaic Virus':                             'Tomato mosaic virus',
    'Mosaic virus':                             'Tomato mosaic virus',
    # Underscore variants
    'Bacterial_Spot':                           'Tomato Bacterial Spot',
    'Early_Blight':                             'Tomato Early blight',
    'Late_Blight':                              'Tomato Late blight',
    'Late_blight':                              'Tomato Late blight',
    'Leaf_Mold':                                'Tomato Leaf Mold',
    'Target_Spot':                              'Tomato Target Spot',
    'Yellow_Leaf_Curl_Virus':                   'Tomato Yellow Leaf Curl Virus',
    'Mosaic_Virus':                             'Tomato mosaic virus',
    'Spider_Mites':                             'Tomato Spider mites Two-spotted spider mite',
}


def get_disease_info(class_name: str) -> dict:
    """
    Ambil info penyakit berdasarkan nama kelas dari output YOLO.
    Urutan pencocokan:
    1. Exact match ke database
    2. Alias mapping
    3. Case-insensitive match
    4. Default fallback
    """
    # 1. Exact match
    if class_name in DISEASE_DATABASE:
        return DISEASE_DATABASE[class_name]

    # 2. Alias mapping
    if class_name in _ALIASES:
        return DISEASE_DATABASE[_ALIASES[class_name]]

    # 3. Case-insensitive + strip
    normalized = class_name.strip().lower()
    for key in DISEASE_DATABASE:
        if key.lower() == normalized:
            return DISEASE_DATABASE[key]
    for alias, target in _ALIASES.items():
        if alias.lower() == normalized:
            return DISEASE_DATABASE[target]

    # 4. Default fallback
    return {
        'nama_id':        class_name,
        'penyebab':       'Tidak diketahui',
        'tingkat_bahaya': 'Tidak diketahui',
        'emoji':          '❓',
        'deskripsi':      'Informasi untuk penyakit ini belum tersedia dalam database.',
        'gejala':         ['Konsultasikan dengan ahli pertanian untuk identifikasi lebih lanjut.'],
        'penanganan':     ['Konsultasikan dengan penyuluh pertanian setempat.'],
    }