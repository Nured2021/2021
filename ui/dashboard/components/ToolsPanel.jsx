import React, { useEffect, useState } from 'react';
import api from '../api';

export default function ToolsPanel() {
  const [tools, setTools] = useState([]);
  useEffect(() => {
    api.get('/tools').then(res => setTools(res.data));
  }, []);
  return <div className="panel tools">Tools: {tools.length}</div>;
}
