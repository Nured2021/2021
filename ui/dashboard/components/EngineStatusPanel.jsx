import React, { useEffect, useState } from 'react';
import api from '../api';

export default function EngineStatusPanel() {
  const [engines, setEngines] = useState([]);
  const [engineMeta, setEngineMeta] = useState({ status: 'idle', total: 0 });
  const [brainCount, setBrainCount] = useState(0);

  useEffect(() => {
    let mounted = true;
    Promise.all([api.get('/engines'), api.get('/engine-brains')])
      .then(([enginesRes, brainsRes]) => {
        if (!mounted) return;
        const enginePayload = enginesRes.data || {};
        const items = Array.isArray(enginePayload) ? enginePayload : (enginePayload.items || []);
        setEngines(items);
        setEngineMeta({
          status: enginePayload.status || 'active',
          total: enginePayload.total || items.length,
        });
        setBrainCount(brainsRes.data?.count || 0);
      })
      .catch(() => {
        if (!mounted) return;
        setEngines([]);
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="panel engine-status-panel">
      <h3>Engine Status</h3>
      <p>System: {engineMeta.status}</p>
      <p>Total Brains: {engineMeta.total}</p>
      <p>Core Engines: {engines.length}</p>
      <p>Engine Brains: {brainCount}</p>
      <ul>
        {engines.map((engine, idx) => (
          <li key={`${engine.name}-${idx}`}>
            <strong>{engine.name}</strong> — active
          </li>
        ))}
      </ul>
    </div>
  );
}
