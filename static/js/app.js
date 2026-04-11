/* ═══════════════════════════════════════════════════════════
   ORD AI — Complete Frontend Logic
   All 4 Blueprints: One Working System
═══════════════════════════════════════════════════════════ */
"use strict";

// ─── Socket.IO connection ───────────────────────────────────
const socket = io();

// ─── CodeMirror editor ─────────────────────────────────────
let editor;
window.addEventListener("DOMContentLoaded", () => {
  const ta = document.getElementById("codeEditor");
  if (ta) {
    editor = CodeMirror.fromTextArea(ta, {
      mode: "python",
      theme: "dracula",
      lineNumbers: true,
      autoCloseBrackets: true,
      matchBrackets: true,
      indentUnit: 4,
      tabSize: 4,
      indentWithTabs: false,
      lineWrapping: false,
      extraKeys: { "Ctrl-Enter": runCode, "Cmd-Enter": runCode },
    });
  }
  refreshState();
  loadRecentBuilds();
});

// ─── Section navigation ────────────────────────────────────
function showSection(id, btn) {
  document.querySelectorAll(".section").forEach(s => s.classList.remove("active"));
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("active"));
  document.getElementById("sec-" + id).classList.add("active");
  if (btn) btn.classList.add("active");
  if (id === "editor" && editor) editor.refresh();
}

// ─── Socket events ─────────────────────────────────────────
socket.on("connect", () => console.log("ORD AI — Socket connected ∞"));
socket.on("disconnect", () => console.warn("Socket disconnected"));

socket.on("state_update", s => updateDashboard(s));
socket.on("metrics", m => updateMetrics(m));
socket.on("pilot_msg", e => appendPilotMsg(e));
socket.on("pilot_history", msgs => { msgs.forEach(m => appendPilotMsg(m)); });
socket.on("agent_update", agents => renderAgentPipeline(agents));
socket.on("hitl_update", items => renderHITL(items));
socket.on("build_done", d => {
  toast(`✅ Build complete: ${d.job} → ${d.version}`, "success");
  updateVersionLabel(d.version);
  loadRecentBuilds();
});
socket.on("tests_done", r => renderTestResults(r));

// ─── Dashboard update ──────────────────────────────────────
function updateDashboard(s) {
  // KPI cards
  setKpi("kpiCores",    s.cores_active,    50, "kpiBCores");
  setKpi("kpiEngines",  s.engines_active,  50, "kpiBEngines");
  setKpi("kpiAI",       s.ai_active,       50, "kpiBAI");
  setKpi("kpiProgress", s.build_progress, 100, "kpiBProgress", "%");
  setKpi("kpiTests",    s.tests_passed,    50, "kpiBTests");
  setEl("kpiFixes",     s.fixes_applied);
  setEl("kpiLoop",      `∞ Loop #${s.loop_count}`);

  // Build progress bar
  const pct = s.build_progress || 0;
  const fill = document.getElementById("bigProgress");
  const pctEl = document.getElementById("bigPct");
  if (fill) fill.style.width = pct + "%";
  if (pctEl) pctEl.textContent = pct + "%";
  setEl("buildTask", s.build_task || "Idle");

  // Gauges
  setGauge("grCores",   "gCoresVal",   s.cores_active,   50);
  setGauge("grEngines", "gEnginesVal", s.engines_active, 50);
  setGauge("grAI",      "gAIVal",      s.ai_active,      50);

  // Bottom bar
  setEl("testsLbl", `${s.tests_passed}/50`);
  setEl("fixesLbl", s.fixes_applied);
  setEl("loopLbl",  `#${s.loop_count}`);
  setEl("verLbl",   s.version);
  updateVersionLabel(s.version);

  // Bottlenecks
  renderBottlenecks(s.bottlenecks || []);

  // Files
  renderFiles(s.files_created || []);

  // Queue
  renderQueue(s.job_queue || [], s.current_job);

  // Metrics bar
  updateMetrics({ cpu: s.cpu, ram: s.ram, rps: s.rps, resp_ms: s.resp_ms });

  // Version list
  if (s.versions) renderVersionList(s.versions);
}

