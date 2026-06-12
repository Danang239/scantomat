import os
import io
import json
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from werkzeug.utils import secure_filename
from predictor import predict_image
from disease_info import get_disease_info
from ai_advice import get_ai_advice, get_ai_glcm_summary, is_ai_enabled
from pdf_generator import generate_pdf
from glcm_analyzer import (
    analyze_glcm,
    interpret_glcm,
    save_glcm_crop,
    save_glcm_visuals,
)
import requests as http_requests

BASE_DIR      = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, '..', 'frontend', 'static', 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
GROQ_URL     = 'https://api.groq.com/openai/v1/chat/completions'

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, '..', 'frontend', 'templates'),
    static_folder=os.path.join(BASE_DIR, '..', 'frontend', 'static'),
)
app.config['UPLOAD_FOLDER']      = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.secret_key = os.environ.get('SECRET_KEY', 'tomatoscan-dev-secret-key')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def safe_json_loads(value, default=None):
    """
    Membaca JSON dari hidden input form dengan aman.
    Dipakai untuk membawa hasil GLCM dari result.html ke download-pdf.
    """
    if default is None:
        default = {}

    if not value:
        return default

    try:
        return json.loads(value)
    except Exception as e:
        print(f"[WARNING] Gagal membaca JSON form: {e}")
        return default


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/history')
def history():
    return render_template('history.html')


@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return redirect(url_for('index'))

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error="Tidak ada file yang dipilih.")

    if not allowed_file(file.filename):
        return render_template('index.html', error="Format tidak didukung. Gunakan JPG, PNG, atau WEBP.")

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        result = predict_image(filepath)
    except Exception as e:
        return render_template('result.html', error=f"Gagal memproses gambar: {str(e)}")

    if result is None:
        return render_template(
            'result.html',
            error="Model belum tersedia. Pastikan file model/best.pt sudah ada."
        )

    disease_name = result['class_name']
    confidence   = round(min(max(result['confidence'] * 100, 0), 100), 1)
    info         = get_disease_info(disease_name)
    advice       = get_ai_advice(disease_name, info)
    ai_active    = advice.get('source') == 'ai'

    # Peringatan jika confidence rendah
    low_confidence = confidence < 70.0

    # Override deskripsi & gejala dengan hasil AI jika tersedia
    if ai_active:
        if advice.get('deskripsi'):
            info['deskripsi'] = advice['deskripsi']
        if advice.get('gejala') and len(advice['gejala']) > 0:
            info['gejala'] = advice['gejala']

    # Analisis GLCM
    glcm_result = None
    glcm_interp = None
    glcm_crop_url = None
    glcm_crop_path = None
    glcm_visuals = {}
    glcm_summary = None

    if result.get('bbox'):
        glcm_result = analyze_glcm(filepath, result['bbox'])

        # Simpan crop area bounding box yang digunakan untuk analisis GLCM
        glcm_crop_rel = save_glcm_crop(filepath, result['bbox'], UPLOAD_FOLDER)
        if glcm_crop_rel:
            glcm_crop_url = url_for('static', filename=glcm_crop_rel)
            glcm_crop_path = os.path.join(app.static_folder, glcm_crop_rel)

        # Simpan visualisasi proses GLCM
        # Output visual mengikuti fungsi save_glcm_visuals()
        # Contoh: grayscale, quantized, glcm_heatmap, contrast_map,
        # dissimilarity_map, homogeneity_map, energy_map, entropy_map
        glcm_visuals_rel = save_glcm_visuals(filepath, result['bbox'], UPLOAD_FOLDER)

        if glcm_visuals_rel:
            glcm_visuals = {
                key: url_for('static', filename=rel_path)
                for key, rel_path in glcm_visuals_rel.items()
            }

        if glcm_result:
            glcm_interp = interpret_glcm(glcm_result)

            # Kesimpulan AI GLCM
            # Catatan:
            # - GLCM tetap dihitung oleh program.
            # - AI hanya membuat narasi kesimpulan dari 5 fitur GLCM.
            glcm_summary = get_ai_glcm_summary(
                disease_name=disease_name,
                disease_info=info,
                glcm_result=glcm_result,
                glcm_interp=glcm_interp,
            )

            print(f"[DEBUG] GLCM kontras      : {glcm_result.get('kontras', '-')}")
            print(f"[DEBUG] GLCM dissimilarity: {glcm_result.get('dissimilarity', '-')}")
            print(f"[DEBUG] GLCM homogenitas  : {glcm_result.get('homogenitas', '-')}")
            print(f"[DEBUG] GLCM energi       : {glcm_result.get('energi', '-')}")
            print(f"[DEBUG] GLCM entropy      : {glcm_result.get('entropy', '-')}")
            print(f"[DEBUG] GLCM crop url     : {glcm_crop_url}")
            print(f"[DEBUG] GLCM crop path    : {glcm_crop_path}")
            print(f"[DEBUG] GLCM visuals      : {list(glcm_visuals.keys())}")
            print(f"[DEBUG] GLCM summary     : {glcm_summary.get('source') if glcm_summary else 'tidak tersedia'}")
    else:
        print(f"[DEBUG] GLCM      : tidak tersedia (bbox kosong)")

    original_url = url_for('static', filename=f'uploads/{filename}')

    if result.get('result_image'):
        result_image_url = url_for('static', filename=result['result_image'])
    else:
        result_image_url = original_url

    base_name       = os.path.splitext(filename)[0]
    result_img_path = os.path.join(UPLOAD_FOLDER, f"result_{base_name}.jpg")
    if not os.path.exists(result_img_path):
        result_img_path = filepath

    print(f"[DEBUG] class          : {disease_name}")
    print(f"[DEBUG] confidence     : {confidence}%")
    print(f"[DEBUG] low_confidence : {low_confidence}")
    print(f"[DEBUG] AI active      : {ai_active}")
    print(f"[DEBUG] result img     : {result_image_url}")
    print(f"[DEBUG] result img path: {result_img_path}")
    print(f"[DEBUG] GLCM           : {'ok' if glcm_result else 'tidak tersedia'}")
    print(f"[DEBUG] GLCM crop url  : {glcm_crop_url}")
    print(f"[DEBUG] GLCM crop path : {glcm_crop_path}")
    print(f"[DEBUG] GLCM visuals   : {glcm_visuals}")
    print(f"[DEBUG] GLCM summary   : {glcm_summary}")

    return render_template(
        'result.html',
        disease_name    = disease_name,
        disease_name_id = info.get('nama_id', disease_name),
        confidence      = confidence,
        low_confidence  = low_confidence,
        info            = info,
        advice          = advice,
        ai_active       = ai_active,
        image_url       = result_image_url,
        original_url    = original_url,
        image_path      = result_img_path,
        glcm_result     = glcm_result,
        glcm_interp     = glcm_interp,
        glcm_crop_url   = glcm_crop_url,
        glcm_crop_path  = glcm_crop_path,
        glcm_visuals    = glcm_visuals,
        glcm_summary    = glcm_summary,
    )


