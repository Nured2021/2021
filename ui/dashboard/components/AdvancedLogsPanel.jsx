import React, { useEffect, useState } from 'react';
import api from '../api';

export default function AdvancedLogsPanel() {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    api.get('/logs?advanced=1').then(res => setLogs(res.data));
  }, []);
  return <div className="panel advanced-logs">Advanced Logs: {logs.length}</div>;
}
