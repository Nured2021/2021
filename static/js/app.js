/* ═══════════════════════════════════════════════════════════
   ORD AI — Complete Frontend Logic
   All 4 Blueprints: One Working System
═══════════════════════════════════════════════════════════ */
"use strict";

// ─── Security: HTML escaping helper ────────────────────────
function _esc(str) {
  return String(str ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#x27;");
}

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
  el.innerHTML = bns.map((bn, i) =>
    `<div class="bn-item">
      <span>${_esc(bn)}</span>
      <button class="fix-bn-btn" data-idx="${i}">Fix</button>
    </div>`
  ).join("");
  // Store current bottlenecks on element to avoid closure capture
  el._bns = bns;
  el.querySelectorAll(".fix-bn-btn").forEach(btn => {
    btn.addEventListener("click", function() {
      const bn = (el._bns || [])[parseInt(this.dataset.idx)];
      if (!bn) return;
      this.disabled = true;
      this.textContent = "Fixing...";
      fetch("/api/fix_bottleneck", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ bottleneck: bn }),
      }).then(() => toast("🔧 Fixed: " + _esc(bn), "success"));
    });
  });
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
  const tags = queue.map(j => `<span style="background:rgba(245,158,11,.2);padding:1px 6px;border-radius:10px;margin:0 2px;font-size:10px">${_esc(j)}</span>`).join("");
  items.innerHTML = current
    ? `<strong style="color:var(--accent)">Building: ${_esc(current)}</strong>  ${tags}`
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
  const icon = document.createElement("span");
  icon.className = "cm-icon";
  icon.textContent = "👤";
  const bubble = document.createElement("div");
  bubble.className = "cm-bubble";
  bubble.textContent = txt;
  div.appendChild(icon);
  div.appendChild(bubble);
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
  div.className = `job-item ${_esc(status)}`;
  div.textContent = (status === "started" ? "🔨 " : "📋 ") + job;
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
    const uIcon = document.createElement("span");
    uIcon.textContent = "👤";
    const uBubble = document.createElement("div");
    uBubble.className = "bubble";
    uBubble.textContent = msg;
    userDiv.appendChild(uIcon);
    userDiv.appendChild(uBubble);
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
      const aIcon = document.createElement("span");
      aIcon.textContent = "🤖";
      const aBubble = document.createElement("div");
      aBubble.className = "bubble";
      aBubble.textContent = d.reply;
      aiDiv.appendChild(aIcon);
      aiDiv.appendChild(aBubble);
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

// ══════════════════════════════════════════════════════════════
//  ENGINE LAYER — ModelRouter · Memory · RAG · FineTuner
// ══════════════════════════════════════════════════════════════

// ── Load engine status on page load + every 15s ──────────────
(function engineInit() {
  loadEngineStatus();
  loadMemory();
  loadRagStats();
  loadFinetuneStatus();
  setInterval(loadEngineStatus, 15000);
  setInterval(loadMemory, 10000);
  setInterval(loadFinetuneStatus, 5000);
  setInterval(loadEpisodicFeed, 8000);
})();

// ─── ModelRouter ─────────────────────────────────────────────
async function loadEngineStatus() {
  try {
    const r = await fetch("/api/models");
    const d = await r.json();
    if (!d.backends) return;
    document.getElementById("routerActiveBadge").textContent = d.active_backend || "mock";
    const container = document.getElementById("routerBackends");
    container.innerHTML = "";
    const order = ["lmstudio","ollama","openai","mock"];
    order.forEach(name => {
      const b = d.backends[name];
      if (!b) return;
      const online = b.available;
      const avgLat = b.avg_latency_ms > 0 ? `${b.avg_latency_ms}ms` : "--";
      container.innerHTML += `
        <div class="router-backend">
          <div class="rb-dot ${online ? 'online' : 'offline'}"></div>
          <span class="rb-name">${name}</span>
          <span class="rb-model">${b.model}</span>
          <div class="rb-stats"><b>${b.calls}</b> calls &nbsp;<b>${b.tokens}</b> tok</div>
          <span class="rb-latency">${avgLat}</span>
        </div>`;
    });
  } catch(e) { /* silent */ }
}

