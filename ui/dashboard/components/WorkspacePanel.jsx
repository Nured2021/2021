import React, { useEffect, useState } from 'react';
import api from '../api';

export default function WorkspacePanel() {
  const [workspace, setWorkspace] = useState(null);
  useEffect(() => {
    api.get('/workspace').then(res => setWorkspace(res.data));
  }, []);
  return <div className="panel workspace">Workspace: {workspace ? workspace.name : 'Loading...'}</div>;
}