@app.route('/chat', methods=['POST'])
def chat():
    data            = request.get_json()
    user_message    = data.get('message', '').strip()
    disease_name    = data.get('disease_name', '')
    disease_name_id = data.get('disease_name_id', '')
    tingkat_bahaya  = data.get('tingkat_bahaya', '')
    penyebab        = data.get('penyebab', '')
    history         = data.get('history', [])

    if not user_message:
        return jsonify({'error': 'Pesan kosong'}), 400

    if not GROQ_API_KEY or len(GROQ_API_KEY) < 10:
        return jsonify({'reply': 'Maaf, fitur chat tidak tersedia karena API key tidak dikonfigurasi.'}), 200

    system_prompt = f"""Kamu adalah asisten pertanian TomatoScan yang membantu petani memahami penyakit tanaman tomat.

Konteks deteksi saat ini:
- Penyakit terdeteksi : {disease_name} ({disease_name_id})
- Tingkat bahaya      : {tingkat_bahaya}
- Penyebab            : {penyebab}

Aturan menjawab:
- Jawab dalam Bahasa Indonesia yang sederhana dan mudah dipahami petani
- Fokus pada topik penyakit tomat dan pertanian
- Jawaban singkat dan praktis, maksimal 4-5 kalimat
- Jika ditanya di luar topik pertanian tomat, arahkan kembali ke topik penyakit yang terdeteksi
- Jangan gunakan markdown, bullet point, atau formatting khusus"""

    messages = [{'role': 'system', 'content': system_prompt}]

    for msg in history[-6:]:
        messages.append({
            'role': msg.get('role', 'user'),
            'content': msg.get('content', '')
        })

    messages.append({'role': 'user', 'content': user_message})

    payload = {
        'model': 'llama-3.1-8b-instant',
        'messages': messages,
        'max_tokens': 300,
        'temperature': 0.5,
    }

    try:
        resp = http_requests.post(
            GROQ_URL,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {GROQ_API_KEY}',
            },
            data=json.dumps(payload),
            timeout=15,
        )

        if resp.status_code == 200:
            reply = resp.json()['choices'][0]['message']['content'].strip()
            return jsonify({'reply': reply})

        print(f'[WARNING] Chat Groq status: {resp.status_code}')
        return jsonify({'reply': 'Maaf, terjadi kesalahan pada server AI. Coba lagi.'}), 200

    except Exception as e:
        print(f'[WARNING] Chat error: {e}')
        return jsonify({'reply': 'Maaf, tidak dapat terhubung ke AI saat ini.'}), 200


