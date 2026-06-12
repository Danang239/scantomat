"""
TomatoScan v2 — Generator PDF Hasil Deteksi
"""

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image as RLImage
)

COLOR_GREEN_DARK   = colors.HexColor('#1A3C2E')
COLOR_GREEN_MID    = colors.HexColor('#2D7A52')
COLOR_GREEN_LIGHT  = colors.HexColor('#E8F5EE')
COLOR_GREEN_BORDER = colors.HexColor('#C8E6D4')
COLOR_RED          = colors.HexColor('#C0392B')
COLOR_RED_LIGHT    = colors.HexColor('#FEE2E2')
COLOR_AMBER        = colors.HexColor('#B45309')
COLOR_AMBER_LIGHT  = colors.HexColor('#FEF3C7')
COLOR_BG           = colors.HexColor('#F7F5F0')
COLOR_TEXT         = colors.HexColor('#1A1916')
COLOR_TEXT_MUTED   = colors.HexColor('#706D65')
COLOR_BORDER       = colors.HexColor('#E4E0D8')
COLOR_WHITE        = colors.white
COLOR_BLUE         = colors.HexColor('#4338CA')
COLOR_BLUE_LIGHT   = colors.HexColor('#EDE9FE')
COLOR_BLUE_BORDER  = colors.HexColor('#C7D2FE')


def _get_severity_color(tingkat):
    t = (tingkat or '').lower()

    if t == 'tinggi':
        return COLOR_RED, COLOR_RED_LIGHT

    if t == 'sedang':
        return COLOR_AMBER, COLOR_AMBER_LIGHT

    return COLOR_GREEN_MID, COLOR_GREEN_LIGHT


def _get_severity_label(tingkat):
    t = (tingkat or '').lower()

    if t == 'tinggi':
        return 'Bahaya Tinggi'

    if t == 'sedang':
        return 'Perlu Perhatian'

    if t == 'sehat':
        return 'Sehat'

    return tingkat or 'Tidak diketahui'


def _safe_text(value):
    """
    Mengamankan teks sederhana agar tidak error saat masuk Paragraph ReportLab.
    """
    if value is None:
        return ''

    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def _get_glcm_level(feature_name: str, value: float) -> tuple[str, colors.Color, colors.Color]:
    """
    Menghasilkan label level sederhana untuk tampilan tabel GLCM.
    Return: (label, text_color, bg_color)

    Fitur yang digunakan:
    - kontras
    - dissimilarity
    - homogenitas
    - energi
    - entropy
    """
    try:
        v = float(value)
    except Exception:
        return 'Tidak diketahui', COLOR_TEXT_MUTED, COLOR_BG

    feature_name = feature_name.lower()

    if feature_name == 'kontras':
        if v < 50:
            return 'Rendah', COLOR_GREEN_MID, COLOR_GREEN_LIGHT
        if v < 200:
            return 'Sedang', COLOR_AMBER, COLOR_AMBER_LIGHT
        return 'Tinggi', COLOR_RED, COLOR_RED_LIGHT

    if feature_name == 'dissimilarity':
        if v < 5:
            return 'Rendah', COLOR_GREEN_MID, COLOR_GREEN_LIGHT
        if v < 15:
            return 'Sedang', COLOR_AMBER, COLOR_AMBER_LIGHT
        return 'Tinggi', COLOR_RED, COLOR_RED_LIGHT

    if feature_name == 'homogenitas':
        if v > 0.7:
            return 'Tinggi', COLOR_GREEN_MID, COLOR_GREEN_LIGHT
        if v > 0.5:
            return 'Sedang', COLOR_AMBER, COLOR_AMBER_LIGHT
        return 'Rendah', COLOR_RED, COLOR_RED_LIGHT

    if feature_name == 'energi':
        if v > 0.05:
            return 'Tinggi', COLOR_GREEN_MID, COLOR_GREEN_LIGHT
        if v > 0.02:
            return 'Sedang', COLOR_AMBER, COLOR_AMBER_LIGHT
        return 'Rendah', COLOR_RED, COLOR_RED_LIGHT

    if feature_name == 'entropy':
        if v < 5:
            return 'Rendah', COLOR_GREEN_MID, COLOR_GREEN_LIGHT
        if v < 7:
            return 'Sedang', COLOR_AMBER, COLOR_AMBER_LIGHT
        return 'Tinggi', COLOR_RED, COLOR_RED_LIGHT

    return 'Terukur', COLOR_GREEN_MID, COLOR_GREEN_LIGHT