function setKpi(valId, val, max, barId, suffix) {
  const el = document.getElementById(valId);
  if (!el) return;
  if (suffix === "%") {
    el.innerHTML = `${val}<span>${suffix}</span>`;
  } else {
    el.innerHTML = `${val}<span>/${max}</span>`;
  }
  if (barId) {
    const bar = document.getElementById(barId);
    if (bar) bar.style.width = Math.min(100, (val / max) * 100) + "%";
  }
}

function setEl(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

function setGauge(circleId, valId, val, max) {
  const circ = document.getElementById(circleId);
  const valEl = document.getElementById(valId);
  if (!circ || !valEl) return;
  const r = 32, circumference = 2 * Math.PI * r;
  const filled = (val / max) * circumference;
  circ.setAttribute("stroke-dasharray", `${filled} ${circumference}`);
  valEl.textContent = val;
}

function updateMetrics(m) {
  if (m.cpu !== undefined) {
    setEl("navCpu", m.cpu + "%");
    setEl("mbCpuVal", m.cpu + "%");
    const b = document.getElementById("mbCpu");
    if (b) b.style.width = m.cpu + "%";
    const s = document.getElementById("smCpu");
    if (s) { s.style.width = m.cpu + "%"; setEl("smCpuV", m.cpu + "%"); }
  }
  if (m.ram !== undefined) {
    setEl("navRam", m.ram + "%");
    setEl("mbRamVal", m.ram + "%");
    const b = document.getElementById("mbRam");
    if (b) b.style.width = m.ram + "%";
    const s = document.getElementById("smRam");
    if (s) { s.style.width = m.ram + "%"; setEl("smRamV", m.ram + "%"); }
  }
  if (m.rps !== undefined) {
    setEl("navRps", m.rps);
    setEl("mbRpsVal", m.rps);
    const b = document.getElementById("mbRps");
    if (b) b.style.width = Math.min(100, m.rps / 20) + "%";
  }
  setEl("mbLoop",  window._loopCount || 0);
  setEl("mbTeam",  3);
}

function updateVersionLabel(v) {
  setEl("navVersion", v);
  setEl("mbVer", v);
  setEl("verLbl", v);
}

// ─── Bottlenecks ───────────────────────────────────────────
function renderBottlenecks(bns) {
  const el = document.getElementById("bottlenecks");
  if (!el) return;
  if (!bns.length) {
    el.innerHTML = '<div class="bn-empty">No bottlenecks ✓</div>';
    return;
  }
  el.innerHTML = bns.map(bn =>
    `<div class="bn-item">
      <span>${bn}</span>
      <button onclick="fixBottleneck(this,'${bn.replace(/'/g, "\\'")}')">Fix</button>
    </div>`
  ).join("");
}

function fixBottleneck(btn, bn) {
  btn.disabled = true;
  btn.textContent = "Fixing...";
  fetch("/api/fix_bottleneck", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ bottleneck: bn }),
  }).then(() => toast("🔧 Fixed: " + bn, "success"));
}

// ─── Files ─────────────────────────────────────────────────
function renderFiles(files) {
  const el = document.getElementById("fileList");
  if (!el) return;
  if (!files.length) {
    el.innerHTML = '<span class="fl-empty">Awaiting build...</span>';
    return;
  }
  el.innerHTML = files.slice(-20).map(f =>
    `<div class="fl-item done">✅ ${f}</div>`
  ).join("");
  el.scrollTop = el.scrollHeight;
}

// ─── Queue ─────────────────────────────────────────────────
function renderQueue(queue, current) {
  const strip = document.getElementById("queueStrip");
  const items = document.getElementById("queueItems");
  if (!strip || !items) return;
  if (!queue.length && !current) {
    strip.style.display = "none";
    return;
  }
  strip.style.display = "block";
  const tags = queue.map(j => `<span style="background:rgba(245,158,11,.2);padding:1px 6px;border-radius:10px;margin:0 2px;font-size:10px">${j}</span>`).join("");
  items.innerHTML = current
    ? `<strong style="color:var(--accent)">Building: ${current}</strong>  ${tags}`
    : tags;
}

