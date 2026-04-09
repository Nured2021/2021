import React, { useEffect, useState } from 'react';
import api from '../api';

export default function EnginesPanel() {
  const [engines, setEngines] = useState([]);
  useEffect(() => {
    api.get('/engines').then(res => setEngines(res.data));
  }, []);
  return <div className="panel engines">Engines: {engines.length}</div>;
}
