import React, { useEffect, useMemo, useState } from 'react';
import api from '../api';

export default function OdexReplitStyleBuilder() {
  const leftNav = [
    'Home',
    'Repls',
    'Deployments',
    'Usage',
    'Teams',
    'Bounties',
    'Templates',
    'Extensions',
    'Learn',
    'Documentation',
  ];

  const [health, setHealth] = useState('checking');
  const [cards, setCards] = useState([]);
  const [brains, setBrains] = useState([]);
  const [tools, setTools] = useState({});
  const [recentProjects, setRecentProjects] = useState([]);
  const [previewUrl, setPreviewUrl] = useState('about:blank');

  useEffect(() => {
    let mounted = true;

    Promise.allSettled([
      api.get('/health'),
      api.get('/dashboard/cards'),
      api.get('/brains'),
      api.get('/tools'),
      api.get('/projects'),
      api.get('/preview/live'),
    ]).then((results) => {
      if (!mounted) return;

      const [healthRes, cardsRes, brainsRes, toolsRes, projectsRes, previewRes] = results;

      if (healthRes.status === 'fulfilled') {
        setHealth(healthRes.value?.data?.status || 'healthy');
      } else {
        setHealth('offline');
      }

      if (cardsRes.status === 'fulfilled') {
        setCards(Array.isArray(cardsRes.value?.data) ? cardsRes.value.data : []);
      }

      if (brainsRes.status === 'fulfilled') {
        const data = brainsRes.value?.data;
        if (Array.isArray(data?.brains)) {
          setBrains(data.brains);
        } else if (Array.isArray(data)) {
          setBrains(data);
        }
      }

      if (toolsRes.status === 'fulfilled') {
        setTools(toolsRes.value?.data || {});
      }

      if (projectsRes.status === 'fulfilled') {
        const projects = Array.isArray(projectsRes.value?.data) ? projectsRes.value.data : [];
        const mapped = projects.slice(0, 6).map((p, i) => ({
          name: p?.name || `Project-${i + 1}`,
          status: 'Updated recently',
        }));
        setRecentProjects(mapped);
      }

      if (previewRes.status === 'fulfilled') {
        setPreviewUrl(previewRes.value?.data?.url || 'about:blank');
      }
    });

    return () => {
      mounted = false;
    };
  }, []);

  const chips = useMemo(() => {
    const names = cards.slice(0, 4).map((c) => c?.name).filter(Boolean);
    return names.length ? names : ['System Health', 'Engine Brains', 'Human Loop', 'View more'];
  }, [cards]);

  const totalTools = useMemo(
    () => Object.values(tools).reduce((acc, list) => acc + (Array.isArray(list) ? list.length : 0), 0),
    [tools],
  );

  return (
    <div style={{ width: '100%', background: '#f5f5f7', color: '#111', borderRadius: 12, overflow: 'hidden' }}>
      <header style={{ height: 48, borderBottom: '1px solid #ddd', background: '#fff', display: 'flex', alignItems: 'center', padding: '0 12px', gap: 12 }}>
        <div style={{ width: 28, height: 28, borderRadius: 6, border: '1px solid #ddd', background: '#fafafa', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 12 }}>≡</div>
        <div style={{ fontSize: 14, fontWeight: 600 }}>odex.ai</div>
        <div style={{ flex: 1, display: 'flex', justifyContent: 'center' }}>
          <div style={{ width: 520, maxWidth: '100%', height: 34, borderRadius: 8, border: '1px solid #ddd', background: '#fafafa', display: 'flex', alignItems: 'center', padding: '0 12px', color: '#666', fontSize: 13 }}>
            Search & run commands
            <span style={{ marginLeft: 'auto', fontSize: 11, border: '1px solid #ddd', borderRadius: 4, padding: '2px 6px', background: '#fff' }}>Ctrl I</span>
          </div>
        </div>
        <div style={{ width: 28, height: 28, borderRadius: '50%', background: '#ececec' }} />
      </header>

      <div style={{ display: 'flex', minHeight: 740 }}>
        <aside style={{ width: 248, borderRight: '1px solid #ddd', background: '#f8f8f8', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: 12, borderBottom: '1px solid #e5e5e5', display: 'grid', gap: 8 }}>
            <button style={{ width: '100%', borderRadius: 10, background: '#fff', border: '1px solid #d8d8d8', height: 40, fontSize: 13, fontWeight: 600 }}>+ Create Repl</button>
            <button style={{ width: '100%', borderRadius: 10, background: '#fff', border: '1px solid #d8d8d8', height: 40, fontSize: 13 }}>Import from GitHub</button>
          </div>

          <div style={{ padding: 12, fontSize: 11, textTransform: 'uppercase', letterSpacing: 0.7, color: '#777' }}>Workspace</div>
          <nav style={{ padding: '0 8px', display: 'grid', gap: 4 }}>
            {leftNav.map((item, i) => (
              <div key={item} style={{ height: 36, borderRadius: 10, padding: '0 12px', display: 'flex', alignItems: 'center', fontSize: 13, background: i === 0 ? '#fff' : 'transparent', border: i === 0 ? '1px solid #ddd' : '1px solid transparent' }}>
                {item}
              </div>
            ))}
          </nav>

          <div style={{ marginTop: 'auto', padding: 12, fontSize: 12, color: '#777', borderTop: '1px solid #e5e5e5' }}>
            ODEX Builder Workspace
            <div style={{ marginTop: 6, fontWeight: 600, color: health === 'healthy' ? '#0a7d2e' : '#b45309' }}>
              Backend: {health}
            </div>
          </div>
        </aside>

        <main style={{ flex: 1, minWidth: 0, overflow: 'auto' }}>
          <div style={{ maxWidth: 980, margin: '0 auto', padding: 24 }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
              <button style={{ height: 32, padding: '0 12px', borderRadius: 8, background: '#2f7cf6', color: '#fff', fontSize: 13, border: 'none' }}>+ Create Repl</button>
              <button style={{ height: 32, padding: '0 12px', borderRadius: 8, border: '1px solid #ddd', background: '#fff', fontSize: 13 }}>Create Next.js</button>
            </div>

            <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={{ fontSize: 22, fontWeight: 700 }}>ODEX Builder Agent</div>
              <span style={{ fontSize: 11, borderRadius: 999, background: '#efe7ff', color: '#6a45c6', padding: '4px 8px' }}>System access</span>
              <span style={{ fontSize: 11, borderRadius: 999, background: '#e8fff1', color: '#16703b', padding: '4px 8px' }}>
                Brains: {brains.length}
              </span>
              <span style={{ fontSize: 11, borderRadius: 999, background: '#e9f1ff', color: '#1f4fa3', padding: '4px 8px' }}>
                Tools: {totalTools}
              </span>
            </div>

            <div style={{ borderRadius: 12, border: '1px solid #d8d8d8', background: '#fff', padding: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.08)' }}>
              <div style={{ border: '1px solid #d9d9d9', borderRadius: 8, minHeight: 74, padding: '12px 14px', fontSize: 13, color: '#777', background: '#fcfcfc' }}>
                Describe what you want to build
              </div>
              <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                {chips.map((chip) => (
                  <button key={chip} style={{ height: 32, padding: '0 12px', borderRadius: 999, border: '1px solid #ddd', background: '#fff', fontSize: 13, color: '#444' }}>
                    {chip}
                  </button>
                ))}
                <button style={{ marginLeft: 'auto', height: 36, padding: '0 16px', borderRadius: 10, background: '#e8dbff', color: '#6d40d6', fontSize: 13, fontWeight: 600, border: 'none' }}>
                  Start building
                </button>
              </div>
            </div>

            <div style={{ marginTop: 30 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
                <div style={{ fontSize: 18, fontWeight: 600 }}>Recent Repls</div>
                <button style={{ height: 32, padding: '0 12px', borderRadius: 8, border: '1px solid #ddd', background: '#fff', fontSize: 13 }}>All Repls</button>
              </div>

              <div style={{ borderRadius: 12, border: '1px solid #ddd', background: '#fff', overflow: 'hidden' }}>
                {recentProjects.map((item, idx) => (
                  <div key={item.name} style={{ padding: '14px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: idx !== recentProjects.length - 1 ? '1px solid #eee' : 'none' }}>
                    <div>
                      <div style={{ fontWeight: 600 }}>{item.name}</div>
                      <div style={{ fontSize: 13, color: '#777' }}>{item.status}</div>
                    </div>
                    <button style={{ border: 'none', background: 'transparent', color: '#777', fontSize: 20, lineHeight: 1 }}>⋮</button>
                  </div>
                ))}
                {!recentProjects.length ? <div style={{ padding: 16, color: '#777', fontSize: 13 }}>No recent repls yet.</div> : null}
              </div>
            </div>
          </div>
        </main>

        <section style={{ width: 360, borderLeft: '1px solid #ddd', background: '#fff', display: 'flex', flexDirection: 'column' }}>
          <div style={{ height: 48, borderBottom: '1px solid #eee', padding: '0 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ fontWeight: 600, fontSize: 13 }}>Live Preview</div>
            <div style={{ fontSize: 11, color: '#777' }}>public side</div>
          </div>
          <div style={{ flex: 1, padding: 16, background: '#fafafa' }}>
            <div style={{ height: '100%', borderRadius: 12, border: '1px solid #ddd', background: '#fff', boxShadow: '0 1px 3px rgba(0,0,0,0.08)', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
              <div style={{ height: 40, borderBottom: '1px solid #eee', display: 'flex', alignItems: 'center', padding: '0 12px', gap: 8 }}>
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#ff5f57' }} />
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#febc2e' }} />
                <div style={{ width: 10, height: 10, borderRadius: '50%', background: '#28c840' }} />
                <div style={{ marginLeft: 8, fontSize: 11, color: '#777', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                  {previewUrl}
                </div>
              </div>
              <iframe title="ODEX Live Preview" src={previewUrl} style={{ border: 'none', flex: 1, minHeight: 520, background: '#fff' }} />
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
