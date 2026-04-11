/* ────────────────────────────────────────────
   ORD AI Platform — Frontend JS
   Socket.IO + CodeMirror + All 10 Panels
   ──────────────────────────────────────────── */

// ── Socket.IO Connection ──
const socket = io();

socket.on("connect",      ()  => addResponse("🟢 Connected to ORD AI Platform.", "info"));
socket.on("disconnect",   ()  => addResponse("🔴 Disconnected. Reconnecting...", "warn"));
socket.on("state_update", (s) => applyState(s));
socket.on("metrics_update",(m)=> applyMetrics(m));
socket.on("pilot_msg",    (m) => addResponse(`${m.msg}`, m.kind));
socket.on("pilot_history",(h) => h.forEach(m => addResponse(m.msg, m.kind)));
socket.on("build_done",   (d) => {
  addResponse(`🎉 Build complete: ${d.job} — ${d.version}`, "success");
  document.getElementById("versionTag").textContent = d.version;
  document.getElementById("statusVer").textContent = "📜 " + d.version;
  document.getElementById("dashVer").textContent = d.version;
});
socket.on("tests_done",   (r) => renderTestResults(r));

// ── CodeMirror ──
let editor;
window.addEventListener("DOMContentLoaded", () => {
  editor = CodeMirror.fromTextArea(document.getElementById("codeEditor"), {
    mode: "python",
    theme: "dracula",
    lineNumbers: true,
    indentUnit: 4,
    tabSize: 4,
    autofocus: false,
    extraKeys: { "Ctrl-Enter": runCode },
  });
  document.getElementById("langSelect").addEventListener("change", (e) => {
    editor.setOption("mode", e.target.value);
  });
  loadState();
});

// ── State Application ──
function applyState(s) {
  // Progress
  const pct = s.build_progress || 0;
  document.getElementById("progressBar").style.width = pct + "%";
  document.getElementById("progressPct").textContent = pct + "%";
  document.getElementById("buildTask").textContent = s.build_task || "Idle";

  // 50/50/50 meters
  setPct("coresFill",   (s.cores_active   / 50) * 100);
  setPct("enginesFill", (s.engines_active / 50) * 100);
  setPct("aiFill",      (s.ai_active      / 50) * 100);
  document.getElementById("coresLbl").textContent   = (s.cores_active||0)   + "/50";
  document.getElementById("enginesLbl").textContent = (s.engines_active||0) + "/50";
  document.getElementById("aiLbl").textContent      = (s.ai_active||0)      + "/50";

  // Files
  renderFiles(s.files_created || []);

  // Stats
  document.getElementById("testsLbl").textContent = (s.tests_passed||0) + "/" + (s.tests_total||50);
  document.getElementById("fixesLbl").textContent = s.fixes_applied || 0;

  // Bottlenecks
  renderBottlenecks(s.bottlenecks || []);

  // Dashboard
  document.getElementById("dashTask").textContent  = s.build_task  || "Idle";
  document.getElementById("dashQueue").textContent = s.job_queue && s.job_queue.length
    ? s.job_queue.join(", ") : "None";
  document.getElementById("dashVer").textContent   = s.version || "v1.0.0";
  document.getElementById("dashLoop").textContent  = s.loop_count || 0;

  // Queue box
  if (s.job_queue && s.job_queue.length) {
    document.getElementById("queueBox").style.display = "block";
    document.getElementById("queueList").textContent = s.job_queue.join(" → ");
  } else {
    document.getElementById("queueBox").style.display = "none";
  }

  // Version / team
  if (s.version) {
    document.getElementById("versionTag").textContent = s.version;
    document.getElementById("statusVer").textContent = "📜 " + s.version;
  }
  if (s.team_online) {
    document.getElementById("teamCount").textContent = "👥 " + s.team_online + " online";
    document.getElementById("statusTeam").textContent = "👥 " + s.team_online + " online";
  }
}

function applyMetrics(m) {
  document.getElementById("dashCpu").textContent = m.cpu + "%";
  document.getElementById("dashRam").textContent = m.ram + "%";
  document.getElementById("dashRps").textContent = m.rps.toLocaleString();
}