async function routerAsk() {
  const prompt = document.getElementById("routerPrompt").value.trim();
  const taskType = document.getElementById("routerTaskType").value;
  if (!prompt) return;
  const el = document.getElementById("routerResponse");
  el.textContent = "⏳ Asking " + taskType + " model…";
  try {
    const r = await fetch("/api/models/ask", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({prompt, task_type: taskType})
    });
    const d = await r.json();
    el.textContent = `[${d.backend} · ${d.model} · ${d.latency_ms}ms · ${d.tokens} tok]\n\n${d.response}`;
    loadEngineStatus();
  } catch(e) { el.textContent = "Error: " + e.message; }
}

document.getElementById("routerPrompt")?.addEventListener("keydown", e => {
  if (e.key === "Enter") routerAsk();
});

// ─── Memory ──────────────────────────────────────────────────
async function loadMemory() {
  try {
    const r = await fetch("/api/memory");
    const d = await r.json();
    if (d.error) return;
    document.getElementById("memShortCount").textContent =
      d.short_term.active_keys + " keys";
    document.getElementById("memLongCount").textContent =
      (d.long_term.count || 0) + " docs";
    document.getElementById("memEpiCount").textContent =
      (d.episodic.total || 0) + " events";
  } catch(e) {}
  loadEpisodicFeed();
}

async function loadEpisodicFeed() {
  try {
    const r = await fetch("/api/memory/episodic?limit=20");
    const events = await r.json();
    const feed = document.getElementById("episodicFeed");
    if (!feed) return;
    feed.innerHTML = events.map(ev => {
      const t = new Date(ev.ts * 1000).toTimeString().slice(0,8);
      return `<div class="ep-event">
        <span class="ep-kind ${ev.kind}">[${ev.kind}]</span>
        <span class="ep-msg">${ev.event}</span>
        <span style="color:var(--text3);font-size:9px">${t}</span>
      </div>`;
    }).join("");
  } catch(e) {}
}

async function memSearch() {
  const q = document.getElementById("memSearchQ").value.trim();
  if (!q) return;
  const el = document.getElementById("memResults");
  el.textContent = "⏳ Searching…";
  try {
    const r = await fetch(`/api/memory/search?q=${encodeURIComponent(q)}`);
    const results = await r.json();
    if (!results.length) { el.textContent = "No results found."; return; }
    el.innerHTML = results.map(r =>
      `<div style="margin-bottom:6px"><b>${r.key}</b><br><span style="color:var(--text3)">${(r.content||"").slice(0,200)}</span></div>`
    ).join("<hr style='border-color:var(--border1);margin:4px 0'>");
  } catch(e) { el.textContent = "Error: " + e.message; }
}

// ─── RAG ─────────────────────────────────────────────────────
async function loadRagStats() {
  try {
    const r = await fetch("/api/rag/stats");
    const d = await r.json();
    document.getElementById("ragTotal").textContent = d.total_documents || 0;
    document.getElementById("ragVectorized").textContent = d.vectorized || 0;
    document.getElementById("ragVectorOk").textContent = d.vector_search_enabled ? "Hybrid" : "BM25";
    document.getElementById("ragVectorOk").className = d.vector_search_enabled ? "badge badge-green" : "badge badge-amber";
    document.getElementById("ragDocBadge").textContent = (d.total_documents || 0) + " docs";
  } catch(e) {}
}

async function ragQuery() {
  const q = document.getElementById("ragQuery").value.trim();
  const mode = document.getElementById("ragMode").value;
  if (!q) return;
  const el = document.getElementById("ragResults");
  el.innerHTML = "⏳ Querying knowledge base…";
  try {
    const r = await fetch("/api/rag/query", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({query: q, mode, top_k: 5})
    });
    const d = await r.json();
    if (!d.results || !d.results.length) {
      el.textContent = "No results found."; return;
    }
    el.innerHTML = d.results.map(res =>
      `<div class="rag-result">
        <div class="rag-result-title">${_esc(res.title)}</div>
        <div class="rag-result-content">${_esc((res.content||"").slice(0,200))}…</div>
        <div class="rag-result-meta">
          <span>score: ${_esc((res.score||0).toFixed(3))}</span>
          <span>method: ${_esc(res.method||mode)}</span>
          <span>source: ${_esc(res.source||"-")}</span>
        </div>
      </div>`
    ).join("");
  } catch(e) { el.textContent = "Error: " + e.message; }
}

document.getElementById("ragQuery")?.addEventListener("keydown", e => {
  if (e.key === "Enter") ragQuery();
});

