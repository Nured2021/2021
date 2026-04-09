import React, { useEffect, useState } from 'react';
import api from '../api';

export default function BillingPanel() {
  const [billing, setBilling] = useState(null);
  useEffect(() => {
    api.get('/billing').then(res => setBilling(res.data));
  }, []);
  return <div className="panel billing">Billing: {billing ? billing.status : 'Loading...'}</div>;
}
