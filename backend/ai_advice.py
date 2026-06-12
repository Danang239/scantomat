import os
import json
import requests

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_URL = 'https://api.groq.com/openai/v1/chat/completions'


def is_ai_enabled() -> bool:
    return bool(GROQ_API_KEY and len(GROQ_API_KEY) > 10)


def _clean_json_response(text: str) -> str:
    """
    Membersihkan respons AI jika dibungkus markdown code block.
    """
    if not text:
        return ''

    text = text.strip()

    if text.startswith('```'):
        parts = text.split('```')
        if len(parts) >= 2:
            text = parts[1].strip()

        if text.startswith('json'):
            text = text[4:].strip()

    return text


def get_ai_advice(disease_name, disease_info):
    if is_ai_enabled():
        result = _call_groq(disease_name, disease_info)
        if result:
            return result

    return _static_advice(disease_info)


def _call_groq(disease_name, disease_info):
    nama_id = disease_info.get('nama_id', disease_name)
    bahaya = disease_info.get('tingkat_bahaya', 'tidak diketahui')
    penyebab = disease_info.get('penyebab', 'tidak diketahui')

    prompt = f"""Kamu adalah ahli pertanian tomat berpengalaman 20 tahun.
Berikan informasi lengkap dalam Bahasa Indonesia untuk penyakit berikut:

Nama Penyakit : {disease_name} ({nama_id})
Penyebab      : {penyebab}
Tingkat Bahaya: {bahaya}

Balas HANYA dengan JSON berikut, tanpa teks lain, tanpa markdown:
{{
  "deskripsi": "1-2 kalimat singkat tentang penyakit ini, maks 30 kata",
  "gejala": [
    "gejala 1",
    "gejala 2",
    "gejala 3",
    "gejala 4"
  ],
  "sections": [
    {{
      "judul": "Tindakan Hari Ini",
      "poin": ["poin 1", "poin 2", "poin 3"]
    }},
    {{
      "judul": "Pengobatan",
      "poin": ["poin 1", "poin 2"]
    }},
    {{
      "judul": "Cegah Penyebaran",
      "poin": ["poin 1", "poin 2"]
    }},
    {{
      "judul": "Tips Pemulihan",
      "poin": ["poin 1", "poin 2"]
    }}
  ]
}}

Setiap gejala dan poin maksimal 15 kata. Bahasa sederhana untuk petani."""

    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': [
            {
                'role': 'system',
                'content': 'Kamu adalah ahli agronomis pertanian tomat Indonesia. Selalu balas dengan JSON valid saja, tanpa penjelasan tambahan.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 700,
        'temperature': 0.3,
    }

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}',
            },
            data=json.dumps(payload),
            timeout=15,
        )

        if resp.status_code == 200:
            text = resp.json()['choices'][0]['message']['content'].strip()
            text = _clean_json_response(text)

            parsed = json.loads(text)
            sections = parsed.get('sections', [])
            deskripsi = parsed.get('deskripsi', '')
            gejala = parsed.get('gejala', [])

            if sections and isinstance(sections, list):
                return {
                    'source': 'ai',
                    'deskripsi': deskripsi,
                    'gejala': gejala,
                    'sections': sections,
                }

        else:
            print(f'[WARNING] Groq API status: {resp.status_code} — {resp.text}')

    except json.JSONDecodeError as e:
        print(f'[WARNING] Groq JSON parse error: {e}')
    except Exception as e:
        print(f'[WARNING] Groq API error: {e}')

    return None


def _static_advice(disease_info):
    items = disease_info.get('penanganan', [])

    if not items:
        items = ['Konsultasikan dengan penyuluh pertanian setempat.']

    return {
        'source': 'static',
        'deskripsi': None,
        'gejala': None,
        'sections': [
            {
                'judul': 'Saran Penanganan',
                'poin': items
            }
        ],
    }


