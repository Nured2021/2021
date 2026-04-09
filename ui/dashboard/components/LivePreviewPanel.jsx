import React, { useEffect, useState } from 'react';
import api from '../api';

export default function LivePreviewPanel() {
  const [preview, setPreview] = useState('Loading preview...');

  useEffect(() => {
    api.get('/preview/live')
      .then((res) => setPreview(res.data?.preview || 'Preview connected'))
      .catch(() => setPreview('Preview unavailable'));
  }, []);

  return (
    <div className="panel live-preview-panel">
      <h3>Live Preview</h3>
      <iframe
        title="ODEX Live Preview"
        src="about:blank"
        style={{ width: '100%', height: '180px', border: '1px solid #2f3a56', borderRadius: 8 }}
      />
      <p>{preview}</p>
    </div>
  );
}
