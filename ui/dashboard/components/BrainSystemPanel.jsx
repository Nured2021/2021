import { useEffect, useState } from 'react';
import api from '../api';

export default function BrainSystemPanel() {
  const [brains, setBrains] = useState([]);
  const [count, setCount] = useState(0);
  const [status, setStatus] = useState('loading');
  const [stabilizeResult, setStabilizeResult] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    const load = async () => {
      try {
        const res = await api.get('/brains');
        if (!mounted) return;
        setBrains(Array.isArray(res.data?.brains) ? res.data.brains : []);
        setCount(res.data?.count || 0);
        setStatus(res.data?.status || 'active');
      } catch (err) {
        if (!mounted) return;
        setError(err?.message || 'Failed to load brain system');
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const runStabilize = async () => {
    try {
      const res = await api.post('/brains/stabilize');
      setStabilizeResult(res.data);
      setError('');
    } catch (err) {
      setError(err?.message || 'Stabilization failed');
    }
  };

  return (
    <div className="panel brain-system-panel">
      <h3>Brain System</h3>
      <p>Total Brains: {count}</p>
      <p>Status: {status}</p>
      <button type="button" onClick={runStabilize}>
        Stabilize
      </button>
      {stabilizeResult ? (
        <p>
          Stabilized: {stabilizeResult.status} (missing: {stabilizeResult.missing}, total:{' '}
          {stabilizeResult.total})
        </p>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
      <ul className="logs-list">
        {brains.map((brain) => (
          <li key={brain}>{brain}</li>
        ))}
      </ul>
    </div>
  );
}