def _build_static_glcm_summary(glcm_result: dict) -> str:
    """
    Fallback kesimpulan GLCM untuk PDF jika glcm_summary dari AI tidak tersedia.
    """
    if not glcm_result:
        return 'Kesimpulan GLCM tidak tersedia karena data analisis tekstur tidak ditemukan.'

    try:
        kontras = float(glcm_result.get('kontras', 0))
        dissimilarity = float(glcm_result.get('dissimilarity', 0))
        homogenitas = float(glcm_result.get('homogenitas', 0))
        energi = float(glcm_result.get('energi', 0))
        entropy = float(glcm_result.get('entropy', 0))
    except Exception:
        return 'Kesimpulan GLCM tidak tersedia karena nilai fitur tekstur tidak valid.'

    if kontras >= 200:
        teks_kontras = 'tekstur cenderung kasar dengan perbedaan intensitas yang tinggi'
    elif kontras >= 50:
        teks_kontras = 'tekstur memiliki variasi intensitas sedang'
    else:
        teks_kontras = 'tekstur cenderung halus dengan perbedaan intensitas rendah'

    if dissimilarity >= 15:
        teks_dissimilarity = 'perbedaan antar piksel berdekatan cukup besar'
    elif dissimilarity >= 5:
        teks_dissimilarity = 'perbedaan antar piksel berada pada tingkat sedang'
    else:
        teks_dissimilarity = 'perbedaan antar piksel relatif kecil'

    if homogenitas < 0.5:
        teks_homogenitas = 'area daun tidak homogen atau tidak seragam'
    elif homogenitas < 0.7:
        teks_homogenitas = 'area daun cukup homogen'
    else:
        teks_homogenitas = 'area daun sangat homogen'

    if energi < 0.02:
        teks_energi = 'pola tekstur terlihat tidak teratur'
    elif energi < 0.05:
        teks_energi = 'pola tekstur cukup teratur'
    else:
        teks_energi = 'pola tekstur terlihat teratur'

    if entropy >= 7:
        teks_entropy = 'kompleksitas tekstur tinggi'
    elif entropy >= 5:
        teks_entropy = 'kompleksitas tekstur sedang'
    else:
        teks_entropy = 'kompleksitas tekstur rendah'

    return (
        f'Berdasarkan hasil ekstraksi 5 fitur GLCM, area daun menunjukkan {teks_kontras}, '
        f'{teks_dissimilarity}, dan {teks_homogenitas}. Nilai energi menunjukkan bahwa '
        f'{teks_energi}, sedangkan entropy menunjukkan {teks_entropy}. Dengan demikian, '
        'GLCM digunakan sebagai analisis pendukung untuk menjelaskan karakter tekstur area daun '
        'yang telah terdeteksi oleh YOLOv8.'
    )


