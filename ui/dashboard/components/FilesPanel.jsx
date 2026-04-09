import React, { useEffect, useState } from 'react';
import api from '../api';

export default function FilesPanel() {
  const [files, setFiles] = useState([]);
  useEffect(() => {
    api.get('/files').then(res => setFiles(res.data));
  }, []);
  return <div className="panel files">Files: {files.length}</div>;
}