def _glcm_level(feature_name: str, value) -> str:
    """
    Menentukan level fitur GLCM agar AI tidak menebak-nebak.
    """
    try:
        v = float(value)
    except Exception:
        return 'tidak diketahui'

    feature_name = feature_name.lower()

    if feature_name == 'kontras':
        if v < 50:
            return 'rendah'
        if v < 200:
            return 'sedang'
        return 'tinggi'

    if feature_name == 'dissimilarity':
        if v < 5:
            return 'rendah'
        if v < 15:
            return 'sedang'
        return 'tinggi'

    if feature_name == 'homogenitas':
        if v > 0.7:
            return 'tinggi'
        if v > 0.5:
            return 'sedang'
        return 'rendah'

    if feature_name == 'energi':
        if v > 0.05:
            return 'tinggi'
        if v > 0.02:
            return 'sedang'
        return 'rendah'

    if feature_name == 'entropy':
        if v < 5:
            return 'rendah'
        if v < 7:
            return 'sedang'
        return 'tinggi'

    return 'terukur'


def get_ai_glcm_summary(disease_name, disease_info, glcm_result, glcm_interp=None):
    """
    Membuat kesimpulan analisis tekstur GLCM.

    Catatan penting:
    - GLCM tetap dihitung oleh program melalui OpenCV + scikit-image.
    - AI hanya digunakan untuk membuat narasi kesimpulan dari hasil GLCM.
    - Fitur yang digunakan hanya 5:
      kontras, dissimilarity, homogenitas, energi, entropy.
    """
    if not glcm_result or glcm_result.get('status') != 'ok':
        return {
            'source': 'none',
            'summary': 'Kesimpulan GLCM tidak tersedia karena hasil analisis tekstur tidak berhasil dihitung.',
            'points': []
        }

    if is_ai_enabled():
        result = _call_groq_glcm_summary(disease_name, disease_info, glcm_result, glcm_interp)
        if result:
            return result

    return _static_glcm_summary(glcm_result, glcm_interp)


def _call_groq_glcm_summary(disease_name, disease_info, glcm_result, glcm_interp=None):
    """
    Meminta AI membuat kesimpulan yang benar-benar fokus pada angka GLCM.
    AI tidak boleh membuat diagnosis baru dan tidak boleh menjawab terlalu umum.
    """
    nama_id = disease_info.get('nama_id', disease_name)

    kontras = glcm_result.get('kontras', 0)
    dissimilarity = glcm_result.get('dissimilarity', 0)
    homogenitas = glcm_result.get('homogenitas', 0)
    energi = glcm_result.get('energi', 0)
    entropy = glcm_result.get('entropy', 0)

    level_kontras = _glcm_level('kontras', kontras)
    level_dissimilarity = _glcm_level('dissimilarity', dissimilarity)
    level_homogenitas = _glcm_level('homogenitas', homogenitas)
    level_energi = _glcm_level('energi', energi)
    level_entropy = _glcm_level('entropy', entropy)

    interp_kontras = ''
    interp_dissimilarity = ''
    interp_homogenitas = ''
    interp_energi = ''
    interp_entropy = ''

    if glcm_interp and isinstance(glcm_interp, dict):
        interp_kontras = glcm_interp.get('kontras', '')
        interp_dissimilarity = glcm_interp.get('dissimilarity', '')
        interp_homogenitas = glcm_interp.get('homogenitas', '')
        interp_energi = glcm_interp.get('energi', '')
        interp_entropy = glcm_interp.get('entropy', '')

    prompt = f"""Kamu adalah asisten analisis citra yang menjelaskan hasil fitur GLCM.
Tugasmu hanya menyimpulkan tekstur berdasarkan ANGKA GLCM, bukan membuat diagnosis penyakit baru.

Hasil deteksi YOLOv8:
- Kelas terdeteksi: {disease_name} ({nama_id})

Nilai fitur GLCM yang wajib dibahas:
1. Kontras = {kontras}
   Level: {level_kontras}
   Interpretasi lokal: {interp_kontras}

2. Dissimilarity = {dissimilarity}
   Level: {level_dissimilarity}
   Interpretasi lokal: {interp_dissimilarity}

3. Homogenitas = {homogenitas}
   Level: {level_homogenitas}
   Interpretasi lokal: {interp_homogenitas}

4. Energi = {energi}
   Level: {level_energi}
   Interpretasi lokal: {interp_energi}

5. Entropy = {entropy}
   Level: {level_entropy}
   Interpretasi lokal: {interp_entropy}

Aturan wajib:
- Fokus pada nilai GLCM, bukan pada nama penyakit.
- Wajib menyebut minimal 3 nilai angka GLCM secara eksplisit.
- Jangan membuat diagnosis baru.
- Jangan mengatakan "mendukung diagnosis" jika tidak perlu.
- Jangan pakai kalimat template umum.
- Jelaskan hubungan antar nilai, misalnya kontras tinggi + homogenitas rendah + entropy tinggi.
- Jika ada nilai yang saling berbeda, jelaskan secara seimbang.
- Gunakan Bahasa Indonesia sederhana.
- Maksimal 4 kalimat untuk summary.
- points harus berupa 3 poin yang spesifik berdasarkan nilai.
- Jangan gunakan markdown.
- Balas hanya JSON valid.

Format JSON:
{{
  "summary": "kesimpulan spesifik berdasarkan angka GLCM, 3 sampai 4 kalimat",
  "points": [
    "poin spesifik 1 berdasarkan angka",
    "poin spesifik 2 berdasarkan angka",
    "poin spesifik 3 berdasarkan angka"
  ]
}}"""

    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': [
            {
                'role': 'system',
                'content': (
                    'Kamu adalah asisten analisis citra pertanian. '
                    'Balas hanya JSON valid. Fokus pada angka GLCM. '
                    'Jangan membuat diagnosis baru dan jangan menjawab dengan kalimat umum.'
                )
            },
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 500,
        'temperature': 0.15,
    }

    try:
        resp = requests.post(
            GROQ_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}',
            },
            data=json.dumps(payload),
            timeout=15,
        )

        if resp.status_code == 200:
            text = resp.json()['choices'][0]['message']['content'].strip()
            text = _clean_json_response(text)

            parsed = json.loads(text)
            summary = parsed.get('summary', '')
            points = parsed.get('points', [])

            if summary:
                if not isinstance(points, list):
                    points = []

                return {
                    'source': 'ai',
                    'summary': summary,
                    'points': points[:3],
                }

        else:
            print(f'[WARNING] Groq GLCM summary status: {resp.status_code} — {resp.text}')

    except json.JSONDecodeError as e:
        print(f'[WARNING] Groq GLCM summary JSON parse error: {e}')
    except Exception as e:
        print(f'[WARNING] Groq GLCM summary error: {e}')

    return None