@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    disease_name    = request.form.get('disease_name', '')
    disease_name_id = request.form.get('disease_name_id', '')
    confidence      = float(request.form.get('confidence', 0))
    image_path      = request.form.get('image_path', '')
    ai_active       = request.form.get('ai_active', 'false') == 'true'

    # Data GLCM dikirim dari result.html melalui hidden input
    glcm_result_json  = request.form.get('glcm_result_json', '')
    glcm_interp_json  = request.form.get('glcm_interp_json', '')
    glcm_summary_json = request.form.get('glcm_summary_json', '')
    glcm_crop_path    = request.form.get('glcm_crop_path', '')

    glcm_result  = safe_json_loads(glcm_result_json, default=None)
    glcm_interp  = safe_json_loads(glcm_interp_json, default=None)
    glcm_summary = safe_json_loads(glcm_summary_json, default=None)

    if not glcm_result or not isinstance(glcm_result, dict):
        glcm_result = None

    if not glcm_interp or not isinstance(glcm_interp, dict):
        glcm_interp = None

    if not glcm_summary or not isinstance(glcm_summary, dict):
        glcm_summary = None

    if not glcm_crop_path or not os.path.exists(glcm_crop_path):
        glcm_crop_path = None

    info   = get_disease_info(disease_name)
    advice = get_ai_advice(disease_name, info)

    if advice.get('source') == 'ai':
        if advice.get('deskripsi'):
            info['deskripsi'] = advice['deskripsi']
        if advice.get('gejala') and len(advice['gejala']) > 0:
            info['gejala'] = advice['gejala']

    print(f"[DEBUG] PDF disease       : {disease_name}")
    print(f"[DEBUG] PDF image path    : {image_path}")
    print(f"[DEBUG] PDF GLCM          : {'ok' if glcm_result else 'tidak tersedia'}")
    print(f"[DEBUG] PDF GLCM summary  : {glcm_summary.get('source') if glcm_summary else 'tidak tersedia'}")
    print(f"[DEBUG] PDF GLCM crop path: {glcm_crop_path}")

    pdf_bytes = generate_pdf(
        disease_name    = disease_name,
        disease_name_id = disease_name_id,
        confidence      = confidence,
        info            = info,
        advice          = advice,
        ai_active       = ai_active,
        image_path      = image_path if os.path.exists(image_path) else None,
        glcm_result     = glcm_result,
        glcm_interp     = glcm_interp,
        glcm_crop_path  = glcm_crop_path,
        glcm_summary    = glcm_summary,
    )

    filename_pdf = f"TomatoScan_{disease_name_id.replace(' ', '_')}.pdf"
    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename_pdf,
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(413)
def file_too_large(e):
    return render_template('index.html', error="File terlalu besar. Maksimal 16MB."), 413


if __name__ == '__main__':
    print("=" * 50)
    print("🍅  TomatoScan — Deteksi Penyakit Daun Tomat")
    print(f"   AI Advice : {'✅ Aktif (Groq)' if is_ai_enabled() else '⚠️  Nonaktif'}")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)