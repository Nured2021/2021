import React, { useEffect, useState } from 'react';
import api from '../api';

export default function LogsPanel() {
  const [logs, setLogs] = useState([]);
  useEffect(() => {
    api.get('/logs').then(res => setLogs(res.data));
  }, []);
  return <div className="panel logs">Logs: {logs.length}</div>;
}