def generate_pdf(
    disease_name: str,
    disease_name_id: str,
    confidence: float,
    info: dict,
    advice: dict,
    ai_active: bool,
    image_path: str = None,
    glcm_result: dict = None,
    glcm_interp: dict = None,
    glcm_crop_path: str = None,
    glcm_summary: dict = None,
) -> bytes:
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Hasil Deteksi TomatoScan — {disease_name_id}",
        author="TomatoScan v2",
    )

    styles = getSampleStyleSheet()
    elements = []

    style_h2 = ParagraphStyle(
        'H2',
        parent=styles['Normal'],
        fontSize=13,
        leading=18,
        textColor=COLOR_GREEN_DARK,
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=8,
    )

    style_h3 = ParagraphStyle(
        'H3',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=COLOR_TEXT_MUTED,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=6,
    )

    style_body = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=10,
        leading=16,
        textColor=COLOR_TEXT,
        fontName='Helvetica',
        spaceAfter=4,
        alignment=TA_JUSTIFY,
    )

    style_muted = ParagraphStyle(
        'Muted',
        parent=styles['Normal'],
        fontSize=9,
        leading=14,
        textColor=COLOR_TEXT_MUTED,
        fontName='Helvetica',
        spaceAfter=2,
    )

    style_center = ParagraphStyle(
        'Center',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT_MUTED,
        fontName='Helvetica',
        alignment=TA_CENTER,
    )

    style_caption = ParagraphStyle(
        'Caption',
        parent=styles['Normal'],
        fontSize=8,
        leading=12,
        textColor=COLOR_TEXT_MUTED,
        fontName='Helvetica-Oblique',
        alignment=TA_CENTER,
        spaceBefore=4,
    )

    style_bullet = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontSize=10,
        leading=16,
        textColor=COLOR_TEXT,
        fontName='Helvetica',
        leftIndent=12,
        spaceAfter=3,
    )

    style_ai_note = ParagraphStyle(
        'AINote',
        parent=styles['Normal'],
        fontSize=8,
        leading=13,
        textColor=COLOR_BLUE,
        fontName='Helvetica-Oblique',
        spaceBefore=8,
    )

    style_section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=COLOR_GREEN_DARK,
        fontName='Helvetica-Bold',
        spaceBefore=10,
        spaceAfter=4,
    )

    style_table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=COLOR_GREEN_DARK,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    )

    style_table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXT,
        fontName='Helvetica',
    )

    style_table_cell_center = ParagraphStyle(
        'TableCellCenter',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=COLOR_TEXT,
        fontName='Helvetica',
        alignment=TA_CENTER,
    )

    style_small_note = ParagraphStyle(
        'SmallNote',
        parent=styles['Normal'],
        fontSize=8,
        leading=12,
        textColor=COLOR_TEXT_MUTED,
        fontName='Helvetica',
        spaceAfter=4,
    )

    style_summary_body = ParagraphStyle(
        'GLCMSummaryBody',
        parent=styles['Normal'],
        fontSize=9,
        leading=14,
        textColor=COLOR_BLUE,
        fontName='Helvetica',
        alignment=TA_JUSTIFY,
        spaceAfter=4,
    )

    # ── HEADER ────────────────────────────────────────────────
    header_data = [[
        Paragraph('<b>TomatoScan</b>', ParagraphStyle(
            'Brand',
            parent=styles['Normal'],
            fontSize=16,
            textColor=COLOR_GREEN_DARK,
            fontName='Helvetica-Bold',
        )),
        Paragraph(
            f'Laporan Hasil Deteksi Penyakit Daun Tomat<br/>'
            f'<font size="8" color="#706D65">Dicetak: {datetime.now().strftime("%d %B %Y, %H:%M WIB")}</font>',
            ParagraphStyle(
                'HeaderRight',
                parent=styles['Normal'],
                fontSize=10,
                textColor=COLOR_GREEN_DARK,
                fontName='Helvetica',
            )
        ),
    ]]

    header_table = Table(header_data, colWidths=[8 * cm, 9 * cm])
    header_table.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('BACKGROUND',    (0, 0), (-1, -1), COLOR_GREEN_LIGHT),
        ('TOPPADDING',    (0, 0), (-1, -1), 14),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
        ('BOX',           (0, 0), (-1, -1), 1, COLOR_GREEN_BORDER),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── GAMBAR + DIAGNOSIS ────────────────────────────────────
    severity_color, severity_bg = _get_severity_color(info.get('tingkat_bahaya', ''))
    severity_label = _get_severity_label(info.get('tingkat_bahaya', ''))
    emoji = info.get('emoji', '')

    left_content = []
    if image_path and os.path.exists(image_path):
        try:
            img = RLImage(image_path, width=7.5 * cm, height=7.5 * cm)
            img.hAlign = 'CENTER'
            left_content.append(img)
            left_content.append(Paragraph('Foto Hasil Deteksi dengan Bounding Box', style_caption))
        except Exception:
            left_content.append(Paragraph('Gambar tidak tersedia', style_muted))
    else:
        left_content.append(Paragraph('Gambar tidak tersedia', style_muted))

    right_content = []

    badge_data = [[Paragraph(f'<b>{_safe_text(severity_label)}</b>', ParagraphStyle(
        'Badge',
        parent=styles['Normal'],
        fontSize=9,
        textColor=severity_color,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
    ))]]

    badge_table = Table(badge_data, colWidths=[7.5 * cm])
    badge_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), severity_bg),
        ('BOX',           (0, 0), (-1, -1), 1, severity_color),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    right_content.append(badge_table)
    right_content.append(Spacer(1, 0.3 * cm))

    right_content.append(Paragraph(
        f'<b>{_safe_text(emoji)} {_safe_text(disease_name_id)}</b>',
        ParagraphStyle(
            'DiseaseName',
            parent=styles['Normal'],
            fontSize=16,
            leading=20,
            textColor=COLOR_GREEN_DARK,
            fontName='Helvetica-Bold',
        )
    ))

    right_content.append(Paragraph(
        f'<i>{_safe_text(disease_name)}</i>',
        ParagraphStyle(
            'DiseaseEN',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLOR_TEXT_MUTED,
            fontName='Helvetica-Oblique',
            spaceAfter=10,
        )
    ))

    conf_data = [[
        Paragraph('<b>Tingkat Keyakinan</b>', ParagraphStyle(
            'ConfLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=COLOR_TEXT_MUTED,
            fontName='Helvetica-Bold',
        )),
        Paragraph(f'<b>{confidence}%</b>', ParagraphStyle(
            'ConfVal',
            parent=styles['Normal'],
            fontSize=14,
            textColor=COLOR_GREEN_MID,
            fontName='Helvetica-Bold',
        )),
    ]]

    conf_table = Table(conf_data, colWidths=[4 * cm, 3.5 * cm])
    conf_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), COLOR_BG),
        ('BOX',           (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 10),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    right_content.append(conf_table)
    right_content.append(Spacer(1, 0.3 * cm))

    if info.get('penyebab') and info.get('penyebab') != 'None':
        penyebab_data = [[
            Paragraph('<b>PENYEBAB</b>', ParagraphStyle(
                'CauseLabel',
                parent=styles['Normal'],
                fontSize=7,
                textColor=COLOR_GREEN_MID,
                fontName='Helvetica-Bold',
            )),
        ], [
            Paragraph(_safe_text(info.get('penyebab', '')), ParagraphStyle(
                'CauseVal',
                parent=styles['Normal'],
                fontSize=9,
                textColor=COLOR_TEXT,
                fontName='Helvetica',
            )),
        ]]

        cause_table = Table(penyebab_data, colWidths=[7.5 * cm])
        cause_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), COLOR_BG),
            ('BOX',           (0, 0), (-1, -1), 1, COLOR_BORDER),
            ('TOPPADDING',    (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ]))
        right_content.append(cause_table)

    two_col = Table(
        [[left_content, right_content]],
        colWidths=[8.5 * cm, 8.5 * cm],
    )
    two_col.setStyle(TableStyle([
        ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING',   (0, 0), (-1, -1), 0),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 0),
        ('TOPPADDING',    (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(two_col)
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_BORDER))

    # ── TENTANG PENYAKIT ──────────────────────────────────────
    elements.append(Paragraph('Tentang Penyakit', style_h2))

    if info.get('deskripsi'):
        elements.append(Paragraph(_safe_text(info['deskripsi']), style_body))

    gejala = info.get('gejala', [])
    if gejala and isinstance(gejala, list) and len(gejala) > 0:
        elements.append(Paragraph('GEJALA YANG TERLIHAT', style_h3))
        for g in gejala:
            elements.append(Paragraph(f'— {_safe_text(g)}', style_bullet))

    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_BORDER))

    # ── ANALISIS TEKSTUR GLCM ─────────────────────────────────
    if glcm_result and glcm_result.get('status') == 'ok':
        elements.append(Paragraph('Analisis Tekstur GLCM', style_h2))

        elements.append(Paragraph(
            'Analisis GLCM digunakan untuk membaca karakter tekstur pada area daun '
            'yang terdeteksi oleh YOLOv8. GLCM tidak menggantikan proses klasifikasi, '
            'tetapi berfungsi sebagai analisis pendukung untuk menjelaskan pola tekstur '
            'pada area daun yang dianalisis.',
            style_body
        ))

        method_data = [
            [
                Paragraph('<b>Mode</b>', style_table_header),
                Paragraph('<b>Ukuran</b>', style_table_header),
                Paragraph('<b>Jarak</b>', style_table_header),
                Paragraph('<b>Sudut</b>', style_table_header),
                Paragraph('<b>Fitur</b>', style_table_header),
            ],
            [
                Paragraph('Grayscale', style_table_cell_center),
                Paragraph('64 × 64 px', style_table_cell_center),
                Paragraph('1 piksel', style_table_cell_center),
                Paragraph('0°, 45°, 90°, 135°', style_table_cell_center),
                Paragraph('5 fitur', style_table_cell_center),
            ],
        ]

        method_table = Table(method_data, colWidths=[3 * cm, 3 * cm, 3 * cm, 4 * cm, 4 * cm])
        method_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, 0), COLOR_GREEN_LIGHT),
            ('BACKGROUND',    (0, 1), (-1, -1), COLOR_WHITE),
            ('BOX',           (0, 0), (-1, -1), 1, COLOR_GREEN_BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING',   (0, 0), (-1, -1), 6),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
            ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(method_table)
        elements.append(Spacer(1, 0.25 * cm))

        glcm_left = []
        if glcm_crop_path and os.path.exists(glcm_crop_path):
            try:
                crop_img = RLImage(glcm_crop_path, width=5.5 * cm, height=4.2 * cm)
                crop_img.hAlign = 'CENTER'
                glcm_left.append(crop_img)
                glcm_left.append(Paragraph('Area ROI / Crop Bounding Box YOLOv8', style_caption))
            except Exception:
                glcm_left.append(Paragraph('Crop area GLCM tidak tersedia.', style_muted))
        else:
            glcm_left.append(Paragraph('Crop area GLCM tidak tersedia.', style_muted))

        bbox = glcm_result.get('bbox')
        glcm_right = []

        if bbox:
            glcm_right.append(Paragraph('<b>Area Analisis</b>', style_section_title))
            glcm_right.append(Paragraph(
                f'Bounding box: x1={bbox[0]}, y1={bbox[1]}, x2={bbox[2]}, y2={bbox[3]}',
                style_small_note
            ))

        glcm_right.append(Paragraph('<b>Catatan</b>', style_section_title))
        glcm_right.append(Paragraph(
            'Fitur yang digunakan dalam laporan ini adalah contrast, dissimilarity, '
            'homogeneity, energy, dan entropy. Kelima fitur ini dipilih agar analisis '
            'lebih ringkas, mudah dipahami, dan tidak menimbulkan ambiguitas.',
            style_small_note
        ))

        glcm_preview_table = Table(
            [[glcm_left, glcm_right]],
            colWidths=[6.5 * cm, 10.5 * cm],
        )
        glcm_preview_table.setStyle(TableStyle([
            ('BACKGROUND',    (0, 0), (-1, -1), COLOR_BG),
            ('BOX',           (0, 0), (-1, -1), 1, COLOR_BORDER),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING',    (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING',   (0, 0), (-1, -1), 10),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 10),
        ]))
        elements.append(glcm_preview_table)
        elements.append(Spacer(1, 0.25 * cm))

        feature_rows = [[
            Paragraph('<b>Fitur</b>', style_table_header),
            Paragraph('<b>Nilai</b>', style_table_header),
            Paragraph('<b>Level</b>', style_table_header),
            Paragraph('<b>Interpretasi</b>', style_table_header),
        ]]

        feature_config = [
            ('Kontras',       'kontras',       'Perbedaan intensitas tekstur'),
            ('Dissimilarity', 'dissimilarity', 'Ketidaksamaan antar piksel'),
            ('Homogenitas',   'homogenitas',   'Kemiripan piksel berdekatan'),
            ('Energi',        'energi',        'Keteraturan pola tekstur'),
            ('Entropy',       'entropy',       'Kompleksitas dan ketidakteraturan tekstur'),
        ]

        level_bg_colors = []

        for label, key, desc in feature_config:
            value = glcm_result.get(key, '-')
            interpretation = ''

            if glcm_interp and isinstance(glcm_interp, dict):
                interpretation = glcm_interp.get(key, '')

            level_label, level_color, level_bg = _get_glcm_level(key, value)
            level_bg_colors.append(level_bg)

            feature_rows.append([
                Paragraph(f'<b>{label}</b><br/><font size="7" color="#706D65">{desc}</font>', style_table_cell),
                Paragraph(_safe_text(value), style_table_cell_center),
                Paragraph(f'<font color="{level_color.hexval()}"><b>{level_label}</b></font>', style_table_cell_center),
                Paragraph(_safe_text(interpretation), style_table_cell),
            ])

        feature_table = Table(
            feature_rows,
            colWidths=[4.3 * cm, 2.4 * cm, 2.6 * cm, 7.7 * cm],
            repeatRows=1,
        )

        feature_style = [
            ('BACKGROUND',    (0, 0), (-1, 0), COLOR_GREEN_LIGHT),
            ('TEXTCOLOR',     (0, 0), (-1, 0), COLOR_GREEN_DARK),
            ('BOX',           (0, 0), (-1, -1), 1, COLOR_GREEN_BORDER),
            ('INNERGRID',     (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ('TOPPADDING',    (0, 0), (-1, -1), 7),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
            ('LEFTPADDING',   (0, 0), (-1, -1), 7),
            ('RIGHTPADDING',  (0, 0), (-1, -1), 7),
            ('VALIGN',        (0, 0), (-1, -1), 'TOP'),
        ]

        for row_index, bg_color in enumerate(level_bg_colors, start=1):
            feature_style.append(('BACKGROUND', (2, row_index), (2, row_index), bg_color))

        feature_table.setStyle(TableStyle(feature_style))
        elements.append(feature_table)
        elements.append(Spacer(1, 0.25 * cm))

        # Kesimpulan GLCM dari AI / fallback lokal
        summary_text = ''
        summary_source = ''

        if glcm_summary and isinstance(glcm_summary, dict):
            summary_text = glcm_summary.get('summary', '')
            summary_source = glcm_summary.get('source', '')

        if not summary_text:
            summary_text = _build_static_glcm_summary(glcm_result)
            summary_source = 'static'

        if summary_text:
            if summary_source == 'ai':
                summary_badge = 'Kesimpulan AI Analisis Tekstur GLCM'
            else:
                summary_badge = 'Kesimpulan Analisis Tekstur GLCM'

            summary_data = [[
                Paragraph(
                    f'<b>{summary_badge}</b>',
                    ParagraphStyle(
                        'GLCMSummaryTitle',
                        parent=styles['Normal'],
                        fontSize=9,
                        leading=13,
                        textColor=COLOR_BLUE,
                        fontName='Helvetica-Bold',
                    )
                )
            ], [
                Paragraph(_safe_text(summary_text), style_summary_body)
            ]]

            points = glcm_summary.get('points', []) if isinstance(glcm_summary, dict) else []
            if points and isinstance(points, list):
                point_text = ' • '.join([_safe_text(point) for point in points[:3]])
                summary_data.append([
                    Paragraph(
                        f'<font size="8" color="#4338CA">{point_text}</font>',
                        style_small_note
                    )
                ])

            summary_table = Table(summary_data, colWidths=[17 * cm])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND',    (0, 0), (-1, -1), COLOR_BLUE_LIGHT),
                ('BOX',           (0, 0), (-1, -1), 1, COLOR_BLUE_BORDER),
                ('TOPPADDING',    (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING',   (0, 0), (-1, -1), 12),
                ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
            ]))
            elements.append(summary_table)
            elements.append(Spacer(1, 0.2 * cm))

        elements.append(Paragraph(
            'Ringkasan fitur: kontras dan dissimilarity membantu membaca tingkat ketidaksamaan tekstur, '
            'homogenitas menunjukkan keseragaman area daun, energi menunjukkan keteraturan pola, '
            'sedangkan entropy menunjukkan tingkat kompleksitas tekstur.',
            style_small_note
        ))

        elements.append(Spacer(1, 0.3 * cm))
        elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_BORDER))

    # ── SARAN PENANGANAN ──────────────────────────────────────
    elements.append(Paragraph('Saran Penanganan', style_h2))

    if ai_active:
        sumber_text   = 'Saran dihasilkan oleh Groq AI (LLaMA 3.1)'
        sumber_color  = COLOR_BLUE
        sumber_bg     = COLOR_BLUE_LIGHT
        sumber_border = COLOR_BLUE_BORDER
    else:
        sumber_text   = 'Saran dari database lokal TomatoScan'
        sumber_color  = COLOR_TEXT_MUTED
        sumber_bg     = COLOR_BG
        sumber_border = COLOR_BORDER

    badge_sumber = Table([[Paragraph(f'<b>{sumber_text}</b>', ParagraphStyle(
        'SumberBadge',
        parent=styles['Normal'],
        fontSize=8,
        textColor=sumber_color,
        fontName='Helvetica-Bold',
    ))]], colWidths=[17 * cm])

    badge_sumber.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), sumber_bg),
        ('BOX',           (0, 0), (-1, -1), 1, sumber_border),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 12),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 12),
    ]))
    elements.append(badge_sumber)
    elements.append(Spacer(1, 0.25 * cm))

    sections = advice.get('sections', [])
    if sections:
        for section in sections:
            judul = section.get('judul', '')
            poin_list = section.get('poin', [])

            if judul:
                elements.append(Paragraph(f'<b>{_safe_text(judul)}</b>', style_section_title))

            for poin in poin_list:
                elements.append(Paragraph(f'→ {_safe_text(poin)}', style_bullet))

        if ai_active:
            elements.append(Paragraph(
                '* Saran ini dihasilkan oleh AI berdasarkan hasil deteksi. '
                'Tetap konsultasikan dengan penyuluh pertanian setempat.',
                style_ai_note
            ))
    else:
        elements.append(Paragraph('Saran tidak tersedia.', style_muted))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width='100%', thickness=1, color=COLOR_BORDER))

    # ── FOOTER ────────────────────────────────────────────────
    elements.append(Spacer(1, 0.3 * cm))
    footer_data = [[
        Paragraph(
            'TomatoScan v2 &nbsp;·&nbsp; YOLOv8 + PlantVillage Dataset &nbsp;·&nbsp; GLCM 5 Fitur &nbsp;·&nbsp; AI oleh Groq (LLaMA 3.1)',
            style_center
        ),
    ], [
        Paragraph(
            '<i>Hasil deteksi bersifat indikatif dan bukan pengganti konsultasi ahli pertanian.</i>',
            style_center
        ),
    ]]

    footer_table = Table(footer_data, colWidths=[17 * cm])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND',    (0, 0), (-1, -1), COLOR_BG),
        ('BOX',           (0, 0), (-1, -1), 1, COLOR_BORDER),
        ('TOPPADDING',    (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('LEFTPADDING',   (0, 0), (-1, -1), 16),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 16),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()