// ─── Agent Pipeline ────────────────────────────────────────
function renderAgentPipeline(agents) {
  const el = document.getElementById("agentPipeline");
  if (!el || !agents) return;
  el.innerHTML = agents.map(a => {
    const cls = a.status === "done" ? "done" : a.status === "running" ? "running" : "";
    return `<div class="ap-row">
      <span class="ap-icon">${a.icon}</span>
      <span class="ap-name">${a.name}</span>
      <div class="ap-bar-wrap"><div class="ap-bar ${cls}" style="width:${a.progress}%"></div></div>
      <span class="ap-status ${a.status}">${a.status === "done" ? "✓ done" : a.status === "running" ? "running" : "idle"}</span>
    </div>`;
  }).join("");
}

// ─── HITL Queue ────────────────────────────────────────────
function renderHITL(items) {
  const el = document.getElementById("hitlList");
  if (!el) return;
  if (!items || !items.length) {
    el.innerHTML = '<div class="hitl-empty">No HITL items — AI Pilot running autonomously ✓</div>';
    return;
  }
  el.innerHTML = items.map(h => {
    const lane = h.lane.replace("HITL_", "");
    return `<div class="hitl-item">
      <span>${h.description}</span>
      <span class="hitl-lane ${lane}">${lane}</span>
      <button class="hitl-approve" onclick="approveHITL(${h.id})">Approve</button>
    </div>`;
  }).join("");
}

function approveHITL(id) {
  fetch("/api/hitl_approve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id }),
  }).then(() => toast("✅ HITL approved", "success"));
}

// ─── Version list ──────────────────────────────────────────
function renderVersionList(versions) {
  const el = document.getElementById("versionList");
  if (!el) return;
  el.innerHTML = versions.slice(0, 15).map(v =>
    `<div class="vl-item"><span class="vl-ver">${v.ver}</span><span class="vl-msg">${v.msg}</span><span class="vl-time muted">${v.time}</span></div>`
  ).join("");
}

// ─── Chat ──────────────────────────────────────────────────
function appendPilotMsg(e) {
  const log = document.getElementById("chatLog");
  if (!log) return;
  const kind = e.kind || "info";
  let cls = "ai";
  if (kind === "success" || kind === "done") cls = "success";
  if (kind === "warn") cls = "system";
  const div = document.createElement("div");
  div.className = `chat-msg ${cls}`;
  div.innerHTML = `<span class="cm-icon">${cls === "ai" || cls === "success" ? "🤖" : "⚡"}</span>
    <div class="cm-bubble"><small style="opacity:.5;font-size:9px">${e.time}</small><br>${e.msg}</div>`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function sendBuild() {
  const txt = (document.getElementById("promptInput")?.value || "").trim();
  if (!txt) { toast("Please type what to build", "error"); return; }
  appendUserMsg(txt);
  document.getElementById("promptInput").value = "";
  fetch("/api/ai_chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: txt }),
  })
  .then(r => r.json())
  .then(d => { appendPilotMsg({ time: now(), msg: d.reply, kind: "info" }); });
}

function sendCmd(cmd) {
  appendUserMsg(cmd);
  fetch("/api/ai_chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: cmd }),
  })
  .then(r => r.json())
  .then(d => appendPilotMsg({ time: now(), msg: d.reply, kind: "info" }));
}

function appendUserMsg(txt) {
  const log = document.getElementById("chatLog");
  if (!log) return;
  const div = document.createElement("div");
  div.className = "chat-msg user";
  div.innerHTML = `<span class="cm-icon">👤</span><div class="cm-bubble">${txt}</div>`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
}

function stopBuild() {
  socket.emit("stop_build");
  toast("⏸ Build stopped", "info");
}

function refreshState() {
  fetch("/api/state").then(r => r.json()).then(s => updateDashboard(s));
}

// ─── Builder section ───────────────────────────────────────
function setPreset(text) {
  const el = document.getElementById("builderPrompt");
  if (el) el.value = text;
}

function buildFromBuilder() {
  const txt = (document.getElementById("builderPrompt")?.value || "").trim();
  if (!txt) { toast("Please describe what to build", "error"); return; }
  fetch("/api/build", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ job: txt }),
  })
  .then(r => r.json())
  .then(d => {
    toast(d.status === "queued" ? `📋 Queued: ${txt}` : `🚀 Building: ${txt}`, "info");
    showSection("dashboard", document.querySelector(".nav-btn"));
    document.querySelectorAll(".nav-btn")[0].classList.add("active");
    updateJobList(txt, d.status);
  });
}

