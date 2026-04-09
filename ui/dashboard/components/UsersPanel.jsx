import React, { useEffect, useState } from 'react';
import api from '../api';

export default function UsersPanel() {
  const [users, setUsers] = useState([]);
  useEffect(() => {
    api.get('/users').then(res => setUsers(res.data));
  }, []);
  return <div className="panel users">Users: {users.length}</div>;
}
