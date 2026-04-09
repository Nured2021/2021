import React, { useEffect, useState } from 'react';
import api from '../api';

export default function PreviewPanel({ previewUrl }) {
  const [resolvedUrl, setResolvedUrl] = useState(previewUrl || 'about:blank');
  const [label, setLabel] = useState('Live preview');

  useEffect(() => {
    let mounted = true;
    api
      .get('/preview/live')
      .then((res) => {
        if (!mounted) return;
        const url = previewUrl || res.data?.url || 'about:blank';
        setResolvedUrl(url);
        setLabel(res.data?.preview || 'Live preview connected');
      })
      .catch(() => {
        if (!mounted) return;
        setResolvedUrl(previewUrl || 'about:blank');
        setLabel('Preview unavailable');
      });
    return () => {
      mounted = false;
    };
  }, [previewUrl]);

  return (
    <div className="preview-panel">
      <div className="preview-panel-header">
        <div>Live Preview</div>
        <div className="preview-url">{resolvedUrl}</div>
      </div>
      <iframe title="ODEX Preview" src={resolvedUrl} className="preview-frame" />
      <div className="preview-label">{label}</div>
    </div>
  );
}