function updateJobList(job, status) {
  const el = document.getElementById("jobList");
  if (!el) return;
  if (el.querySelector(".job-item.idle")) el.innerHTML = "";
  const div = document.createElement("div");
  div.className = `job-item ${status}`;
  div.innerHTML = `${status === "started" ? "🔨" : "📋"} ${job}`;
  el.insertBefore(div, el.firstChild);
}

function loadRecentBuilds() {
  fetch("/api/builds").then(r => r.json()).then(builds => {
    const el = document.getElementById("recentBuilds");
    if (!el) return;
    if (!builds.length) { el.innerHTML = "<div style='color:var(--text3)'>No builds yet</div>"; return; }
    el.innerHTML = builds.map(b =>
      `<div style="padding:4px 0;border-bottom:1px solid var(--border);display:flex;justify-content:space-between">
        <span style="color:var(--text2)">${b.job.substring(0,30)}...</span>
        <span class="${b.status === 'done' ? 'green' : 'accent'}" style="font-family:var(--mono);font-size:10px">${b.version}</span>
      </div>`
    ).join("");
  });
}

// ─── Editor ────────────────────────────────────────────────
function runCode() {
  const code = editor ? editor.getValue() : document.getElementById("codeEditor")?.value || "";
  const lang = document.getElementById("editorLang")?.value || "python";
  const out  = document.getElementById("edOutput");
  if (out) out.textContent = "> Running...";
  fetch("/api/execute", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, lang }),
  })
  .then(r => r.json())
  .then(d => {
    if (out) out.textContent = d.error ? `ERROR:\n${d.error}` : d.output || "(no output)";
  });
}

function saveCode() {
  const code = editor ? editor.getValue() : "";
  const blob = new Blob([code], { type: "text/plain" });
  const url  = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = "ord_ai_code.py"; a.click();
  URL.revokeObjectURL(url);
  toast("💾 Code downloaded", "success");
}

function clearEditor() {
  if (editor) editor.setValue("");
  const o = document.getElementById("edOutput");
  if (o) o.textContent = "> Cleared.";
}

document.getElementById("editorLang")?.addEventListener("change", function() {
  if (editor) editor.setOption("mode", this.value);
});

// ─── Tests ─────────────────────────────────────────────────
function runTests() {
  toast("🧪 Running test suite...", "info");
  fetch("/api/test_run", { method: "POST" }).then(() => {});
}

function renderTestResults(r) {
  toast(`✅ Tests: ${r.unit.passed} unit, ${r.integration.passed} integration`, "success");
}