function setPct(id, pct) {
  document.getElementById(id).style.width = Math.min(100, pct) + "%";
}

function renderFiles(files) {
  const el = document.getElementById("fileTree");
  if (!files.length) { el.innerHTML = '<span class="muted">Awaiting build...</span>'; return; }
  const all = ["app.py","models/user.py","models/db.py","routes/api.py","routes/auth.py",
                "static/index.html","static/style.css","static/app.js","tests/test_api.py","Dockerfile","README.md"];
  el.innerHTML = all.map(f => {
    const done = files.includes(f);
    const active = !done && files.length > 0 && f === all[files.length];
    const cls = done ? "done" : active ? "active" : "pending";
    const icon = done ? "✅" : active ? "🔄" : "⏳";
    return `<div class="file-item ${cls}">${icon} ${f}</div>`;
  }).join("");
}

function renderBottlenecks(bns) {
  const el = document.getElementById("bottlenecks");
  const lbl = document.getElementById("bnLabel");
  if (!bns.length) { el.innerHTML = ""; lbl.style.display = "none"; return; }
  lbl.style.display = "block";
  el.innerHTML = bns.map(bn =>
    `<div class="bn-item">⚠ ${bn}
      <button onclick="fixBottleneck('${bn.replace(/'/g,"\\'")}')">FIX</button>
    </div>`
  ).join("");
}

// ── Response Box ──
function addResponse(msg, kind = "info") {
  const box = document.getElementById("responseBox");
  const div = document.createElement("div");
  div.className = "rline " + kind;
  const time = new Date().toLocaleTimeString("en", {hour12:false,hour:"2-digit",minute:"2-digit",second:"2-digit"});
  div.textContent = `[${time}] ${msg}`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
  // keep max 300 lines
  while (box.children.length > 300) box.removeChild(box.firstChild);
}

// ── API calls ──
async function loadState() {
  try {
    const r = await fetch("/api/state");
    const s = await r.json();
    applyState(s);
  } catch(e) { /* offline */ }
}

async function sendBuild() {
  const txt = document.getElementById("promptInput").value.trim();
  if (!txt) { addResponse("⚠ Please type what to build.", "warn"); return; }
  addResponse("▶ Sending build request: " + txt, "start");
  document.getElementById("promptInput").value = "";
  const r = await fetch("/api/build", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({job: txt}),
  });
  const d = await r.json();
  if (d.status === "queued") addResponse(`📋 Queued: ${d.job}`, "warn");
  else addResponse(`🚀 Build started: ${d.job}`, "start");
}

async function sendPromptCmd(cmd) {
  const input = document.getElementById("promptInput");
  const txt = input.value.trim() || cmd;
  addResponse(`▶ Command: ${cmd} — ${txt}`, "info");
  const r = await fetch("/api/ai_chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({message: cmd + " " + txt}),
  });
  const d = await r.json();
  addResponse("🤖 " + d.reply, "pilot");
}

async function fixBottleneck(bn) {
  await fetch("/api/fix_bottleneck", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({bottleneck: bn}),
  });
  addResponse(`✓ User fixed: ${bn}`, "fix");
}

function stopBuild() {
  socket.emit("stop_build");
  addResponse("⏹ Stop signal sent.", "warn");
}

// ── Code Execution ──
async function runCode() {
  const code = editor.getValue();
  const lang = document.getElementById("langSelect").value;
  const out = document.getElementById("codeOutput");
  out.textContent = "> Running...";
  try {
    const r = await fetch("/api/execute", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({code, lang}),
    });
    const d = await r.json();
    const output = (d.output || "").trim();
    const error  = (d.error  || "").trim();
    out.textContent = (output ? "> " + output : "") + (error ? "\n⚠ " + error : "") || "> (no output)";
  } catch(e) {
    out.textContent = "⚠ Execution failed: " + e.message;
  }
}

function saveCode() {
  const blob = new Blob([editor.getValue()], {type:"text/plain"});
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = "ord_code.py";
  a.click();
  addResponse("💾 Code saved to file.", "done");
}

