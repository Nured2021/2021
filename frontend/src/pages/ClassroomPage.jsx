import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import ClassroomVoiceChat from '../components/ClassroomVoiceChat';
import PeerTeaching       from '../components/PeerTeaching';
import styles             from './ClassroomPage.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';

const THEMES = ['default', 'galaxy', 'ocean', 'forest', 'sunset'];
const THEME_EMOJIS = { default: '🏫', galaxy: '🌌', ocean: '🌊', forest: '🌲', sunset: '🌅' };

/* ─── Tab sections inside an open classroom ─────────────────────────────── */
const TABS = [
  { id: 'voice',   label: '🎤 Voice Chat'   },
  { id: 'peers',   label: '👥 Peer Teaching' },
  { id: 'chat',    label: '💬 Chat'          },
  { id: 'members', label: '🧑‍🎓 Members'      },
];

/* ─── Create-classroom modal ────────────────────────────────────────────── */
function CreateModal({ onClose, onCreate }) {
  const [form, setForm] = useState({ name: '', subject: '', theme: 'default' });
  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2 className={styles.modalTitle}>🏫 Create New Classroom</h2>

        <label className={styles.label}>Class Name</label>
        <input className={styles.input} placeholder="e.g. Physics 101"
          value={form.name} onChange={(e) => update('name', e.target.value)} />

        <label className={styles.label}>Subject</label>
        <input className={styles.input} placeholder="e.g. Science, Math, Law…"
          value={form.subject} onChange={(e) => update('subject', e.target.value)} />

        <label className={styles.label}>Theme</label>
        <div className={styles.themeRow}>
          {THEMES.map((t) => (
            <button key={t}
              className={`${styles.themeBtn} ${form.theme === t ? styles.themeBtnActive : ''}`}
              onClick={() => update('theme', t)}>
              {THEME_EMOJIS[t]} {t}
            </button>
          ))}
        </div>

        <div className={styles.modalActions}>
          <button className={styles.btnSecondary} onClick={onClose}>Cancel</button>
          <button className={styles.btnPrimary}
            onClick={() => onCreate(form)} disabled={!form.name || !form.subject}>
            Create Classroom
          </button>
        </div>
      </div>
    </div>
  );
}

/* ─── Join-classroom modal ──────────────────────────────────────────────── */
function JoinModal({ onClose, onJoin }) {
  const [classId, setClassId] = useState('');
  const [role,    setRole]    = useState('student');
  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <h2 className={styles.modalTitle}>🔑 Join a Classroom</h2>
        <label className={styles.label}>Class ID</label>
        <input className={styles.input} placeholder="e.g. PHYS-ABC123"
          value={classId} onChange={(e) => setClassId(e.target.value.toUpperCase())} />
        <label className={styles.label}>Join as</label>
        <div className={styles.roleRow}>
          {['student', 'teacher'].map((r) => (
            <button key={r}
              className={`${styles.roleBtn} ${role === r ? styles.roleBtnActive : ''}`}
              onClick={() => setRole(r)}>
              {r === 'student' ? '🙋' : '📚'} {r}
            </button>
          ))}
        </div>
        <div className={styles.modalActions}>
          <button className={styles.btnSecondary} onClick={onClose}>Cancel</button>
          <button className={styles.btnPrimary} onClick={() => onJoin(classId, role)}
            disabled={!classId}>Join</button>
        </div>
      </div>
    </div>
  );
}

