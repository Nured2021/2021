/* EASY AI DOC & EDUCATION CORE — Frontend */

let selectedFormat = 'pdf';
let selectedProfessor = 'cs';

// ── Tab Navigation ───────────────────────────────────────────
function showTab(tabId, btn) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
  document.getElementById('sec-' + tabId).classList.add('active');
  if (btn) btn.classList.add('active');
  if (tabId === 'files') loadFiles();
}

// ── Format Selection ─────────────────────────────────────────
function selectFormat(fmt, btn) {
  selectedFormat = fmt;
  document.querySelectorAll('.format-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

// ── Smart Generate ───────────────────────────────────────────
async function smartGenerate() {
  const prompt = document.getElementById('mainPrompt').value.trim();
  if (!prompt) { toast('Please enter a prompt', 'error'); return; }

  showLoading(true);
  try {
    const res = await fetch('/api/smart-generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt })
    });
    const data = await res.json();
    if (data.error) { toast(data.error, 'error'); return; }

    displayResults(data);
    toast(`Generated ${data.files.length} file(s) successfully!`, 'success');
  } catch (e) {
    toast('Generation failed: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

// ── Generate Specific Format ─────────────────────────────────
async function generateFile() {
  const prompt = document.getElementById('mainPrompt').value.trim();
  if (!prompt) { toast('Please enter a prompt', 'error'); return; }

  showLoading(true);
  try {
    const res = await fetch('/api/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt, type: selectedFormat })
    });
    const data = await res.json();
    if (data.error) { toast(data.error, 'error'); return; }

    displaySingleResult(data);
    toast(`${selectedFormat.toUpperCase()} generated!`, 'success');
  } catch (e) {
    toast('Generation failed: ' + e.message, 'error');
  } finally {
    showLoading(false);
  }
}

// ── Display Results ──────────────────────────────────────────
function displayResults(data) {
  const area = document.getElementById('resultsArea');
  const analysisHtml = `
    <div class="result-card" style="border-color:var(--brand)">
      <div class="result-info">
        <div class="result-icon">🧠</div>
        <div>
          <div class="result-name">AI Analysis</div>
          <div class="result-meta">Intent: ${data.analysis.intent} | Mode: ${data.analysis.mode} | Files: ${data.analysis.file_types.join(', ')}</div>
        </div>
      </div>
    </div>`;

  const filesHtml = data.files.map(f => {
    if (f.error) return `<div class="result-card" style="border-color:var(--red)"><div class="result-info"><div class="result-icon">❌</div><div><div class="result-name">${f.type.toUpperCase()}</div><div class="result-meta">${f.error}</div></div></div></div>`;
    const icon = { pdf: '📄', docx: '📝', xlsx: '📊', pptx: '📽️' }[f.type] || '📁';
    return `
      <div class="result-card">
        <div class="result-info">
          <div class="result-icon">${icon}</div>
          <div>
            <div class="result-name">${f.filename}</div>
            <div class="result-meta">${f.type.toUpperCase()}</div>
          </div>
        </div>
        <div class="result-actions">
          <a href="${f.download_url}" class="btn btn-primary btn-sm">⬇ Download</a>
        </div>
      </div>`;
  }).join('');

  area.innerHTML = analysisHtml + filesHtml;
}

function displaySingleResult(data) {
  const area = document.getElementById('resultsArea');
  const icon = { pdf: '📄', docx: '📝', xlsx: '📊', pptx: '📽️' }[data.type] || '📁';
  area.innerHTML = `
    <div class="result-card">
      <div class="result-info">
        <div class="result-icon">${icon}</div>
        <div>
          <div class="result-name">${data.filename}</div>
          <div class="result-meta">${data.type.toUpperCase()} | Generated at ${new Date(data.generated_at).toLocaleTimeString()}</div>
        </div>
      </div>
      <div class="result-actions">
        <a href="${data.download_url}" class="btn btn-primary btn-sm">⬇ Download</a>
      </div>
    </div>`;
}

// ── Professor Selection ──────────────────────────────────────
function selectProfessor(id, el) {
  selectedProfessor = id;
  document.querySelectorAll('.prof-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
}

async function loadProfessors() {
  try {
    const res = await fetch('/api/professors');
    const profs = await res.json();
    const grid = document.getElementById('profGrid');
    grid.innerHTML = profs.map(p => `
      <div class="prof-card ${p.id === selectedProfessor ? 'selected' : ''}" onclick="selectProfessor('${p.id}', this)">
        <div class="prof-icon">${p.icon}</div>
        <div class="prof-name">${p.name}</div>
        <div class="prof-title">${p.title}</div>
        <div class="prof-specs">${p.specialties.slice(0, 3).join(' · ')}</div>
      </div>
    `).join('');
  } catch (e) {
    console.error('Failed to load professors:', e);
  }
}

// ── Generate Course ──────────────────────────────────────────
async function generateCourse() {
  const topic = document.getElementById('eduTopic').value.trim();
  if (!topic) { toast('Please enter a topic', 'error'); return; }

  showLoading(true, 'eduLoading');
  try {
    const res = await fetch('/api/education/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ professor: selectedProfessor, topic })
    });
    const data = await res.json();
    if (data.error) { toast(data.error, 'error'); return; }

    displayCourse(data.course);
    toast('Course generated!', 'success');
  } catch (e) {
    toast('Failed: ' + e.message, 'error');
  } finally {
    showLoading(false, 'eduLoading');
  }
}

function displayCourse(course) {
  const out = document.getElementById('courseOutput');

  const syllabusRows = course.syllabus.weeks.map(w =>
    `<tr><td><strong>Week ${w.week}</strong></td><td>${w.topic}</td><td>${w.readings}</td></tr>`
  ).join('');

  const examSections = course.exam.sections.map(s => {
    const questions = s.questions.map((q, i) => {
      if (typeof q === 'string') return `<div class="exam-q">${i + 1}. ${q}</div>`;
      let html = `<div class="exam-q">${i + 1}. ${q.q}`;
      if (q.options) html += '<br>' + q.options.join('<br>');
      html += '</div>';
      return html;
    }).join('');
    return `<div class="exam-section"><h4>${s.type} (${s.count} questions, ${s.points_each} pts each)</h4>${questions}</div>`;
  }).join('');

  out.innerHTML = `
    <div class="course-header">
      <h2>${course.professor.icon} ${course.professor.name}</h2>
      <p>${course.professor.title} | Topic: ${course.topic} | ${course.date}</p>
      <p style="font-size:11px;margin-top:4px;color:rgba(255,255,255,.5)">Style: ${course.professor.style}</p>
    </div>

    <div class="panel">
      <div class="panel-head"><span class="ph-title">📋 15-Week Syllabus</span></div>
      <div style="overflow-x:auto;padding:8px">
        <table class="syllabus-table">
          <thead><tr><th>Week</th><th>Topic</th><th>Readings</th></tr></thead>
          <tbody>${syllabusRows}</tbody>
        </table>
      </div>
    </div>

    <div class="panel" style="margin-top:12px">
      <div class="panel-head"><span class="ph-title">📖 Lecture Notes</span></div>
      <div class="lecture-box">${course.lecture.content}</div>
    </div>

    <div class="panel" style="margin-top:12px">
      <div class="panel-head"><span class="ph-title">📝 Examination (${course.exam.duration})</span></div>
      ${examSections}
    </div>
  `;
}

// ── Files ────────────────────────────────────────────────────
async function loadFiles() {
  try {
    const res = await fetch('/api/files');
    const files = await res.json();
    const grid = document.getElementById('filesGrid');
    if (files.length === 0) {
      grid.innerHTML = '<div style="text-align:center;padding:40px;color:var(--muted)">No files generated yet. Go to the Generator tab to create documents.</div>';
      return;
    }
    const icons = { pdf: '📄', docx: '📝', xlsx: '📊', pptx: '📽️' };
    grid.innerHTML = files.map(f => `
      <div class="file-card">
        <div class="file-icon">${icons[f.type] || '📁'}</div>
        <div class="file-info">
          <div class="file-name">${f.name}</div>
          <div class="file-size">${(f.size / 1024).toFixed(1)} KB · ${f.type.toUpperCase()}</div>
        </div>
        <a href="${f.download_url}" class="btn btn-primary btn-sm">⬇</a>
      </div>
    `).join('');
  } catch (e) {
    console.error('Failed to load files:', e);
  }
}

// ── Helpers ──────────────────────────────────────────────────
function showLoading(show, id = 'loading') {
  const el = document.getElementById(id);
  if (el) el.classList.toggle('active', show);
}

function toast(msg, type = 'info') {
  const container = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = 'toast ' + type;
  t.textContent = msg;
  container.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

function usePreset(text) {
  document.getElementById('mainPrompt').value = text;
}

// ── Init ─────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  loadProfessors();
  // Health check
  fetch('/api/health').then(r => r.json()).then(d => {
    document.getElementById('healthStatus').textContent = `v${d.version} · ${d.professors} Professors · ${d.engines.length} Engines`;
  });
});