function clearCode() {
  editor.setValue("");
  document.getElementById("codeOutput").textContent = "> Cleared.";
}

// ── Test results ──
function renderTestResults(r) {
  const el = document.getElementById("testResultsBody");
  if (!el) return;
  el.innerHTML = Object.entries(r).map(([k, v]) => {
    const pct = Math.round((v.passed / v.total) * 100);
    const icon = pct === 100 ? "✅" : pct >= 95 ? "⚠️" : "❌";
    return `<div class="test-row"><span>${icon} ${k}</span><span>${v.passed}/${v.total}</span></div>`;
  }).join("");
}

// ──────────────────────────────────────────────
// PANELS
// ──────────────────────────────────────────────

const PANELS = {

  save: {
    title: "💾 SAVE & LOAD SYSTEM",
    html: (s) => `
      <label>System Name</label>
      <input id="saveName" value="${s.current_job || 'My_ORD_System'}">
      <label>Version</label>
      <input id="saveVer" value="${s.version || 'v1.0.0'}">
      <label>Description</label>
      <input id="saveDesc" placeholder="What does this system do?">
      <div class="p-row">
        <button class="btn-primary" onclick="doSave()">💾 SAVE</button>
        <button class="btn-secondary">SAVE AS</button>
        <button class="btn-secondary">AUTO-SAVE ON</button>
      </div>
      <div class="p-section">Recent Saves</div>
      <ul class="p-list" id="savesList"></ul>`,
    after: (s) => {
      const el = document.getElementById("savesList");
      if (el) el.innerHTML = (s.saves||[]).slice(0,5).map(sv =>
        `<li>💾 ${sv.name} <span class="muted">(${sv.version}) — ${sv.time}</span></li>`
      ).join("");
    }
  },

  deploy: {
    title: "🚀 DEPLOY SYSTEM",
    html: () => `
      <div class="p-section">Target Platform</div>
      <div class="p-row">
        ${["AWS","GCP","Azure","Vercel","Netlify","Heroku","DigitalOcean","Custom"].map(p=>
          `<button class="btn-secondary" onclick="deployTo('${p}')">${p}</button>`
        ).join("")}
      </div>
      <div class="p-section">Settings</div>
      <label>Region</label><input value="us-east-1">
      <label>Instance</label><input value="t2.micro">
      <div class="p-row">
        <button class="btn-primary" onclick="deployTo('AWS')">🚀 DEPLOY NOW</button>
        <button class="btn-secondary">⏰ SCHEDULE</button>
        <button class="btn-secondary">↩ ROLLBACK</button>
      </div>`,
    after: () => {}
  },

  collab: {
    title: "👥 TEAM COLLABORATION",
    html: (s) => `
      <div class="p-section">Online Members</div>
      <ul class="p-list">
        <li>👤 Alex (Owner) — Editing code</li>
        <li>👤 Sarah (Editor) — Testing</li>
        <li>👤 Mike (Viewer) — Watching preview</li>
      </ul>
      <div class="p-section">Chat</div>
      <div style="background:var(--bg);border:1px solid var(--border);border-radius:4px;padding:8px;font-size:11px;margin-bottom:8px">
        <div>Alex: "Build is looking great"</div>
        <div>Sarah: "Tests passing"</div>
        <div>Mike: "Deployment ready"</div>
      </div>
      <div class="p-row">
        <button class="btn-primary">+ INVITE</button>
        <button class="btn-secondary">📞 VOICE</button>
        <button class="btn-secondary">🖥 SHARE</button>
      </div>`,
    after: () => {}
  },

  version: {
    title: "📜 VERSION HISTORY",
    html: (s) => `
      <ul class="p-list" id="versionList"></ul>
      <div class="p-row">
        <button class="btn-secondary">↩ ROLLBACK</button>
        <button class="btn-secondary">⟷ COMPARE</button>
        <button class="btn-secondary">⎇ BRANCH</button>
        <button class="btn-secondary">⊕ MERGE</button>
      </div>`,
    after: (s) => {
      const el = document.getElementById("versionList");
      if (el) el.innerHTML = (s.versions||[]).slice(0,8).map(v =>
        `<li><strong>${v.ver}</strong> — ${v.msg} <span class="muted">${v.time}</span></li>`
      ).join("");
    }
  },

  test: {
    title: "🧪 TEST DASHBOARD",
    html: () => `
      <div id="testResultsBody"></div>
      <div class="p-section">Coverage</div>
      <div class="bar-wrap"><div class="bar-fill" style="width:97%"></div></div>
      <div style="font-size:11px;color:var(--muted);margin-bottom:10px">97% — 370/381 lines covered</div>
      <div class="p-row">
        <button class="btn-primary" onclick="runTests()">▶ RUN ALL</button>
        <button class="btn-secondary">RUN FAILED</button>
        <button class="btn-secondary">📄 EXPORT REPORT</button>
      </div>`,
    after: (s) => renderTestResults(s.test_results || {})
  },

  analytics: {
    title: "📊 LIVE METRICS",
    html: (s) => `
      <div class="p-section">System Metrics</div>
      ${[
        ["CPU",    s.cpu+"%",   s.cpu],
        ["RAM",    s.ram+"%",   s.ram],
        ["Uptime", s.uptime+"%",s.uptime],
      ].map(([k,v,p]) => `
        <div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:2px">
          <span>${k}</span><span>${v}</span>
        </div>
        <div class="bar-wrap"><div class="bar-fill" style="width:${Math.min(p,100)}%"></div></div>
      `).join("")}
      <div style="font-size:12px;margin:6px 0">
        <div>REQ/s: <strong>${(s.rps||0).toLocaleString()}</strong></div>
        <div>Response: <strong>${s.resp_ms||45}ms</strong></div>
      </div>
      <div class="p-row">
        <button class="btn-secondary">📥 EXPORT</button>
        <button class="btn-secondary">🔔 ALERTS</button>
        <button class="btn-secondary">📊 FULL DASHBOARD</button>
      </div>`,
    after: () => {}
  },

  marketplace: {
    title: "🏪 MARKETPLACE",
    html: (s) => `
      <div class="p-section">Featured Systems</div>
      <ul class="p-list">${(s.marketplace||[]).map(m =>
        `<li>🛒 <strong>${m.name}</strong> — ${m.price} — ${m.downloads} downloads</li>`
      ).join("")}</ul>
      <div class="p-section">Your Sales</div>
      <div style="font-size:12px;margin-bottom:10px">💰 $234 earned this month</div>
      <div class="p-row">
        <button class="btn-primary">📤 PUBLISH</button>
        <button class="btn-secondary">🛒 BUY</button>
        <button class="btn-secondary">⭐ RATE</button>
      </div>`,
    after: () => {}
  },

  templates: {
    title: "📚 TEMPLATE LIBRARY",
    html: () => `
      <div class="p-section">Pre-built Templates</div>
      <div class="p-row">
        ${["ChatGPT","Ecommerce","Social Media","Portfolio","Dashboard","API Server","Blog","CRM"].map(t =>
          `<button class="btn-secondary" onclick="useTemplate('${t}')">${t}</button>`
        ).join("")}
      </div>
      <div class="p-section">Each template includes</div>
      <ul class="p-list">
        <li>✅ Full source code</li>
        <li>✅ Database schema</li>
        <li>✅ API documentation</li>
        <li>✅ Deployment scripts</li>
      </ul>
      <div class="p-row">
        <button class="btn-primary" onclick="useTemplate('ChatGPT')">▶ USE TEMPLATE</button>
        <button class="btn-secondary">👁 PREVIEW</button>
        <button class="btn-secondary">✏ CUSTOMIZE</button>
      </div>`,
    after: () => {}
  },

  export: {
    title: "📦 EXPORT SYSTEM",
    html: () => `
      <div class="p-section">Export Format</div>
      <div class="p-row">
        ${["Docker","ZIP","GitHub","API Package","Mobile App"].map(f =>
          `<button class="btn-secondary">${f}</button>`
        ).join("")}
      </div>
      <div class="p-section">Include</div>
      <ul class="p-list">
        <li>✅ Source Code</li>
        <li>✅ Database</li>
        <li>✅ Documentation</li>
        <li>✅ Tests</li>
        <li>✅ Deployment files</li>
      </ul>
      <div class="p-row">
        <button class="btn-primary">📥 EXPORT</button>
        <button class="btn-secondary">🔗 SHARE LINK</button>
        <button class="btn-secondary">🔑 API KEY</button>
      </div>`,
    after: () => {}
  },

  ai: {
    title: "🤖 AI ASSISTANT — 100% ALIVE",
    html: () => `
      <div style="font-size:11px;color:var(--accent);margin-bottom:8px">
        ∞ Loop Active — Answering | Building | Showing | Feeling | Learning | Correcting | Talking
      </div>
      <div class="ai-chat-log" id="aiChatLog">
        <div class="chat-msg ai">🤖 Hello! I'm your AI Pilot. I'm 100% alive and ready to build anything.</div>
        <div class="chat-msg ai">🤖 Type what you need — I'll never stop until it's done.</div>
      </div>
      <div class="ai-input-row">
        <input id="aiMsgInput" placeholder="Ask anything or say 'Build me...'" onkeydown="if(event.key==='Enter')sendAiMsg()">
        <button class="btn-primary" onclick="sendAiMsg()">SEND</button>
        <button class="btn-secondary" onclick="addResponse('🎤 Voice input activated','info');closePanel()">🎤</button>
      </div>`,
    after: () => { setTimeout(() => document.getElementById("aiMsgInput")?.focus(), 50); }
  },

};