/* ─── Single classroom view ─────────────────────────────────────────────── */
function ClassroomView({ classroom, onBack, user, authHeader }) {
  const [activeTab, setActiveTab] = useState('voice');
  const [chatMsgs,  setChatMsgs]  = useState([]);
  const [chatInput, setChatInput] = useState('');

  const theme = classroom.theme || 'default';

  return (
    <div className={`${styles.classroomView} ${styles[`theme_${theme}`] || ''}`}>
      {/* ── Header */}
      <div className={styles.cvHeader}>
        <button className={styles.backBtn} onClick={onBack}>← Back</button>
        <div className={styles.cvInfo}>
          <span className={styles.cvTheme}>{THEME_EMOJIS[theme] || '🏫'}</span>
          <div>
            <h2 className={styles.cvName}>{classroom.name}</h2>
            <p className={styles.cvMeta}>
              🔑 {classroom.class_id} &nbsp;·&nbsp;
              👥 {classroom.member_count || 0} members
            </p>
          </div>
        </div>
        <div className={styles.cvBadges}>
          {classroom.members?.filter((m) => m.role === 'professor').map((m) => (
            <span key={m.user_id} className={styles.badge}>🎓 {m.user_name}</span>
          ))}
          {classroom.members?.filter((m) => m.role === 'teacher').map((m) => (
            <span key={m.user_id} className={styles.badge}>📚 {m.user_name}</span>
          ))}
        </div>
      </div>

      {/* ── Tabs */}
      <div className={styles.tabs}>
        {TABS.map((t) => (
          <button key={t.id}
            className={`${styles.tab} ${activeTab === t.id ? styles.tabActive : ''}`}
            onClick={() => setActiveTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* ── Tab content */}
      <div className={styles.tabContent}>
        {activeTab === 'voice' && (
          <ClassroomVoiceChat
            classroomId={classroom.id}
            userId={user?.id || 'guest'}
            userName={user?.name || 'Guest'}
            userRole={user?.role || 'student'}
          />
        )}

        {activeTab === 'peers' && (
          <PeerTeaching
            classroomId={classroom.id}
            userId={user?.id || 'guest'}
            userName={user?.name || 'Guest'}
            authHeader={authHeader}
          />
        )}

        {activeTab === 'chat' && (
          <div className={styles.simpleChat}>
            <div className={styles.chatMsgs}>
              {chatMsgs.length === 0 && (
                <p className={styles.chatEmpty}>No messages yet. Start the conversation!</p>
              )}
              {chatMsgs.map((m, i) => (
                <div key={i} className={styles.chatMsg}>
                  <span className={styles.chatUser}>{m.user}:</span> {m.text}
                </div>
              ))}
            </div>
            <div className={styles.chatRow}>
              <input className={styles.chatField} value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && chatInput.trim()) {
                    setChatMsgs((m) => [...m, { user: user?.name || 'You', text: chatInput }]);
                    setChatInput('');
                  }
                }}
                placeholder="Type a message…" />
              <button className={styles.sendBtn} onClick={() => {
                if (chatInput.trim()) {
                  setChatMsgs((m) => [...m, { user: user?.name || 'You', text: chatInput }]);
                  setChatInput('');
                }
              }}>Send</button>
            </div>
          </div>
        )}

        {activeTab === 'members' && (
          <div className={styles.membersList}>
            {(classroom.members || []).map((m) => (
              <div key={m.user_id} className={styles.memberRow}>
                <span className={styles.memberIcon}>
                  {m.role === 'professor' ? '🎓' : m.role === 'teacher' ? '📚' : '🙋'}
                </span>
                <span className={styles.memberName}>{m.user_name}</span>
                <span className={styles.memberRole}>{m.role}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

/* ─── Main ClassroomPage component ─────────────────────────────────────── */
export default function ClassroomPage({ onClose }) {
  const { user, authHeader } = useAuth();
  const [classrooms,   setClassrooms]   = useState([]);
  const [activeRoom,   setActiveRoom]   = useState(null);
  const [showCreate,   setShowCreate]   = useState(false);
  const [showJoin,     setShowJoin]     = useState(false);
  const [error,        setError]        = useState('');
  const [loading,      setLoading]      = useState(false);

  useEffect(() => {
    if (!user) return;
    setLoading(true);
    fetch(`${API_BASE}/api/classroom/my`, { headers: authHeader() })
      .then((r) => r.ok ? r.json() : [])
      .then((d) => { setClassrooms(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [user, authHeader]);

  const handleCreate = async (form) => {
    if (!user) { setError('Sign in to create a classroom.'); return; }
    const r = await fetch(`${API_BASE}/api/classroom`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify(form),
    });
    if (r.ok) {
      const room = await r.json();
      setClassrooms((c) => [room, ...c]);
      setActiveRoom(room);
      setShowCreate(false);
    } else {
      const e = await r.json().catch(() => ({}));
      setError(e.detail || 'Failed to create classroom.');
    }
  };

  const handleJoin = async (classId, role) => {
    if (!user) { setError('Sign in to join a classroom.'); return; }
    const r = await fetch(`${API_BASE}/api/classroom/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...authHeader() },
      body: JSON.stringify({ class_id: classId, role }),
    });
    if (r.ok) {
      const room = await r.json();
      setClassrooms((c) => {
        const exists = c.find((x) => x.id === room.id);
        return exists ? c.map((x) => x.id === room.id ? room : x) : [room, ...c];
      });
      setActiveRoom(room);
      setShowJoin(false);
    } else {
      const e = await r.json().catch(() => ({}));
      setError(e.detail || 'Classroom not found.');
    }
  };

  if (activeRoom) {
    return (
      <div className={styles.page}>
        <ClassroomView
          classroom={activeRoom}
          onBack={() => setActiveRoom(null)}
          user={user}
          authHeader={authHeader}
        />
      </div>
    );
  }

  return (
    <div className={styles.page}>
      {showCreate && <CreateModal onClose={() => setShowCreate(false)} onCreate={handleCreate} />}
      {showJoin   && <JoinModal   onClose={() => setShowJoin(false)}   onJoin={handleJoin}   />}

      {/* ── Page header */}
      <div className={styles.pageHeader}>
        <div>
          <h2 className={styles.pageTitle}>🏫 AI Classroom</h2>
          <p className={styles.pageSub}>Voice chat · Peer teaching · Collaborative whiteboard</p>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.btnSecondary} onClick={() => setShowJoin(true)}>🔑 Join</button>
          {user && <button className={styles.btnPrimary} onClick={() => setShowCreate(true)}>+ Create</button>}
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </div>
      </div>

      {error && <p className={styles.errMsg}>⚠ {error}</p>}

      {!user && (
        <div className={styles.authNotice}>
          Sign in to create or join classrooms. You can still explore below.
        </div>
      )}

      {loading && <p className={styles.loadMsg}>Loading your classrooms…</p>}

      {/* ── Classroom grid */}
      <div className={styles.grid}>
        {classrooms.map((room) => (
          <button key={room.id} className={styles.roomCard}
            onClick={() => setActiveRoom(room)}>
            <span className={styles.roomTheme}>{THEME_EMOJIS[room.theme] || '🏫'}</span>
            <div className={styles.roomInfo}>
              <p className={styles.roomName}>{room.name}</p>
              <p className={styles.roomMeta}>🔑 {room.class_id}</p>
              <p className={styles.roomMeta}>👥 {room.member_count || 0} members</p>
            </div>
            <span className={styles.enterArrow}>→</span>
          </button>
        ))}

        {classrooms.length === 0 && !loading && (
          <div className={styles.emptyGrid}>
            <p className={styles.emptyIcon}>🏫</p>
            <p>No classrooms yet.</p>
            <p className={styles.emptySub}>Create a classroom or join one with a Class ID.</p>
          </div>
        )}
      </div>
    </div>
  );
}
