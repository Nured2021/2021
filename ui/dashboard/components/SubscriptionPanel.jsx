import React, { useEffect, useState } from 'react';
import api from '../api';

export default function SubscriptionPanel() {
  const [sub, setSub] = useState(null);
  useEffect(() => {
    api.get('/subscription').then(res => setSub(res.data));
  }, []);
  return <div className="panel subscription">Subscription: {sub ? sub.status : 'Loading...'}</div>;
}
