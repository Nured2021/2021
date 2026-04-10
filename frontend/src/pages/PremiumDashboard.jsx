import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import styles from './PremiumDashboard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';

const DEMO_DATA = {
  totalDocuments: 125,
  totalAICalls: 47,
  totalStudyGroups: 12,
  productivity: 89,
  storageUsed: 250,
  storageLimit: 1024,
  recentActivity: [
    { id: 1, action: 'Generated "Business Plan 2026"',        module: 'Business AI',   time: 'Today 09:45' },
    { id: 2, action: 'Joined "Physics 101" Classroom',        module: 'Classroom',     time: 'Today 08:30' },
    { id: 3, action: 'Created Study Group "Calculus Help"',   module: 'Peer Teaching', time: 'Yesterday'   },
    { id: 4, action: 'Exported "Marketing Strategy" to PDF',  module: 'Document AI',   time: 'Yesterday'   },
    { id: 5, action: 'Generated "Legal Brief – Smith v Lee"', module: 'Court AI',      time: '2 days ago'  },
  ],
  recentDocuments: [
    { id: 1, name: 'Business Plan 2026.docx',    module: 'Business AI', date: '2 days ago' },
    { id: 2, name: 'Monthly Budget.xlsx',         module: 'Excel AI',    date: '3 days ago' },
    { id: 3, name: 'Pitch Deck.pptx',             module: 'Slides AI',   date: '5 days ago' },
    { id: 4, name: 'Employment Contract.docx',    module: 'Court AI',    date: '1 week ago' },
    { id: 5, name: 'Research Paper – AI Ethics',  module: 'Research AI', date: '1 week ago' },
  ],
  classrooms: [
    { id: 1, name: 'Physics 101',           teacher: 'Professor Smith', students: 24, classId: 'PHYS-101' },
    { id: 2, name: 'Calculus Study Group',  teacher: 'You (Teacher)',   students: 5,  classId: 'CALC-SG1', isTeacher: true },
    { id: 3, name: 'Chemistry Lab',         teacher: 'Professor Lee',   students: 18, classId: 'CHEM-LAB' },
  ],
  aiUsage: { business: 45, court: 28, professor: 52, excel: 18 },
  integrations: { googleDrive: true, slack: true, zoom: false },
};

const DOC_ICON = { xlsx: '📊', pptx: '📽️', docx: '📄', pdf: '📄' };
function docIcon(name) {
  const ext = name.split('.').pop();
  return DOC_ICON[ext] || '📄';
}