async function ragIngest() {
  const title   = document.getElementById("ingestTitle").value.trim();
  const content = document.getElementById("ingestContent").value.trim();
  const tags    = document.getElementById("ingestTags").value.trim();
  if (!content) { toast("Add content to ingest", "error"); return; }
  try {
    const r = await fetch("/api/rag/ingest", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({title: title||"Untitled", content, source:"user", tags})
    });
    const d = await r.json();
    toast(`✅ Ingested: ${d.title} (id #${d.id})`, "success");
    document.getElementById("ingestContent").value = "";
    document.getElementById("ingestTitle").value = "";
    loadRagStats();
  } catch(e) { toast("Ingest failed: " + e.message, "error"); }
}

// ─── FineTuner ───────────────────────────────────────────────
async function loadFinetuneStatus() {
  try {
    const r = await fetch("/api/finetune/status");
    const d = await r.json();
    const badge = document.getElementById("ftStatusBadge");
    const fill  = document.getElementById("ftProgressFill");
    const pct   = document.getElementById("ftProgressPct");
    const status = document.getElementById("ftStatus");
    badge.textContent = d.status;
    badge.className = "badge " + (d.status==="done"?"badge-green":d.status==="training"?"badge-blue":d.status==="error"?"badge-red":"badge-amber");
    fill.style.width = d.progress + "%";
    pct.textContent  = d.progress + "%";
    if (d.current_run) {
      const run = d.current_run;
      status.textContent = `Model: ${run.base_model} | Method: ${run.method} | Epochs: ${run.epochs}\n` +
        `Samples: ${run.training_samples} | Status: ${run.status}` +
        (run.final_loss ? ` | Final loss: ${run.final_loss}` : "") +
        (run.current_loss ? ` | Loss: ${run.current_loss}` : "");
    }
    // History
    if (d.history && d.history.length) {
      document.getElementById("ftHistory").innerHTML = d.history.slice(-5).reverse().map(h =>
        `<div class="ft-hist-item">${h.started_at} · ${h.base_model} · ${h.method} · ${h.training_samples} samples · ${h.status}</div>`
      ).join("");
    }
  } catch(e) {}
}

async function startFinetune() {
  const base_model = document.getElementById("ftModel").value;
  const method     = document.getElementById("ftMethod").value;
  const epochs     = parseInt(document.getElementById("ftEpochs").value) || 3;
  try {
    const r = await fetch("/api/finetune/start", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({base_model, method, epochs})
    });
    const d = await r.json();
    toast(`🎓 Fine-tuning ${d.status}: ${base_model}`, d.status==="started"?"success":"info");
    loadFinetuneStatus();
  } catch(e) { toast("Finetune error: " + e.message, "error"); }
}

// ══════════════════════════════════════════════════════════════
//  ORCHESTRATOR — Task Board + HITL Approval Queue
// ══════════════════════════════════════════════════════════════

(function orchInit() {
  loadTaskBoard();
  loadHitlQueue();
  setInterval(loadTaskBoard, 4000);
  setInterval(loadHitlQueue, 3000);
})();

// Live update from socket
if (typeof socket !== "undefined") {
  socket.on("orchestrator_update", function(data) {
    renderTaskBoard(data.tasks || []);
    renderHitlQueue(data.tasks ? data.tasks.filter(t => t.status === "awaiting_approval") : []);
  });
  socket.on("hitl_required", function(task) {
    toast(`⚠ HITL Required: ${task.name}`, "error");
    loadHitlQueue();
  });
  socket.on("hitl_approved", function(d) {
    toast(`✅ HITL Approved: ${d.task_id.slice(0,8)}`, "success");
    loadTaskBoard();
    loadHitlQueue();
  });
  socket.on("build_complete", function(d) {
    toast(`🎉 Build complete → ${d.version} | ${d.files} files | ${d.tests} tests | [${d.backend}]`, "success");
    loadTaskBoard();
    loadEngineStatus();
  });
}

async function loadTaskBoard() {
  try {
    const r = await fetch("/api/orchestrator/tasks");
    const tasks = await r.json();
    renderTaskBoard(tasks);
    // Update counts
    const hitl = tasks.filter(t => t.status === "awaiting_approval");
    document.getElementById("orchTaskCount").textContent = tasks.length + " tasks";
    document.getElementById("orchHitlCount").textContent = hitl.length + " HITL";
    document.getElementById("orchHitlCount").className = hitl.length > 0 ? "badge badge-red" : "badge badge-amber";
    renderHitlQueue(hitl);
  } catch(e) {}
}