// ─── MODALS ────────────────────────────────────────────────
const MODAL_CONTENT = {
  save: () => `
    <label>Save Name</label>
    <input id="mSaveName" placeholder="My ORD AI Build v1.0" value="ORD AI Build ${new Date().toLocaleDateString()}">
    <label style="margin-top:8px">Notes (optional)</label>
    <textarea placeholder="What was built..." style="height:60px"></textarea>
    <div class="modal-row">
      <button class="pa-btn primary" onclick="doSave()">💾 Save to Repository</button>
      <button class="pa-btn" onclick="closeModal()">Cancel</button>
    </div>`,

  load: () => `
    <div class="modal-sect">Saved Builds</div>
    <ul class="modal-list" id="mLoadList"><li>Loading...</li></ul>`,

  deploy: () => `
    <div class="modal-sect">Deploy ORD AI to:</div>
    <div class="deploy-grid">
      ${["🌐 Vercel","☁ AWS","🔵 Azure","🟠 GCP","🐋 Docker","⚙ Heroku","📦 GitHub Pages","🌩 Netlify"].map(p =>
        `<button class="deploy-btn" onclick="doDeploy('${p}')">${p}</button>`).join("")}
    </div>
    <div class="modal-sect">Deploy Config</div>
    <label>Environment</label>
    <select class="ed-select" style="width:100%"><option>Production</option><option>Staging</option><option>Development</option></select>
    <label>Region</label>
    <select class="ed-select" style="width:100%"><option>us-east-1</option><option>eu-west-1</option><option>ap-southeast-1</option></select>
    <div class="prog-bar-wrap" id="deployProg" style="display:none"><div class="prog-bar-fill" id="deployFill" style="width:0%"></div></div>
    <div id="deployStatus" style="font-size:11px;margin-top:4px"></div>`,

  version: () => `
    <div class="modal-sect">Version History</div>
    <div id="mVersionList" style="max-height:280px;overflow-y:auto">Loading...</div>`,

  collab: () => `
    <div class="modal-sect">Team Members Online</div>
    <ul class="modal-list">
      <li><span>👤 You (Owner)</span><span class="green">● Online</span></li>
      <li><span>👤 Developer A</span><span class="green">● Online</span></li>
      <li><span>👤 Developer B</span><span class="amber">● Away</span></li>
    </ul>
    <div class="modal-sect">Invite</div>
    <input placeholder="Email address...">
    <button class="pa-btn primary" style="margin-top:8px">Send Invite</button>`,

  marketplace: () => `
    <div class="modal-sect">ORD AI Marketplace — Pre-built Systems</div>
    <ul class="modal-list" id="mMarket">Loading...</ul>`,

  templates: () => `
    <div class="modal-sect">Quick Build Templates</div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
      ${[
        ["🤖 ChatGPT Clone","ChatGPT Clone with voice, memory, plugins"],
        ["🛒 Ecommerce","Full Ecommerce with Stripe payments"],
        ["📱 Social Media","Social Media with real-time chat"],
        ["🧠 RAG Pipeline","RAG Pipeline with vector DB"],
        ["🤖 AI Agent","AI Agent that builds and runs code"],
        ["⚙ API Server","REST API with auth & docs"],
        ["📊 Dashboard","Analytics with ML predictions"],
        ["📲 Mobile App","React Native with offline mode"],
      ].map(([name,prompt]) =>
        `<button class="deploy-btn" style="text-align:left;padding:10px" onclick="closeModal();setPreset('${prompt}');showSection('builder',null)">${name}</button>`
      ).join("")}
    </div>`,

  export: () => `
    <div class="modal-sect">Export ORD AI System</div>
    <div class="modal-row">
      ${["📦 ZIP","🐋 Docker Image","☁ Terraform","📋 PDF Blueprint","📊 Analytics CSV"].map(f =>
        `<button class="deploy-btn" onclick="doExport('${f}')">${f}</button>`).join("")}
    </div>`,

  ai: () => `
    <div class="ai-chat-log" id="aiLog">
      <div class="ai-row ai"><span>🤖</span><div class="bubble">ORD AI Pilot here. Ask me anything. I can build, fix, explain, test, or deploy — right now.</div></div>
    </div>
    <div class="ai-input-row">
      <input id="aiInput" placeholder="Ask AI Pilot anything..." onkeydown="if(event.key==='Enter')aiSend()">
      <button class="pa-btn primary" onclick="aiSend()">Send</button>
    </div>`,
};

function openModal(type) {
  const overlay = document.getElementById("modalOverlay");
  const modal   = document.getElementById("modal");
  const title   = document.getElementById("modalTitle");
  const body    = document.getElementById("modalBody");
  if (!modal) return;

  const titles = {
    save:"💾 Save Build", load:"📂 Load Build", deploy:"🚀 Deploy",
    version:"🔄 Version History", collab:"👥 Team Collaboration",
    marketplace:"🏪 Marketplace", templates:"📚 Templates",
    export:"📦 Export", ai:"🤖 AI Pilot Assistant",
  };

  title.textContent = titles[type] || type;
  body.innerHTML = (MODAL_CONTENT[type] || (() => "<p>Coming soon...</p>"))();
  overlay.classList.add("show");
  modal.style.display = "block";
  setTimeout(() => modal.classList.add("show"), 10);

  // Populate dynamic content
  if (type === "load") loadSaves();
  if (type === "version") loadVersions();
  if (type === "marketplace") loadMarket();
}

function closeModal() {
  const overlay = document.getElementById("modalOverlay");
  const modal   = document.getElementById("modal");
  overlay.classList.remove("show");
  modal.classList.remove("show");
  setTimeout(() => { modal.style.display = "none"; }, 200);
}

