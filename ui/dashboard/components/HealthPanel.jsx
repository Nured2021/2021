import React, { useEffect, useState } from 'react';
import api from '../api';

export default function HealthPanel() {
  const [health, setHealth] = useState(null);
  useEffect(() => {
    api.get('/health').then(res => setHealth(res.data));
  }, []);
  return <div className="panel health">Health: {health ? health.status : 'Loading...'}</div>;
}