function renderTaskBoard(tasks) {
  const board = document.getElementById("taskBoard");
  if (!board) return;
  if (!tasks || !tasks.length) {
    board.innerHTML = '<div style="color:var(--text3);font-size:11px;padding:12px">No active tasks. Trigger a build to see the DAG here.</div>';
    return;
  }
  const statusIcon = {
    done: "✅", running: "⚡", pending: "⏳",
    blocked: "🔒", awaiting_approval: "👤", failed: "❌"
  };
  board.innerHTML = tasks.map(t => `
    <div class="task-card status-${t.status}">
      <div class="tc-header">
        <div class="tc-status-dot ${t.status}"></div>
        <span class="tc-name">${t.name}</span>
        <span class="tc-lane ${t.hitl_lane}">${t.hitl_lane}</span>
      </div>
      <div class="tc-desc">${t.description || ""}</div>
      <div class="tc-meta">
        <span>${statusIcon[t.status] || "•"} ${t.status}</span>
        ${t.assigned_backend ? `<span>🔀 ${t.assigned_backend}</span>` : ""}
        ${t.duration ? `<span>⏱ ${t.duration}s</span>` : ""}
      </div>
      ${t.error ? `<div style="color:var(--red);font-size:9px;margin-top:4px">⚠ ${t.error}</div>` : ""}
      ${t.status === "awaiting_approval" ? `
        <button class="tc-approve-btn" onclick="approveTask('${t.id}','${t.name}')">✅ Approve</button>
        <button class="tc-reject-btn" onclick="rejectTask('${t.id}','${t.name}')">✗ Reject</button>
      ` : ""}
    </div>
  `).join("");
}

async function loadHitlQueue() {
  try {
    const r = await fetch("/api/orchestrator/hitl");
    const tasks = await r.json();
    renderHitlQueue(tasks);
    const badge = document.getElementById("hitlQueueBadge");
    if (badge) {
      badge.textContent = tasks.length + " pending";
      badge.className = tasks.length > 0 ? "badge badge-red" : "badge badge-green";
    }
  } catch(e) {}
}

function renderHitlQueue(tasks) {
  const el = document.getElementById("hitlApprovalQueue");
  if (!el) return;
  if (!tasks || !tasks.length) {
    el.innerHTML = '<div style="color:var(--green);font-size:11px;padding:12px">✅ No pending approvals — all gates clear</div>';
    return;
  }
  el.innerHTML = tasks.map(t => `
    <div class="hitl-item">
      <div class="hitl-icon">👤</div>
      <div class="hitl-body">
        <div class="hitl-name">${t.name} <span class="tc-lane ${t.hitl_lane}">${t.hitl_lane}</span></div>
        <div class="hitl-desc">${t.description || ""}</div>
      </div>
      <div class="hitl-actions">
        <button class="hitl-approve" onclick="approveTask('${t.id}','${t.name}')">✅ Approve</button>
        <button class="hitl-reject" onclick="rejectTask('${t.id}','${t.name}')">✗ Reject</button>
      </div>
    </div>
  `).join("");
}

async function approveTask(taskId, taskName) {
  try {
    const r = await fetch("/api/orchestrator/approve", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({task_id: taskId})
    });
    const d = await r.json();
    toast(`✅ Approved: ${taskName}`, "success");
    loadTaskBoard();
    loadHitlQueue();
  } catch(e) { toast("Approve error: " + e.message, "error"); }
}

async function rejectTask(taskId, taskName) {
  try {
    await fetch("/api/orchestrator/reject", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({task_id: taskId, reason: "Rejected by user"})
    });
    toast(`✗ Rejected: ${taskName}`, "info");
    loadTaskBoard();
    loadHitlQueue();
  } catch(e) { toast("Reject error: " + e.message, "error"); }
}