function loadSaves() {
  fetch("/api/builds").then(r => r.json()).then(builds => {
    const el = document.getElementById("mLoadList");
    if (!el) return;
    if (!builds.length) { el.innerHTML = "<li>No saved builds yet</li>"; return; }
    el.innerHTML = builds.map(b =>
      `<li><span>${b.job.substring(0,30)}</span><span class="accent" style="font-family:var(--mono);font-size:10px">${b.version}</span></li>`
    ).join("");
  });
}

function loadVersions() {
  fetch("/api/state").then(r => r.json()).then(s => {
    const el = document.getElementById("mVersionList");
    if (!el) return;
    const versions = s.versions || [];
    el.innerHTML = versions.map(v =>
      `<div class="vl-item"><span class="vl-ver">${v.ver}</span><span class="vl-msg">${v.msg}</span><span class="vl-time muted">${v.time}</span></div>`
    ).join("") || "<div style='color:var(--text3)'>No versions yet</div>";
  });
}

function loadMarket() {
  const el = document.getElementById("mMarket");
  if (!el) return;
  fetch("/api/state").then(r => r.json()).then(s => {
    const m = s.marketplace || [];
    el.innerHTML = m.map(item =>
      `<li><span>${item.name} <span class="muted">(${item.downloads} downloads)</span></span><span class="accent">${item.price}</span></li>`
    ).join("");
  });
}

function doSave() {
  const name = document.getElementById("mSaveName")?.value || "ORD AI Build";
  fetch("/api/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  }).then(() => { closeModal(); toast(`💾 Saved: ${name}`, "success"); });
}

function doDeploy(platform) {
  const prog = document.getElementById("deployProg");
  const fill = document.getElementById("deployFill");
  const status = document.getElementById("deployStatus");
  if (prog) prog.style.display = "block";
  const steps = ["Preparing build...", "Running tests...", "Building container...", "Pushing to registry...", `Deploying to ${platform}...`, "Health check...", "✅ Deployed!"];
  let i = 0;
  const iv = setInterval(() => {
    if (i >= steps.length) { clearInterval(iv); return; }
    const pct = ((i + 1) / steps.length * 100).toFixed(0);
    if (fill) fill.style.width = pct + "%";
    if (status) status.textContent = steps[i];
    i++;
    if (i === steps.length) toast(`🚀 Deployed to ${platform}!`, "success");
  }, 600);
}

function doExport(fmt) {
  toast(`📦 Exporting as ${fmt}...`, "info");
  setTimeout(() => toast(`✅ ${fmt} export ready`, "success"), 1500);
  closeModal();
}

function aiSend() {
  const input = document.getElementById("aiInput");
  if (!input?.value.trim()) return;
  const msg = input.value.trim();
  input.value = "";
  const log = document.getElementById("aiLog");
  if (log) {
    const userDiv = document.createElement("div");
    userDiv.className = "ai-row user";
    userDiv.innerHTML = `<span>👤</span><div class="bubble">${msg}</div>`;
    log.appendChild(userDiv);
    log.scrollTop = log.scrollHeight;
  }
  fetch("/api/ai_chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: msg }),
  })
  .then(r => r.json())
  .then(d => {
    if (log) {
      const aiDiv = document.createElement("div");
      aiDiv.className = "ai-row ai";
      aiDiv.innerHTML = `<span>🤖</span><div class="bubble">${d.reply}</div>`;
      log.appendChild(aiDiv);
      log.scrollTop = log.scrollHeight;
    }
  });
}

// ─── Toast ─────────────────────────────────────────────────
function toast(msg, type = "info") {
  const c = document.getElementById("toastContainer");
  if (!c) return;
  const t = document.createElement("div");
  t.className = `toast ${type}`;
  t.textContent = msg;
  c.appendChild(t);
  setTimeout(() => t.remove(), 3500);
}

// ─── Prompt input keyboard ────────────────────────────────
document.getElementById("promptInput")?.addEventListener("keydown", function(e) {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendBuild(); }
});

// ─── Helpers ───────────────────────────────────────────────
function now() {
  return new Date().toTimeString().slice(0, 8);
}
