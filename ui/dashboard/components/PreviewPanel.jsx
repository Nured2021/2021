import React, { useEffect } from 'react';
import api from '../api';

export default function PreviewPanel() {
  useEffect(() => {
    // Auto-open live preview on mount
    api.get('/preview/live');
  }, []);
  return <div className="preview-panel">Live Preview Window (auto-opened)</div>;
}
