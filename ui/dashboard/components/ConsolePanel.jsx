import React from 'react';

export default function ConsolePanel({ lines = [] }) {
  return (
    <div className="console-panel">
      <div className="console-header">Console</div>
      <div className="console-body">
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
