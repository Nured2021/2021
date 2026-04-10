import { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './Dashboard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';

// ── Role-specific hero cards ───────────────────────────────────────────────
const ROLE_META = {
  student: {
    icon:  '🙋',
    label: 'Student Dashboard',
    color: '#3b82f6',
    tips:  ['Use Exam Prep AI to practise past papers', 'Try Simulation AI for case studies', 'Upload lecture notes for instant summaries'],
  },
  teacher: {
    icon:  '📚',
    label: 'Teacher Dashboard',
    color: '#10b981',
    tips:  ['Build full lesson plans with Teacher AI', 'Generate exam question banks with Exam AI', 'Use Course Builder for full curricula'],
  },
  professor: {
    icon:  '🎓',
    label: 'Professor Dashboard',
    color: '#8b5cf6',
    tips:  ['Senior Professor AI for research papers', 'Research AI for literature reviews', 'Analytics AI for data-driven insights'],
  },
  lawyer: {
    icon:  '⚖️',
    label: 'Legal Professional Dashboard',
    color: '#f59e0b',
    tips:  ['Court AI for legal briefs and arguments', 'Integrity AI to review documents', 'Citation AI for Bluebook & OSCOLA citations'],
  },
  admin: {
    icon:  '👑',
    label: 'Admin Dashboard',
    color: '#ef4444',
    tips:  ['Monitor usage via Analytics AI', 'Admin AI for policies and reports', 'Manage API keys from the sidebar'],
  },
};

const DEFAULT_ROLE = 'student';

// ── Sub-components ─────────────────────────────────────────────────────────

function StatsCard({ label, value, icon }) {
  return (
    <div className={styles.statCard}>
      <span className={styles.statIcon}>{icon}</span>
      <div>
        <p className={styles.statValue}>{value ?? '—'}</p>
        <p className={styles.statLabel}>{label}</p>
      </div>
    </div>
  );
}

function ModuleCard({ mod, onActivate }) {
  return (
    <button className={styles.modCard} onClick={() => onActivate(mod.id)}>
      <span className={styles.modIcon}>{mod.icon}</span>
      <span className={styles.modName}>{mod.name}</span>
    </button>
  );
}

function RecentDoc({ doc }) {
  return (
    <div className={styles.recentDoc}>
      <span className={styles.recentIcon}>📄</span>
      <div className={styles.recentInfo}>
        <p className={styles.recentTitle}>{doc.title}</p>
        <p className={styles.recentMeta}>
          {doc.module} · {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ''}
        </p>
      </div>
    </div>
  );
}

// ── Main Dashboard component ───────────────────────────────────────────────

export default function Dashboard({ onClose, onActivateModule }) {
  const { user, authHeader } = useAuth();
  const [data, setData]       = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError]     = useState(null);

  const role = user?.role || DEFAULT_ROLE;
  const meta = ROLE_META[role] || ROLE_META[DEFAULT_ROLE];

  useEffect(() => {
    if (!user) { setLoading(false); return; }
    fetch(`${API_BASE}/api/dashboard`, { headers: authHeader() })
      .then((r) => r.ok ? r.json() : Promise.reject(r.statusText))
      .then((d) => { setData(d); setLoading(false); })
      .catch((e) => { setError(String(e)); setLoading(false); });
  }, [user, authHeader]);

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        {/* Header */}
        <div className={styles.header} style={{ borderTopColor: meta.color }}>
          <span className={styles.roleIcon}>{meta.icon}</span>
          <div>
            <h2 className={styles.title}>{meta.label}</h2>
            {user && <p className={styles.subtitle}>Welcome back, {user.name}</p>}
          </div>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>

        {loading && <p className={styles.loadMsg}>Loading dashboard…</p>}
        {error   && <p className={styles.errMsg}>⚠ {error}</p>}

        {data && !loading && (
          <div className={styles.body}>
            {/* Stats row */}
            <div className={styles.statsRow}>
              <StatsCard label="Total Generated"   value={data.stats?.total_generated} icon="✦" />
              <StatsCard label="Plan"               value={data.stats?.plan?.toUpperCase()} icon="💎" />
              <StatsCard label="Recent Documents"   value={data.recent_documents?.length} icon="📄" />
              <StatsCard label="Recommended Tools"  value={data.recommended_modules?.length} icon="🤖" />
            </div>

            {/* Recommended modules */}
            {data.recommended_modules?.length > 0 && (
              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>Recommended for {role}s</h3>
                <div className={styles.modGrid}>
                  {data.recommended_modules.map((m) => (
                    <ModuleCard key={m.id} mod={m} onActivate={(id) => { onActivateModule?.(id); onClose(); }} />
                  ))}
                </div>
              </section>
            )}

            {/* Tips for this role */}
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Quick Tips</h3>
              <ul className={styles.tipsList}>
                {meta.tips.map((t, i) => <li key={i} className={styles.tip}>💡 {t}</li>)}
              </ul>
            </section>

            {/* Recent documents */}
            {data.recent_documents?.length > 0 && (
              <section className={styles.section}>
                <h3 className={styles.sectionTitle}>Recent Documents</h3>
                <div className={styles.recentList}>
                  {data.recent_documents.map((d) => <RecentDoc key={d.id} doc={d} />)}
                </div>
              </section>
            )}
          </div>
        )}

        {!user && !loading && (
          <div className={styles.body}>
            <p className={styles.noAuth}>Sign in to see your personalised dashboard.</p>
            <section className={styles.section}>
              <h3 className={styles.sectionTitle}>Quick Tips</h3>
              <ul className={styles.tipsList}>
                {meta.tips.map((t, i) => <li key={i} className={styles.tip}>💡 {t}</li>)}
              </ul>
            </section>
          </div>
        )}
      </div>
    </div>
  );
}
