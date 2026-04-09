import React, { useEffect, useMemo, useState } from 'react';
import api from '../api';

export default function AutoSystemPanel() {
  const [systemData, setSystemData] = useState(null);
  const [nexusStatus, setNexusStatus] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;

    Promise.all([api.get('/auto-system'), api.get('/nexus/action')])
      .then(([systemRes, nexusRes]) => {
        if (!mounted) return;
        setSystemData(systemRes.data);
        setNexusStatus(nexusRes.data);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err?.message || 'Failed to connect auto system');
      });

    return () => {
      mounted = false;
    };
  }, []);

  const counters = useMemo(() => {
    if (!systemData) {
      return {
        brains: 0,
        routes: 0,
        components: 0,
        panels: 0,
      };
    }
    return {
      brains: systemData?.system?.brains || 0,
      routes: systemData?.routes?.length || 0,
      components: systemData?.components?.length || 0,
      panels: systemData?.panels?.length || 0,
    };
  }, [systemData]);

  return (
    <div className="panel auto-system">
      <h3>ODEX Auto System</h3>
      {error ? <p className="error">Connection error: {error}</p> : null}
      <p>Status: {systemData?.system?.status || 'connecting...'}</p>
      <p>Mode: {systemData?.system?.mode || 'auto'}</p>
      <p>Brains: {counters.brains}</p>
      <p>Routes: {counters.routes}</p>
      <p>Components: {counters.components}</p>
      <p>Panels: {counters.panels}</p>
      <p>Nexus route: {nexusStatus?.status || 'pending'}</p>
    </div>
  );
}
