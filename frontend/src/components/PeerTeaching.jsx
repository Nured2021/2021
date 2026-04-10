import { useState, useEffect, useRef, useCallback } from 'react';
import styles from './PeerTeaching.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';
const WS_BASE  = API_BASE.replace(/^http/, 'ws');
const ICE_CONFIG = {
  iceServers: [
    { urls: ['stun:stun.l.google.com:19302'] },
    { urls: ['stun:stun1.l.google.com:19302'] },
  ],
};

/**
 * PeerTeaching – study groups, collaborative whiteboard, and screen sharing.
 *
 * Props:
 *   classroomId  – parent classroom UUID
 *   userId / userName – current user
 *   authHeader   – () => {Authorization: "Bearer ..."}
 */
export default function PeerTeaching({ classroomId, userId, userName, authHeader }) {
  const [studyGroups,    setStudyGroups]    = useState([]);
  const [activeGroup,    setActiveGroup]    = useState(null);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [isDrawing,      setIsDrawing]      = useState(false);
  const [drawColor,      setDrawColor]      = useState('#60a5fa');
  const [drawSize,       setDrawSize]       = useState(3);
  const [chatMessages,   setChatMessages]   = useState([]);
  const [chatInput,      setChatInput]      = useState('');
  const [showCreate,     setShowCreate]     = useState(false);
  const [newGroup,       setNewGroup]       = useState({ name: '', topic: '' });

  const canvasRef      = useRef(null);
  const screenRef      = useRef(null);    // <video> for remote screen share
  const screenStreamRef = useRef(null);
  const wsRef          = useRef(null);
  const screenPcRef    = useRef(null);    // RTCPeerConnection for screen share
  const lastPointRef   = useRef(null);

  // ── Load study groups ─────────────────────────────────────────────────
  const loadGroups = useCallback(async () => {
    try {
      const r = await fetch(`${API_BASE}/api/classroom/${classroomId}/study-groups`,
                            { headers: authHeader?.() || {} });
      if (r.ok) setStudyGroups(await r.json());
    } catch (_) {}
  }, [classroomId, authHeader]);

  useEffect(() => { loadGroups(); }, [loadGroups]);

  // ── WebSocket ─────────────────────────────────────────────────────────
  useEffect(() => {
    const url = `${WS_BASE}/ws/peer/${classroomId}?user_id=${encodeURIComponent(userId)}&user_name=${encodeURIComponent(userName)}`;
    const ws  = new WebSocket(url);
    wsRef.current = ws;

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'whiteboard_update') {
        replayAction(data.action);
      } else if (data.type === 'screen_share_started') {
        // A peer started screen sharing; set up to receive their track
        setupScreenReceive(data.teacher_id);
      } else if (data.type === 'screen_share_stopped') {
        if (screenRef.current) screenRef.current.srcObject = null;
      } else if (data.type === 'group_update') {
        loadGroups();
      } else if (data.type === 'group_state') {
        setActiveGroup(data.group);
        replayWhiteboard(data.whiteboard?.elements || []);
      } else if (data.type === 'chat') {
        setChatMessages((m) => [...m.slice(-99), data]);
      } else if (data.type === 'offer' && data.from) {
        handleScreenOffer(data.from, data.sdp);
      } else if (data.type === 'answer' && data.from) {
        screenPcRef.current?.setRemoteDescription(new RTCSessionDescription(data.sdp));
      } else if (data.type === 'ice_candidate' && data.from) {
        screenPcRef.current?.addIceCandidate(new RTCIceCandidate(data.candidate));
      }
    };

    return () => ws.close();
  }, [classroomId, userId, userName]);

  // ── Canvas helpers ────────────────────────────────────────────────────
  const getCtx = () => {
    const canvas = canvasRef.current;
    if (!canvas) return null;
    const ctx = canvas.getContext('2d');
    ctx.strokeStyle = drawColor;
    ctx.lineWidth   = drawSize;
    ctx.lineCap     = 'round';
    ctx.lineJoin    = 'round';
    return ctx;
  };

  const replayAction = (action) => {
    if (!action) return;
    const ctx = getCtx();
    if (!ctx) return;
    if (action.action_type === 'clear') {
      const c = canvasRef.current;
      ctx.clearRect(0, 0, c.width, c.height);
    } else if (action.action_type === 'draw' && action.data) {
      const { x1, y1, x2, y2, color, size } = action.data;
      ctx.strokeStyle = color || drawColor;
      ctx.lineWidth   = size  || drawSize;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
    }
  };

  const replayWhiteboard = (elements) => {
    const ctx = getCtx();
    if (!ctx || !canvasRef.current) return;
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    elements.forEach(replayAction);
  };

  // ── Drawing events ────────────────────────────────────────────────────
  const onMouseDown = (e) => {
    setIsDrawing(true);
    const r = canvasRef.current.getBoundingClientRect();
    lastPointRef.current = {
      x: e.clientX - r.left,
      y: e.clientY - r.top,
    };
  };

  const onMouseMove = (e) => {
    if (!isDrawing || !lastPointRef.current || !activeGroup) return;
    const canvas = canvasRef.current;
    const r      = canvas.getBoundingClientRect();
    const x2 = e.clientX - r.left;
    const y2 = e.clientY - r.top;
    const { x: x1, y: y1 } = lastPointRef.current;
    const ctx = getCtx();
    if (!ctx) return;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    lastPointRef.current = { x: x2, y: y2 };

    // Broadcast
    wsRef.current?.send(JSON.stringify({
      type: 'whiteboard', action: 'draw',
      group_id: activeGroup.id, user_id: userId,
      data: { x1, y1, x2, y2, color: drawColor, size: drawSize },
    }));
  };

  const onMouseUp   = () => { setIsDrawing(false); lastPointRef.current = null; };
  const onMouseLeave = () => { setIsDrawing(false); lastPointRef.current = null; };

  const clearWhiteboard = () => {
    const ctx = getCtx();
    if (!ctx || !canvasRef.current) return;
    ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
    if (activeGroup) {
      wsRef.current?.send(JSON.stringify({
        type: 'whiteboard', action: 'clear', group_id: activeGroup.id, user_id: userId, data: {},
      }));
    }
  };

  // ── Screen share ──────────────────────────────────────────────────────
  const startScreenShare = async () => {
    if (!activeGroup) return;
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      screenStreamRef.current = stream;
      setIsScreenSharing(true);

      const pc = new RTCPeerConnection(ICE_CONFIG);
      screenPcRef.current = pc;
      stream.getTracks().forEach((t) => pc.addTrack(t, stream));

      pc.onicecandidate = (e) => {
        if (e.candidate) {
          wsRef.current?.send(JSON.stringify({
            type: 'ice_candidate', target: 'broadcast',
            group_id: activeGroup.id, candidate: e.candidate,
          }));
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      wsRef.current?.send(JSON.stringify({
        type: 'start_screen_share', group_id: activeGroup.id, user_id: userId,
      }));
      wsRef.current?.send(JSON.stringify({
        type: 'offer', target: 'broadcast', group_id: activeGroup.id, sdp: offer,
      }));

      stream.getVideoTracks()[0].onended = stopScreenShare;
    } catch (e) {
      console.warn('[PeerTeaching] Screen share error:', e.message);
    }
  };

  const stopScreenShare = () => {
    screenStreamRef.current?.getTracks().forEach((t) => t.stop());
    setIsScreenSharing(false);
    screenPcRef.current?.close();
    if (activeGroup) {
      wsRef.current?.send(JSON.stringify({ type: 'stop_screen_share', group_id: activeGroup.id }));
    }
  };

  const setupScreenReceive = (teacherId) => {
    const pc = new RTCPeerConnection(ICE_CONFIG);
    screenPcRef.current = pc;
    pc.ontrack = (e) => {
      if (screenRef.current) screenRef.current.srcObject = e.streams[0];
    };
    pc.onicecandidate = (e) => {
      if (e.candidate) {
        wsRef.current?.send(JSON.stringify({
          type: 'ice_candidate', target: teacherId, candidate: e.candidate,
        }));
      }
    };
  };

  const handleScreenOffer = async (fromId, sdp) => {
    const pc = screenPcRef.current || new RTCPeerConnection(ICE_CONFIG);
    screenPcRef.current = pc;
    await pc.setRemoteDescription(new RTCSessionDescription(sdp));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsRef.current?.send(JSON.stringify({ type: 'answer', target: fromId, sdp: answer }));
    pc.ontrack = (e) => { if (screenRef.current) screenRef.current.srcObject = e.streams[0]; };
  };

  // ── Join / Create group ───────────────────────────────────────────────
  const joinGroup = async (groupId) => {
    const r = await fetch(`${API_BASE}/api/classroom/study-group/${groupId}/join`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(authHeader?.() || {}) },
      body: JSON.stringify({ user_id: userId, user_name: userName }),
    });
    if (r.ok) {
      const group = await r.json();
      setActiveGroup(group);
      wsRef.current?.send(JSON.stringify({ type: 'join_group', group_id: groupId, user_id: userId }));
      loadGroups();
    }
  };

  const createGroup = async () => {
    if (!newGroup.name || !newGroup.topic) return;
    const r = await fetch(`${API_BASE}/api/classroom/study-group/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...(authHeader?.() || {}) },
      body: JSON.stringify({
        classroom_id: classroomId, name: newGroup.name,
        topic: newGroup.topic, user_id: userId, user_name: userName,
      }),
    });
    if (r.ok) {
      const group = await r.json();
      setStudyGroups((g) => [...g, group]);
      setActiveGroup(group);
      setShowCreate(false);
      setNewGroup({ name: '', topic: '' });
      wsRef.current?.send(JSON.stringify({ type: 'join_group', group_id: group.id, user_id: userId }));
    }
  };

  const sendChat = () => {
    if (!chatInput.trim() || !activeGroup) return;
    wsRef.current?.send(JSON.stringify({
      type: 'chat', group_id: activeGroup.id, user_id: userId, user_name: userName, text: chatInput,
    }));
    setChatInput('');
  };

  const isTeacher = activeGroup?.teacher_student_id === userId;

  return (
    <div className={styles.peerTeaching}>
      {/* ── Left: study group list ────────────────────────────── */}
      <div className={styles.sidebar}>
        <div className={styles.sidebarHeader}>
          <span className={styles.sidebarTitle}>📚 Study Groups</span>
          <button className={styles.createBtn} onClick={() => setShowCreate(true)}>+ New</button>
        </div>

        {showCreate && (
          <div className={styles.createForm}>
            <input className={styles.formInput} placeholder="Group name"
              value={newGroup.name} onChange={(e) => setNewGroup((n) => ({ ...n, name: e.target.value }))} />
            <input className={styles.formInput} placeholder="Topic"
              value={newGroup.topic} onChange={(e) => setNewGroup((n) => ({ ...n, topic: e.target.value }))} />
            <div className={styles.formActions}>
              <button className={styles.btnSecondary} onClick={() => setShowCreate(false)}>Cancel</button>
              <button className={styles.btnPrimary}   onClick={createGroup}>Create</button>
            </div>
          </div>
        )}

        {studyGroups.length === 0 && !showCreate && (
          <p className={styles.emptyMsg}>No study groups yet. Create one to start peer teaching!</p>
        )}

        {studyGroups.map((g) => (
          <div key={g.id}
            className={`${styles.groupCard} ${activeGroup?.id === g.id ? styles.groupCardActive : ''}`}>
            <div className={styles.groupName}>{g.name}</div>
            <div className={styles.groupMeta}>📖 {g.topic}</div>
            <div className={styles.groupMeta}>
              👨‍🏫 {g.teacher_student_name}
            </div>
            <div className={styles.groupFooter}>
              <span className={styles.learnerCount}>👥 {g.learner_student_ids?.length || 0}</span>
              <button className={styles.joinBtn} onClick={() => joinGroup(g.id)}>
                {activeGroup?.id === g.id ? 'Active' : 'Join'}
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* ── Right: active session ─────────────────────────────── */}
      <div className={styles.session}>
        {!activeGroup ? (
          <div className={styles.emptySession}>
            <div className={styles.emptyIcon}>📐</div>
            <p>Join or create a study group to start learning together.</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className={styles.sessionHeader}>
              <div>
                <h3 className={styles.sessionTitle}>{activeGroup.name}</h3>
                <p className={styles.sessionSub}>📖 {activeGroup.topic}
                  {isTeacher && <span className={styles.teacherTag}> · You are teaching</span>}
                </p>
              </div>
              <div className={styles.sessionActions}>
                {isTeacher && (
                  <button
                    className={`${styles.actionBtn} ${isScreenSharing ? styles.actionDanger : ''}`}
                    onClick={isScreenSharing ? stopScreenShare : startScreenShare}>
                    {isScreenSharing ? '⏹ Stop Share' : '🖥 Share Screen'}
                  </button>
                )}
              </div>
            </div>

            {/* Screen share viewer */}
            <video ref={screenRef} className={styles.screenVideo} autoPlay playsInline
              style={{ display: screenRef.current?.srcObject ? 'block' : 'none' }} />

            {/* Whiteboard */}
            <div className={styles.whiteboardWrap}>
              <div className={styles.wbToolbar}>
                <span className={styles.wbLabel}>🎨 Whiteboard</span>
                <input type="color" value={drawColor}
                  onChange={(e) => setDrawColor(e.target.value)} className={styles.colorPicker}
                  title="Pen color" />
                <input type="range" min="1" max="20" value={drawSize}
                  onChange={(e) => setDrawSize(Number(e.target.value))} className={styles.sizeSlider}
                  title="Pen size" />
                <button className={styles.clearBtn} onClick={clearWhiteboard}>Clear</button>
              </div>
              <canvas ref={canvasRef} width={700} height={350}
                className={styles.whiteboard}
                onMouseDown={onMouseDown} onMouseMove={onMouseMove}
                onMouseUp={onMouseUp} onMouseLeave={onMouseLeave}
                style={{ cursor: 'crosshair' }} />
            </div>

            {/* Chat */}
            <div className={styles.chat}>
              <p className={styles.chatTitle}>💬 Group Chat</p>
              <div className={styles.messages}>
                {chatMessages.map((m, i) => (
                  <div key={i} className={`${styles.msg} ${m.user_id === userId ? styles.msgSelf : ''}`}>
                    <span className={styles.msgUser}>{m.user_name}:</span> {m.text}
                  </div>
                ))}
              </div>
              <div className={styles.chatInput}>
                <input className={styles.chatField} value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendChat()}
                  placeholder="Ask a question…" />
                <button className={styles.sendBtn} onClick={sendChat}>Send</button>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