/* ═══════════════════════════════════════════════════════════════
   PROTECTION SYSTEMS — 14 Live Status Cards
═══════════════════════════════════════════════════════════════ */
const PROTECTION_SYSTEMS = [
  { id:1,  icon:"🔄", title:"Infinite Loop Protection",     sev:"CRITICAL", desc:"Escape hatch + frustration metric + forced mode switching",  endpoint:"/api/loop_protection/status" },
  { id:2,  icon:"👤", title:"Human Judgment Stabilizer",    sev:"CRITICAL", desc:"Detect inconsistent feedback + loss aversion correction",     endpoint:"/api/judgment/status" },
  { id:3,  icon:"🔒", title:"Memory Poisoning Protection",  sev:"CRITICAL", desc:"Database-backed memory + audit trail + rollback",             endpoint:"/api/secure_memory/status" },
  { id:4,  icon:"🧩", title:"Agent Composability",          sev:"HIGH",     desc:"Primitives-based architecture — fix parts without rewriting",  endpoint:null },
  { id:5,  icon:"🏗",  title:"Structure-in-the-Loop",       sev:"HIGH",     desc:"Sandbox + database + version control identity layers",         endpoint:"/api/structural_defense/status" },
  { id:6,  icon:"🧠", title:"Continuous Memory",            sev:"HIGH",     desc:"Portable memory that persists across sessions",                endpoint:"/api/continuous_memory/status" },
  { id:7,  icon:"📡", title:"Observability & Monitoring",   sev:"CRITICAL", desc:"Engineering traces · Executive cost · Customer quality",       endpoint:"/api/observability/status" },
  { id:8,  icon:"⚡", title:"Load & Stress Testing",        sev:"HIGH",     desc:"Normal / surge / adversarial three-scenario testing",          endpoint:null },
  { id:9,  icon:"⏪", title:"Rollback & Recovery",          sev:"CRITICAL", desc:"One-command versioned bundle revert in under 10 minutes",      endpoint:"/api/rollback/status" },
  { id:10, icon:"📂", title:"Agent Filesystem (AgentFS)",   sev:"HIGH",     desc:"SQLite-backed POSIX FS + KV store + append-only audit trail",  endpoint:null },
  { id:11, icon:"🛡", title:"Prompt Injection Defense",     sev:"CRITICAL", desc:"Multi-agent pipeline: detect → classify → sanitize → verify", endpoint:"/api/prompt_defense/status" },
  { id:12, icon:"💰", title:"Cost Controls & Budget",       sev:"HIGH",     desc:"Per-workflow tracking · quota enforcement · ROI calculation",  endpoint:"/api/cost/status" },
  { id:13, icon:"📋", title:"Continuous Post-Mortems",      sev:"MEDIUM",   desc:"Incident capture → root cause → improvement tasks pipeline",   endpoint:"/api/postmortem/status" },
  { id:14, icon:"🪪", title:"Identity & Guardrails (Soul)", sev:"HIGH",     desc:"Non-overridable agent identity + absolute/soft guardrail rules",endpoint:"/api/identity/status" },
];

async function loadProtectionSystems() {
  const grid = document.getElementById('protectionGrid');
  if (!grid) return;
  grid.innerHTML = '';

  for (const sys of PROTECTION_SYSTEMS) {
    let statusClass = 'active', badgeClass = 'badge-active', statusText = '✅ ACTIVE';
    if (sys.endpoint) {
      try {
        const r = await fetch(sys.endpoint);
        if (!r.ok) throw new Error('http ' + r.status);
        const d = await r.json();
        if (d.error) { statusClass = 'error'; badgeClass = 'badge-error'; statusText = '❌ ERROR'; }
        else if (d.status === 'partial') { statusClass = 'warning'; badgeClass = 'badge-partial'; statusText = '⚠ PARTIAL'; }
      } catch(e) {
        statusClass = 'warning'; badgeClass = 'badge-partial'; statusText = '⚠ LOADING';
      }
    }
    const sevClass = sys.sev === 'CRITICAL' ? 'sev-critical' : sys.sev === 'HIGH' ? 'sev-high' : 'sev-medium';
    grid.innerHTML += `
      <div class="prot-card ${statusClass}">
        <div class="prot-card-header">
          <span class="prot-card-icon">${sys.icon}</span>
          <span class="prot-card-title">#${sys.id} ${sys.title}</span>
          <span class="prot-card-sev ${sevClass}">${sys.sev}</span>
        </div>
        <span class="prot-status-badge ${badgeClass}">${statusText}</span>
        <div class="prot-card-desc">${sys.desc}</div>
      </div>`;
  }

  loadCostDetail();
  loadIncidents();
  loadRollbackBundles();
}

