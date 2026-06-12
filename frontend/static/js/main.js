// ─── TomatoScan v2 — main.js ─────────────────────────────────

const dropZone    = document.getElementById('dropZone');
const fileInput   = document.getElementById('fileInput');
const dropContent = document.getElementById('dropContent');
const dropPreview = document.getElementById('dropPreview');
const previewImg  = document.getElementById('previewImg');
const fileName    = document.getElementById('fileName');
const btnAnalyze  = document.getElementById('btnAnalyze');
const uploadForm  = document.getElementById('uploadForm');
const loadingOverlay = document.getElementById('loadingOverlay');

// ── File Handler ──────────────────────────────────────────────
function handleFile(file) {
  if (!file) return;

  const allowed = ['image/jpeg', 'image/png', 'image/webp'];
  if (!allowed.includes(file.type)) {
    alert('Format tidak didukung. Gunakan JPG, PNG, atau WEBP.');
    return;
  }
  if (file.size > 16 * 1024 * 1024) {
    alert('Ukuran file terlalu besar. Maksimal 16 MB.');
    return;
  }

  const reader = new FileReader();
  reader.onload = (e) => {
    previewImg.src = e.target.result;
    dropContent.style.display = 'none';
    dropPreview.style.display = 'block';
    fileName.textContent      = file.name;
    btnAnalyze.disabled       = false;
  };
  reader.readAsDataURL(file);
}

// ── Input change ──────────────────────────────────────────────
fileInput.addEventListener('change', () => {
  if (fileInput.files.length > 0) handleFile(fileInput.files[0]);
});

// ── Drag & Drop ───────────────────────────────────────────────
dropZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  dropZone.classList.add('dragover');
});
dropZone.addEventListener('dragleave', () => {
  dropZone.classList.remove('dragover');
});
dropZone.addEventListener('drop', (e) => {
  e.preventDefault();
  dropZone.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) {
    // Assign to input so form submission works
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    handleFile(file);
  }
});

// ── Form Submit → show loading ────────────────────────────────
uploadForm.addEventListener('submit', (e) => {
  if (!fileInput.files.length) {
    e.preventDefault();
    return;
  }
  loadingOverlay.classList.add('show');
  btnAnalyze.disabled = true;
});