export default function PremiumDashboard({ onClose, onActivateModule }) {
  const { user, authHeader } = useAuth();
  const [stats, setStats]     = useState(DEMO_DATA);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) { setLoading(false); return; }
    fetch(`${API_BASE}/api/dashboard/premium`, { headers: authHeader() })
      .then((r) => r.ok ? r.json() : null)
      .then((d) => { if (d) setStats(d); })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, authHeader]);

  const quickActions = [
    { icon: '✦', label: 'New Document',   action: 'document',   color: '#3b82f6' },
    { icon: '📤', label: 'Upload File',    action: 'uploads',    color: '#10b981' },
    { icon: '🏫', label: 'New Classroom',  action: 'classroom',  color: '#8b5cf6' },
    { icon: '👥', label: 'Study Group',    action: 'classroom',  color: '#f59e0b' },
  ];

  const statCards = [
    { label: 'Documents',   value: stats.totalDocuments,            icon: '📄', color: '#3b82f6' },
    { label: 'AI Calls',    value: stats.totalAICalls,              icon: '🤖', color: '#10b981' },
    { label: 'Study Groups',value: stats.totalStudyGroups,          icon: '👥', color: '#8b5cf6' },
    { label: 'Productivity',value: `${stats.productivity}%`,        icon: '📈', color: '#f59e0b' },
  ];

  const maxUsage = Math.max(...Object.values(stats.aiUsage), 1);
  const storagePercent = Math.round((stats.storageUsed / stats.storageLimit) * 100);

  if (loading) {
    return (
      <div className={styles.loading}>
        <div className={styles.spinner}>⟳</div>
        <p style={{ color: '#7a92b0', marginTop: 16 }}>Loading your dashboard…</p>
      </div>
    );
  }

  return (
    <div className={styles.dashboard}>
      {/* ── Header ── */}
      <div className={styles.header}>
        <div>
          <h1>✦ Premium Dashboard</h1>
          <p className={styles.subtitle}>
            Welcome back{user ? `, ${user.name || user.email}` : ''}! Here's your complete overview.
          </p>
        </div>
        <button className={styles.closeBtn} onClick={onClose} title="Close">✕</button>
      </div>

      {/* ── Stat Cards ── */}
      <div className={styles.statGrid}>
        {statCards.map((s) => (
          <div key={s.label} className={styles.statCard} style={{ borderTopColor: s.color }}>
            <div className={styles.statIcon}>{s.icon}</div>
            <div className={styles.statValue}>{s.value}</div>
            <div className={styles.statLabel}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* ── Quick Actions ── */}
      <div className={styles.quickActions}>
        <h3>🚀 Quick Actions</h3>
        <div className={styles.actionGrid}>
          {quickActions.map((a) => (
            <button
              key={a.label}
              className={styles.actionBtn}
              style={{ borderColor: `${a.color}55`, background: `${a.color}18` }}
              onClick={() => { onActivateModule?.(a.action); onClose?.(); }}
            >
              <span className={styles.actionIcon}>{a.icon}</span> {a.label}
            </button>
          ))}
        </div>
      </div>

      {/* ── Two-column section ── */}
      <div className={styles.twoColumn}>
        {/* Recent Activity */}
        <div className={styles.section}>
          <h3>📈 Recent Activity</h3>
          <div className={styles.activityList}>
            {stats.recentActivity.map((a) => (
              <div key={a.id} className={styles.activityItem}>
                <span className={styles.activityTime}>{a.time}</span>
                <span className={styles.activityAction}>{a.action}</span>
                <span className={styles.activityModule}>{a.module}</span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Usage */}
        <div className={styles.section}>
          <h3>📊 AI Usage Statistics</h3>
          <div className={styles.usageList}>
            {Object.entries(stats.aiUsage).map(([key, val]) => (
              <div key={key} className={styles.usageItem}>
                <span className={styles.usageLabel}>{key.charAt(0).toUpperCase() + key.slice(1)} AI</span>
                <div className={styles.usageBar}>
                  <div className={styles.usageFill} style={{ width: `${(val / maxUsage) * 100}%` }} />
                </div>
                <span className={styles.usageValue}>{val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Recent Documents ── */}
      <div className={styles.section}>
        <h3>📁 Recent Documents</h3>
        <div className={styles.docList}>
          {stats.recentDocuments.map((d) => (
            <div key={d.id} className={styles.docItem}>
              <span className={styles.docIcon}>{docIcon(d.name)}</span>
              <span className={styles.docName}>{d.name}</span>
              <span className={styles.docModule}>{d.module}</span>
              <span className={styles.docDate}>{d.date}</span>
              <button
                className={styles.docOpen}
                onClick={() => {
                  const mod = d.module.toLowerCase().replace(' ai', '');
                  onActivateModule?.(mod);
                  onClose?.();
                }}
              >
                Open
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* ── Classrooms ── */}
      <div className={styles.section}>
        <h3>🏫 My Classrooms &amp; Study Groups</h3>
        <div className={styles.classroomList}>
          {stats.classrooms.map((c) => (
            <div key={c.id} className={styles.classroomItem}>
              <span className={styles.classroomIcon}>{c.isTeacher ? '📚' : '🎓'}</span>
              <div>
                <div className={styles.classroomName}>{c.name}</div>
                <div className={styles.classroomTeacher}>{c.teacher}</div>
              </div>
              <span className={styles.classroomCount}>👥 {c.students}</span>
              <button
                className={styles.classroomOpen}
                onClick={() => { onActivateModule?.('classroom'); onClose?.(); }}
              >
                Open
              </button>
            </div>
          ))}
          {stats.classrooms.length === 0 && (
            <p style={{ color: '#7a92b0', fontSize: 14 }}>No classrooms yet. Create one!</p>
          )}
        </div>
      </div>

      {/* ── Storage + Integrations row ── */}
      <div className={styles.twoColumn}>
        {/* Storage */}
        <div className={styles.section}>
          <h3>💾 Storage Usage &nbsp; <span style={{ color: '#7a92b0', fontWeight: 400, fontSize: 13 }}>{storagePercent}% used</span></h3>
          <div className={styles.storageBar}>
            <div className={styles.storageFill} style={{ width: `${storagePercent}%` }} />
          </div>
          <p className={styles.storageText}>{stats.storageUsed} MB / {stats.storageLimit} MB</p>
        </div>

        {/* Integrations */}
        <div className={styles.section}>
          <h3>🔗 Integration Status</h3>
          <div className={styles.integrationList}>
            {[
              { key: 'googleDrive', label: 'Google Drive', icon: '🟢' },
              { key: 'slack',       label: 'Slack',        icon: '🟢' },
              { key: 'zoom',        label: 'Zoom',         icon: '⚠️' },
            ].map(({ key, label, icon }) => (
              <div key={key} className={styles.integrationItem}>
                <span>{stats.integrations[key] ? '✅' : icon}</span>
                <span style={{ flex: 1, color: '#fff' }}>{label}</span>
                {stats.integrations[key]
                  ? <span className={styles.integrationConnected}>Connected</span>
                  : <button className={styles.integrationConnect}>Connect</button>
                }
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Upgrade Banner ── */}
      <div className={styles.upgradeBanner}>
        <span>⚡ Unlock unlimited AI calls, 10 GB storage, priority support &amp; team collaboration.</span>
        <button className={styles.upgradeBtn}>Upgrade to Pro</button>
      </div>
    </div>
  );
}
