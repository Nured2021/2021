import React, { useEffect, useMemo, useRef, useState } from 'react';
import Sidebar from './components/Sidebar';
import BuilderCore from './components/BuilderCore';
import PreviewPanel from './components/PreviewPanel';
import ConsolePanel from './components/ConsolePanel';

const DEFAULT_STEPS = ['Plan', 'Build', 'Fix', 'Test'];
const BACKEND_URL = 'http://localhost:8080';

function formatLogEntry(entry) {
  if (typeof entry === 'string') return entry;
  if (!entry) return '';
  const engine = entry.engine ? `[${entry.engine}] ` : '';
  const stage = entry.stage ? `${entry.stage}: ` : '';
  const message = entry.message || entry.event || JSON.stringify(entry);
  return `${engine}${stage}${message}`;
}

export default function BuilderWorkspace() {
  const [activeModule, setActiveModule] = useState('Files');
  const [prompt, setPrompt] = useState('');
  const [steps, setSteps] = useState(DEFAULT_STEPS.map((name) => ({ name, status: 'idle' })));
  const [logs, setLogs] = useState([]);
  const [consoleLines, setConsoleLines] = useState(['[system] ODEX Builder initialized']);
  const [files, setFiles] = useState([]);
  const [previewUrl, setPreviewUrl] = useState('http://localhost:5173');
  const [engines, setEngines] = useState([]);
  const [backendStatus, setBackendStatus] = useState('checking');
  const [backendError, setBackendError] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  const streamTimerRef = useRef(null);
  const streamCursorRef = useRef(0);
  const streamPayloadRef = useRef({ logs: [], steps: [] });

  const modules = useMemo(
    () => ['Files', 'Engines', 'Pipeline', 'Logs', 'Workers', 'Settings'],
    []
  );

  useEffect(() => {
    let mounted = true;

    const loadBackendState = async () => {
      try {
        const [healthRes, enginesRes] = await Promise.all([
          fetch(`${BACKEND_URL}/api/health`),
          fetch(`${BACKEND_URL}/api/engines`),
        ]);

        if (!healthRes.ok) {
          throw new Error(`Health check failed (${healthRes.status})`);
        }

        const healthJson = await healthRes.json();
        const enginesJson = enginesRes.ok ? await enginesRes.json() : {};
        const list = Array.isArray(enginesJson?.items) ? enginesJson.items : [];

        if (!mounted) return;
        setBackendStatus(healthJson?.status || 'healthy');
        setEngines(list);
        setBackendError('');
        setConsoleLines((prev) => [...prev, `[system] Backend status: ${healthJson?.status || 'healthy'}`]);
      } catch (err) {
        if (!mounted) return;
        const msg = err?.message || 'Backend unavailable';
        setBackendStatus('offline');
        setBackendError(msg);
        setConsoleLines((prev) => [...prev, `[error] ${msg}`]);
      }
    };

    loadBackendState();
    return () => {
      mounted = false;
    };
  }, []);

  const clearStreamTimer = () => {
    if (streamTimerRef.current) {
      clearInterval(streamTimerRef.current);
      streamTimerRef.current = null;
    }
  };

  const appendConsole = (line) => {
    if (!line) return;
    setConsoleLines((prev) => [...prev.slice(-300), line]);
  };

  const advanceStream = () => {
    const logs = streamPayloadRef.current.logs;
    const stepNames = streamPayloadRef.current.steps;
    const idx = streamCursorRef.current;

    if (idx >= logs.length) {
      clearStreamTimer();
      setIsRunning(false);
      setIsPaused(false);
      setSteps(stepNames.map((name) => ({ name, status: 'done' })));
      appendConsole('[system] Build completed');
      return;
    }

    const line = logs[idx];
    setLogs((prev) => [...prev, line]);
    appendConsole(line);

    const stepIndex = Math.min(idx, stepNames.length - 1);
    setSteps(stepNames.map((name, i) => ({ name, status: i < stepIndex ? 'done' : i === stepIndex ? 'running' : 'idle' })));

    streamCursorRef.current += 1;
  };

  const startStreaming = () => {
    clearStreamTimer();
    streamTimerRef.current = setInterval(advanceStream, 700);
  };

  const handleStart = async () => {
    const input = prompt.trim();
    if (!input || isRunning) return;

    setIsRunning(true);
    setIsPaused(false);
    setLogs([]);
    setFiles([]);
    setSteps(DEFAULT_STEPS.map((name, i) => ({ name, status: i === 0 ? 'running' : 'idle' })));
    appendConsole(`[build] Starting build for prompt: "${input}"`);

    try {
      const response = await fetch(`${BACKEND_URL}/build`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: input }),
      });

      if (!response.ok) {
        throw new Error(`Build API failed (${response.status})`);
      }

      const payload = await response.json();
      const incomingSteps = Array.isArray(payload.steps) && payload.steps.length
        ? payload.steps
        : DEFAULT_STEPS;
      const incomingLogs = Array.isArray(payload.logs)
        ? payload.logs.map(formatLogEntry)
        : [];

      setFiles(Array.isArray(payload.files) ? payload.files : []);
      if (payload.preview_url) setPreviewUrl(payload.preview_url);

      streamPayloadRef.current = {
        steps: incomingSteps,
        logs: incomingLogs.length ? incomingLogs : ['[system] Build completed with no log output'],
      };
      streamCursorRef.current = 0;
      setSteps(incomingSteps.map((name, i) => ({ name, status: i === 0 ? 'running' : 'idle' })));
      startStreaming();
    } catch (err) {
      const msg = err?.message || 'Unknown build error';
      appendConsole(`[error] ${msg}`);
      setIsRunning(false);
      setIsPaused(false);
      setSteps(DEFAULT_STEPS.map((name) => ({ name, status: 'idle' })));
    }
  };

  const handleStop = () => {
    clearStreamTimer();
    setIsRunning(false);
    setIsPaused(true);
    appendConsole('[build] Streaming paused by user');
  };

  const handleContinue = () => {
    if (!isPaused) return;
    setIsRunning(true);
    setIsPaused(false);
    appendConsole('[build] Streaming resumed');
    startStreaming();
  };

  return (
    <div className="builder-workspace">
      <div className="builder-main">
        <aside className="builder-sidebar-shell">
          <Sidebar
            activeModule={activeModule}
            modules={modules}
            onSelect={setActiveModule}
            engines={engines}
            backendStatus={backendStatus}
          />
        </aside>
        <section className="builder-center-shell">
          {backendError ? (
            <div className="builder-error-banner">Backend connection error: {backendError}</div>
          ) : null}
          <BuilderCore
            activeModule={activeModule}
            healthStatus={backendStatus}
            healthError={backendError}
            engineItems={engines}
            prompt={prompt}
            steps={steps}
            logs={logs}
            files={files}
            isPaused={isPaused}
            isRunning={isRunning}
            onContinue={handleContinue}
            onPromptChange={setPrompt}
            onStart={handleStart}
            onStop={handleStop}
          />
        </section>
        <aside className="builder-preview-shell">
          <PreviewPanel previewUrl={previewUrl} />
        </aside>
      </div>
      <footer className="builder-console-shell">
        <ConsolePanel lines={consoleLines} />
      </footer>
    </div>
  );
}
