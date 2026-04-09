import React, { useEffect, useState } from 'react';
import LoginRegister from './LoginRegister';
import UserPanel from './UserPanel';
import AdminPanel from './AdminPanel';
import api from '../api';

export default function AppRouter() {
  const [role, setRole] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/auth/me').then(res => {
      setRole(res.data.role);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;
  if (!role) return <LoginRegister setRole={setRole} />;
  if (role === 'admin') return <AdminPanel />;
  return <UserPanel />;
}
