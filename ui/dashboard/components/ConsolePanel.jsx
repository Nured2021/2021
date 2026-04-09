import React from 'react';

export default function ConsolePanel({ lines = [], error }) {
  return (
    <div className="console-panel">
      <div className="console-header">Console</div>
      <div className="console-body">
        {error ? <div className="console-line console-error">[error] {error}</div> : null}
        {lines.length ? (
          lines.map((line, idx) => (
            <div key={`${idx}-${line}`} className="console-line">
              {line}
            </div>
          ))
        ) : (
          <div className="console-line">No logs yet...</div>
        )}
      </div>
    </div>
  );
}
