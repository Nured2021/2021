import React, { useEffect, useMemo, useState } from 'react';
import api from '../api';

export default function LiveLogsPanel() {
  const [logs, setLogs] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    const poll = () => {
      api
        .get('/logs')
        .then((res) => {
          if (!mounted) return;
          const value = Array.isArray(res.data) ? res.data : [];
          setLogs(value);
          setError('');
        })
        .catch((err) => {
          if (!mounted) return;
          setError(err?.message || 'Unable to load logs');
        });
    };

    poll();
    const timer = setInterval(poll, 3000);
    return () => {
      mounted = false;
      clearInterval(timer);
    };
  }, []);

  const preview = useMemo(() => logs.slice(0, 8), [logs]);

  return (
    <div className="panel live-logs-panel">
      <h3>Live Logs</h3>
      {error ? <p className="error">Error: {error}</p> : null}
      {!preview.length ? (
        <p>Waiting for activity...</p>
      ) : (
        <ul>
          {preview.map((log, idx) => (
            <li key={`${log?.event || 'log'}-${idx}`}>{log?.event || JSON.stringify(log)}</li>
          ))}
        </ul>
      )}
    </div>
  );
}
