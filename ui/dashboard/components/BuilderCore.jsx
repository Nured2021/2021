import React from 'react';

export default function BuilderCore({
  activeModule,
  healthStatus,
  healthError,
  engineItems = [],
  prompt = '',
  steps = [],
  logs = [],
  files = [],
  isRunning,
  isPaused,
  onPromptChange,
  onStart,
  onStop,
  onContinue,
}) {
  return (
    <div className="builder-core">
      <div className="builder-toolbar">
        <div className="builder-module">Active: {activeModule}</div>
        <div className="builder-actions">
          <button type="button" onClick={onStart} disabled={isRunning}>
            Start
          </button>
          <button type="button" onClick={onStop} disabled={!isRunning}>
            Stop
          </button>
          <button type="button" onClick={onContinue} disabled={!isPaused}>
            Continue
          </button>
        </div>
      </div>

      <div className="builder-health-row">
        <span className={`builder-health-pill ${healthStatus === 'healthy' ? 'ok' : 'warn'}`}>
          Health: {healthStatus}
        </span>
        {healthError ? <span className="builder-health-error">{healthError}</span> : null}
      </div>

      <div className="builder-prompt">
        <textarea
          value={prompt}
          onChange={(e) => onPromptChange(e.target.value)}
          placeholder="Describe what you want to build..."
        />
      </div>

      <div className="builder-live">
        <div className="builder-steps">
          <h3>AI Thinking</h3>
          <ul>
            {steps.map((step) => (
              <li key={step.name} className={`step-${step.status}`}>
                <strong>{step.name}</strong>
                <span>{step.status}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="builder-stream">
          <h3>Live Stream</h3>
          <div className="stream-box">
            {logs.length ? (
              logs.map((line, i) => <div key={`${line}-${i}`}>{line}</div>)
            ) : (
              <div className="stream-empty">Waiting for build stream...</div>
            )}
          </div>
        </div>

        <div className="builder-files">
          <h3>Files Created</h3>
          <div className="files-box">
            {files.length ? (
              files.map((file, i) => <div key={`${file}-${i}`}>{file}</div>)
            ) : (
              <div className="stream-empty">No files reported yet</div>
            )}
          </div>
        </div>

        <div className="builder-files">
          <h3>Engines</h3>
          <div className="files-box">
            {engineItems.length ? (
              engineItems.map((engine, i) => (
                <div key={`${engine.name || 'engine'}-${i}`}>
                  {engine.name || 'Unknown Engine'} — active
                </div>
              ))
            ) : (
              <div className="stream-empty">No engines reported</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