def _static_glcm_summary(glcm_result, glcm_interp=None):
    """
    Fallback kesimpulan lokal jika AI tidak aktif/error.
    Tetap memakai 5 fitur GLCM utama dan menyebut angka agar tidak terasa template.
    """
    kontras = float(glcm_result.get('kontras', 0))
    dissimilarity = float(glcm_result.get('dissimilarity', 0))
    homogenitas = float(glcm_result.get('homogenitas', 0))
    energi = float(glcm_result.get('energi', 0))
    entropy = float(glcm_result.get('entropy', 0))

    level_kontras = _glcm_level('kontras', kontras)
    level_dissimilarity = _glcm_level('dissimilarity', dissimilarity)
    level_homogenitas = _glcm_level('homogenitas', homogenitas)
    level_energi = _glcm_level('energi', energi)
    level_entropy = _glcm_level('entropy', entropy)

    summary = (
        f'Berdasarkan nilai GLCM, kontras sebesar {kontras} berada pada level {level_kontras}, '
        f'sedangkan dissimilarity sebesar {dissimilarity} berada pada level {level_dissimilarity}. '
        f'Homogenitas sebesar {homogenitas} menunjukkan tingkat keseragaman tekstur yang {level_homogenitas}, '
        f'dan energi sebesar {energi} menunjukkan keteraturan pola yang {level_energi}. '
        f'Entropy sebesar {entropy} berada pada level {level_entropy}, sehingga karakter tekstur utama '
        'dapat dibaca dari kombinasi perbedaan intensitas, keseragaman, keteraturan, dan kompleksitas tekstur.'
    )

    return {
        'source': 'static',
        'summary': summary,
        'points': [
            f'Kontras {level_kontras}: {kontras}',
            f'Homogenitas {level_homogenitas}: {homogenitas}',
            f'Entropy {level_entropy}: {entropy}',
        ],
    }