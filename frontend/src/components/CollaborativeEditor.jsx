import { useEffect, useRef, useState, useCallback } from 'react';
import styles from './CollaborativeEditor.module.css';

const WS_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  .replace(/^http/, 'ws');

/**
 * CollaborativeEditor — real-time multi-user document editor.
 *
 * Props:
 *   documentId     – document UUID to collaborate on
 *   userId         – current user's ID (from AuthContext)
 *   userName       – display name shown to other users
 *   initialContent – text shown before the WS connection delivers state
 *   readOnly       – if true, renders as a read-only viewer
 *   onContentChange(content) – callback whenever local content changes
 */
export default function CollaborativeEditor({
  documentId,
  userId      = 'anonymous',
  userName    = 'Anonymous',
  initialContent = '',
  readOnly    = false,
  onContentChange,
}) {
  const [content, setContent]       = useState(initialContent);
  const [connected, setConnected]   = useState(false);
  const [activeUsers, setActiveUsers] = useState([]);
  const [cursors, setCursors]       = useState({});        // userId → position
  const [statusMsg, setStatusMsg]   = useState('Connecting…');

  const wsRef       = useRef(null);
  const textareaRef = useRef(null);
  const reconnectRef = useRef(null);

  // ── WebSocket lifecycle ────────────────────────────────────────────────
  const connect = useCallback(() => {
    const url = `${WS_BASE}/ws/${documentId}?user_id=${encodeURIComponent(userId)}&user_name=${encodeURIComponent(userName)}`;
    const ws  = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnected(true);
      setStatusMsg('Connected');
    };

    ws.onclose = () => {
      setConnected(false);
      setStatusMsg('Disconnected — reconnecting in 3 s…');
      reconnectRef.current = setTimeout(connect, 3000);
    };

    ws.onerror = () => {
      setStatusMsg('Connection error');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        switch (data.type) {
          case 'init':
            if (data.content) setContent(data.content);
            setActiveUsers(data.users || []);
            break;
          case 'update':
            setContent(data.content);
            setCursors((prev) => ({ ...prev, [data.user]: data.cursor }));
            break;
          case 'cursor':
            setCursors((prev) => ({ ...prev, [data.user]: data.position }));
            break;
          case 'user_joined':
          case 'user_left':
            setActiveUsers(data.users || []);
            break;
          default:
            break;
        }
      } catch (_) { /* malformed frame */ }
    };
  }, [documentId, userId, userName]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  // ── Event handlers ────────────────────────────────────────────────────
  const handleChange = (e) => {
    const newContent = e.target.value;
    setContent(newContent);
    onContentChange?.(newContent);

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type:    'edit',
        content: newContent,
        cursor:  e.target.selectionStart,
      }));
    }
  };

  const handleSelect = (e) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type:     'cursor',
        position: e.target.selectionStart,
      }));
    }
  };

  // ── Render ────────────────────────────────────────────────────────────
  return (
    <div className={styles.editor}>
      {/* Status bar */}
      <div className={styles.statusBar}>
        <span className={`${styles.dot} ${connected ? styles.online : styles.offline}`} />
        <span className={styles.statusText}>{statusMsg}</span>

        {/* Active user avatars */}
        <div className={styles.users}>
          {activeUsers.map((u) => (
            <span
              key={u.user_id}
              className={styles.avatar}
              style={{ background: u.color }}
              title={u.name}
            >
              {(u.name || u.user_id).slice(0, 1).toUpperCase()}
            </span>
          ))}
          {activeUsers.length > 0 && (
            <span className={styles.userCount}>
              {activeUsers.length} editing
            </span>
          )}
        </div>
      </div>

      {/* Editor area */}
      <textarea
        ref={textareaRef}
        className={styles.textarea}
        value={content}
        onChange={handleChange}
        onSelect={handleSelect}
        readOnly={readOnly}
        placeholder="Start typing — changes sync to all collaborators in real time…"
        spellCheck
      />

      {/* Cursor indicators (simplified — shows positions as badges) */}
      {Object.entries(cursors).filter(([uid]) => uid !== userId).length > 0 && (
        <div className={styles.cursorInfo}>
          {Object.entries(cursors)
            .filter(([uid]) => uid !== userId)
            .map(([uid, pos]) => {
              const user = activeUsers.find((u) => u.user_id === uid);
              return (
                <span
                  key={uid}
                  className={styles.cursorBadge}
                  style={{ background: user?.color || '#3b82f6' }}
                >
                  {user?.name || uid} @ {pos}
                </span>
              );
            })}
        </div>
      )}
    </div>
  );
}
