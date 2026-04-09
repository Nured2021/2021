import React, { useState } from 'react';
import api from '../api';

export default function HumanLoopPanel() {
  const [stage, setStage] = useState('Human-in-the-decision-loop');
  const [context, setContext] = useState('dashboard_manual_trigger');
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const trigger = async () => {
    try {
      const payload = { stage, context };
      const res = await api.post('/human-loop', payload);
      setResult(res.data);
      setError('');
    } catch (err) {
      setError(err?.message || 'Failed to trigger human loop');
    }
  };

  return (
    <div className="panel human-loop-panel">
      <h3>Human Loop Panel</h3>
      <label>
        Stage
        <input
          value={stage}
          onChange={(e) => setStage(e.target.value)}
          style={{ width: '100%', marginTop: 4, marginBottom: 8 }}
        />
      </label>
      <label>
        Context
        <input
          value={context}
          onChange={(e) => setContext(e.target.value)}
          style={{ width: '100%', marginTop: 4, marginBottom: 8 }}
        />
      </label>
      <button onClick={trigger} type="button">Activate Human Loop</button>
      {error ? <p className="error">{error}</p> : null}
      {result ? (
        <div style={{ marginTop: 8 }}>
          <p>Active Brain: {result.active_brain}</p>
          <p>Status: {result.status}</p>
          <pre style={{ whiteSpace: 'pre-wrap', overflowWrap: 'anywhere' }}>
            {JSON.stringify(result.context, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}