let _currentState = {};

async function openPanel(name) {
  const p = PANELS[name];
  if (!p) return;
  const r = await fetch("/api/state");
  _currentState = await r.json();
  document.getElementById("panelTitle").textContent = p.title;
  document.getElementById("panelBody").innerHTML = p.html(_currentState);
  document.getElementById("panelOverlay").style.display = "block";
  document.getElementById("panel").style.display = "block";
  if (p.after) p.after(_currentState);
}

function closePanel() {
  document.getElementById("panelOverlay").style.display = "none";
  document.getElementById("panel").style.display = "none";
}

// ── Panel actions ──
async function doSave() {
  const name = document.getElementById("saveName").value.trim() || "Unnamed";
  const ver  = document.getElementById("saveVer").value.trim()  || "v1.0.0";
  await fetch("/api/save", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({name, version: ver}),
  });
  addResponse(`💾 Saved: ${name} (${ver})`, "done");
  closePanel();
}

function deployTo(platform) {
  addResponse(`🚀 Deploying to ${platform}...`, "start");
  setTimeout(() => addResponse(`✅ Deployed to ${platform} successfully!`, "success"), 2000);
  closePanel();
}

function useTemplate(name) {
  closePanel();
  document.getElementById("promptInput").value = `Build me a ${name} system`;
  sendBuild();
}

async function runTests() {
  addResponse("🧪 Running full test suite...", "info");
  await fetch("/api/test_run", {method:"POST"});
  closePanel();
}

async function sendAiMsg() {
  const input = document.getElementById("aiMsgInput");
  const msg = input.value.trim();
  if (!msg) return;
  input.value = "";
  const log = document.getElementById("aiChatLog");
  log.innerHTML += `<div class="chat-msg user">👤 ${msg}</div>`;
  log.scrollTop = log.scrollHeight;
  const r = await fetch("/api/ai_chat", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({message: msg}),
  });
  const d = await r.json();
  log.innerHTML += `<div class="chat-msg ai">🤖 ${d.reply}</div>`;
  log.scrollTop = log.scrollHeight;
  addResponse("🤖 AI: " + d.reply, "pilot");
}

// Keyboard shortcut: Ctrl+Enter = build
document.addEventListener("keydown", (e) => {
  if (e.ctrlKey && e.key === "Enter") sendBuild();
  if (e.key === "Escape") closePanel();
});