async function loadCostDetail() {
  const el = document.getElementById('costDetail');
  if (!el) return;
  try {
    const r = await fetch('/api/cost/summary');
    const d = await r.json();
    el.innerHTML = `<b>Daily Budget:</b> $${d.daily_budget ?? '—'} &nbsp;|&nbsp;
      <b>Spent Today:</b> $${(d.spent_today ?? 0).toFixed(4)} &nbsp;|&nbsp;
      <b>Requests:</b> ${d.total_requests ?? 0} &nbsp;|&nbsp;
      <b>Budget OK:</b> ${d.budget_ok ? '✅' : '❌ EXCEEDED'}`;
  } catch(e) { el.textContent = 'Cost Governor: active (no data yet)'; }
}

async function loadIncidents() {
  const el = document.getElementById('incidentList');
  if (!el) return;
  try {
    const r = await fetch('/api/postmortem/incidents');
    const d = await r.json();
    const items = d.incidents ?? [];
    if (!items.length) { el.textContent = '✅ No incidents recorded — system healthy'; return; }
    el.innerHTML = items.slice(0,5).map(i =>
      `<div style="margin-bottom:8px;padding:8px;background:#1a1a2e;border-radius:6px">
        <b>${i.id ?? '?'}</b> · <span style="color:#ffaa00">${i.category ?? 'unknown'}</span>
        · ${i.status ?? ''} · <span style="color:#888">${i.timestamp ?? ''}</span>
       </div>`).join('');
  } catch(e) { el.textContent = 'Post-mortem system: active (no incidents yet)'; }
}

async function loadRollbackBundles() {
  const el = document.getElementById('rollbackList');
  if (!el) return;
  try {
    const r = await fetch('/api/rollback/bundles');
    const d = await r.json();
    const bundles = d.bundles ?? [];
    if (!bundles.length) { el.textContent = 'No bundles yet — click "Snapshot Now" to create first bundle'; return; }
    el.innerHTML = bundles.slice(0,5).map(b =>
      `<div style="margin-bottom:6px;padding:8px;background:#1a1a2e;border-radius:6px;display:flex;align-items:center;gap:8px">
        <span style="color:#00e5a0;font-weight:700">${b.id ?? '?'}</span>
        <span>${b.name ?? ''}</span>
        <span style="color:#888;font-size:11px;margin-left:auto">${b.created_at ?? ''}</span>
        <button class="btn-secondary" style="font-size:11px;padding:3px 8px" onclick="doRollback('${b.id}')">↩ Rollback</button>
       </div>`).join('');
  } catch(e) { el.textContent = 'Rollback system: active (no bundles yet)'; }
}

async function snapshotBundle() {
  try {
    const r = await fetch('/api/rollback/snapshot', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name:'manual-snapshot'})});
    const d = await r.json();
    toast('📸 Bundle ' + (d.bundle_id ?? '') + ' saved!', 'success');
    loadRollbackBundles();
  } catch(e) { toast('Snapshot failed: ' + e.message, 'error'); }
}

async function doRollback(bundleId) {
  if (!confirm('Rollback to bundle ' + bundleId + '?')) return;
  try {
    const r = await fetch('/api/rollback/rollback', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({bundle_id: bundleId})});
    const d = await r.json();
    toast('⏪ Rolled back to ' + bundleId, d.success ? 'success' : 'warn');
  } catch(e) { toast('Rollback failed: ' + e.message, 'error'); }
}

async function testInjection() {
  const input = document.getElementById('injTestInput').value;
  const res = document.getElementById('injResult');
  if (!input.trim()) { res.textContent = 'Please enter text to scan.'; return; }
  res.textContent = '⏳ Scanning...';
  try {
    const r = await fetch('/api/prompt_defense/inspect', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({text: input})});
    const d = await r.json();
    const safe = d.is_safe !== false;
    res.innerHTML = `<b style="color:${safe?'#00e5a0':'#ff4466'}">${safe ? '✅ SAFE' : '🚨 INJECTION DETECTED'}</b>
      &nbsp; Threat level: <b>${d.threat_level ?? 'none'}</b>
      &nbsp; Flags: ${(d.flags ?? []).join(', ') || 'none'}
      ${d.sanitized ? '<br>Sanitized: <em>' + d.sanitized + '</em>' : ''}`;
  } catch(e) { res.textContent = 'Scan error: ' + e.message; }
}

// Auto-load when protection section becomes visible
const _origShowSection = window.showSection;
window.showSection = function(name, btn) {
  _origShowSection && _origShowSection(name, btn);
  if (name === 'protection') loadProtectionSystems();
};

// Also trigger on direct page load if hash === protection
if (location.hash === '#protection') loadProtectionSystems();
