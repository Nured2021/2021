import { useEffect, useRef, useState, useCallback } from 'react';
import styles from './ClassroomVoiceChat.module.css';

const WS_BASE = (import.meta.env.VITE_API_URL || 'http://localhost:8000')
  .replace(/^http/, 'ws');

const ICE_CONFIG = {
  iceServers: [
    { urls: ['stun:stun.l.google.com:19302'] },
    { urls: ['stun:stun1.l.google.com:19302'] },
  ],
};

/**
 * ClassroomVoiceChat
 *
 * Props:
 *   classroomId  – classroom UUID
 *   userId       – current user ID
 *   userName     – display name
 *   userRole     – professor | teacher | student
 */
export default function ClassroomVoiceChat({ classroomId, userId, userName, userRole = 'student' }) {
  const [connected,       setConnected]       = useState(false);
  const [isMuted,         setIsMuted]         = useState(false);
  const [isRecording,     setIsRecording]     = useState(false);
  const [activeSpeakers,  setActiveSpeakers]  = useState([]);
  const [transcriptions,  setTranscriptions]  = useState([]);
  const [peers,           setPeers]           = useState([]);
  const [vadEnabled,      setVadEnabled]      = useState(true);

  const wsRef          = useRef(null);
  const localStreamRef = useRef(null);
  const peerConnsRef   = useRef({});  // peerId → RTCPeerConnection
  const transcriptRef  = useRef(null);
  const vadTimerRef    = useRef(null);
  const remoteAudiosRef = useRef({});

  // ── Connect microphone ────────────────────────────────────────────────
  const initMic = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      localStreamRef.current = stream;
      if (vadEnabled) setupVAD(stream);
    } catch (e) {
      console.warn('[VoiceChat] Mic access denied:', e.message);
    }
  }, [vadEnabled]);

  // ── Voice Activity Detection (simple amplitude) ───────────────────────
  const setupVAD = (stream) => {
    const ctx     = new (window.AudioContext || window.webkitAudioContext)();
    const source  = ctx.createMediaStreamSource(stream);
    const analyser = ctx.createAnalyser();
    analyser.fftSize = 512;
    source.connect(analyser);
    const buf = new Uint8Array(analyser.frequencyBinCount);
    let speaking = false;

    vadTimerRef.current = setInterval(() => {
      analyser.getByteFrequencyData(buf);
      const avg = buf.reduce((a, b) => a + b, 0) / buf.length;
      const isSpeaking = avg > 15;
      if (isSpeaking !== speaking && wsRef.current?.readyState === WebSocket.OPEN) {
        speaking = isSpeaking;
        wsRef.current.send(JSON.stringify({ type: isSpeaking ? 'speaking' : 'stopped_speaking' }));
      }
    }, 200);
  };

  // ── WebSocket lifecycle ───────────────────────────────────────────────
  const connectWS = useCallback(() => {
    const url = `${WS_BASE}/ws/voice/${classroomId}?user_id=${encodeURIComponent(userId)}&user_name=${encodeURIComponent(userName)}`;
    const ws  = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen  = () => setConnected(true);
    ws.onclose = () => { setConnected(false); setTimeout(connectWS, 4000); };
    ws.onerror = () => {};

    ws.onmessage = async (event) => {
      const data = JSON.parse(event.data);
      switch (data.type) {
        case 'init':
          setPeers(data.peers || []);
          setIsRecording(data.is_recording || false);
          // Dial all existing peers
          for (const peer of (data.peers || [])) {
            await createOffer(peer.user_id);
          }
          break;
        case 'peer_joined':
          setPeers((p) => [...p.filter((x) => x.user_id !== data.user_id),
                            { user_id: data.user_id, user_name: data.user_name }]);
          break;
        case 'peer_left':
          setPeers((p) => p.filter((x) => x.user_id !== data.user_id));
          closePeer(data.user_id);
          break;
        case 'offer':
          await handleOffer(data.from, data.sdp);
          break;
        case 'answer':
          await handleAnswer(data.from, data.sdp);
          break;
        case 'ice_candidate':
          await handleIce(data.from, data.candidate);
          break;
        case 'speaker_update':
          setActiveSpeakers(data.speakers || []);
          break;
        case 'transcription':
          setTranscriptions((t) => [...t.slice(-49),
            { user_name: data.user_name, text: data.text, ts: data.timestamp }]);
          break;
        case 'recording_started':
          setIsRecording(true);
          break;
        case 'recording_stopped':
          setIsRecording(false);
          break;
        case 'user_muted':
          break;
        case 'user_unmuted':
          break;
        default:
          break;
      }
    };
  }, [classroomId, userId, userName]);

  useEffect(() => {
    initMic();
    connectWS();
    return () => {
      clearInterval(vadTimerRef.current);
      wsRef.current?.close();
      localStreamRef.current?.getTracks().forEach((t) => t.stop());
      Object.values(peerConnsRef.current).forEach((pc) => pc.close());
    };
  }, [initMic, connectWS]);

  // ── WebRTC helpers ────────────────────────────────────────────────────
  const makePeerConn = (peerId) => {
    const pc = new RTCPeerConnection(ICE_CONFIG);
    peerConnsRef.current[peerId] = pc;

    localStreamRef.current?.getTracks().forEach((t) => pc.addTrack(t, localStreamRef.current));

    pc.ontrack = (e) => {
      const audio = new Audio();
      audio.srcObject = e.streams[0];
      audio.autoplay  = true;
      remoteAudiosRef.current[peerId] = audio;
    };

    pc.onicecandidate = (e) => {
      if (e.candidate && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'ice_candidate', target: peerId, candidate: e.candidate,
        }));
      }
    };
    return pc;
  };

  const createOffer = async (peerId) => {
    const pc    = makePeerConn(peerId);
    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);
    wsRef.current?.send(JSON.stringify({ type: 'offer', target: peerId, sdp: offer }));
  };

  const handleOffer = async (fromId, sdp) => {
    const pc = makePeerConn(fromId);
    await pc.setRemoteDescription(new RTCSessionDescription(sdp));
    const answer = await pc.createAnswer();
    await pc.setLocalDescription(answer);
    wsRef.current?.send(JSON.stringify({ type: 'answer', target: fromId, sdp: answer }));
  };

  const handleAnswer = async (fromId, sdp) => {
    const pc = peerConnsRef.current[fromId];
    if (pc) await pc.setRemoteDescription(new RTCSessionDescription(sdp));
  };

  const handleIce = async (fromId, candidate) => {
    const pc = peerConnsRef.current[fromId];
    if (pc) await pc.addIceCandidate(new RTCIceCandidate(candidate));
  };

  const closePeer = (peerId) => {
    peerConnsRef.current[peerId]?.close();
    delete peerConnsRef.current[peerId];
    remoteAudiosRef.current[peerId]?.pause();
    delete remoteAudiosRef.current[peerId];
  };

  // ── Controls ──────────────────────────────────────────────────────────
  const toggleMute = () => {
    const tracks = localStreamRef.current?.getAudioTracks() || [];
    tracks.forEach((t) => { t.enabled = isMuted; });
    setIsMuted(!isMuted);
    wsRef.current?.send(JSON.stringify({ type: isMuted ? 'unmute' : 'mute' }));
  };

  const toggleRecording = () => {
    wsRef.current?.send(JSON.stringify({ type: isRecording ? 'stop_recording' : 'start_recording' }));
  };

  // ── Web Speech API transcription ──────────────────────────────────────
  const startTranscription = () => {
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) return;
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    const sr = new SR();
    sr.continuous     = true;
    sr.interimResults = false;
    sr.lang           = 'en-US';
    sr.onresult = (e) => {
      const text = e.results[e.results.length - 1][0].transcript.trim();
      if (text && wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({ type: 'transcription', text }));
      }
    };
    sr.start();
    transcriptRef.current = sr;
  };

  return (
    <div className={styles.voiceChat}>
      {/* Status bar */}
      <div className={styles.statusBar}>
        <span className={`${styles.dot} ${connected ? styles.online : styles.offline}`} />
        <span className={styles.statusLabel}>{connected ? 'Voice Connected' : 'Connecting…'}</span>
        <span className={styles.peerCount}>{peers.length + 1} in call</span>
      </div>

      {/* Controls */}
      <div className={styles.controls}>
        <button className={`${styles.ctrlBtn} ${isMuted ? styles.ctrlDanger : ''}`}
          onClick={toggleMute}>
          {isMuted ? '🔇 Unmute' : '🎤 Mute'}
        </button>

        <button className={`${styles.ctrlBtn} ${isRecording ? styles.ctrlRecording : ''}`}
          onClick={toggleRecording}>
          {isRecording ? '⏹ Stop Rec' : '🔴 Record'}
        </button>

        <button className={styles.ctrlBtn} onClick={startTranscription}
          title="Start auto-transcription (requires mic permission)">
          📝 Transcribe
        </button>
      </div>

      {/* Active speakers */}
      {activeSpeakers.length > 0 && (
        <div className={styles.speakers}>
          {activeSpeakers.map((s) => (
            <span key={s.id} className={styles.speakerBadge}>🗣️ {s.name}</span>
          ))}
        </div>
      )}

      {/* Peers in call */}
      <div className={styles.peers}>
        <span className={styles.peersLabel}>In call:</span>
        <span className={styles.peerSelf}>{userName} (you)</span>
        {peers.map((p) => (
          <span key={p.user_id} className={styles.peerChip}>{p.user_name}</span>
        ))}
      </div>

      {/* Transcriptions */}
      <div className={styles.transcriptions}>
        <p className={styles.transcTitle}>📝 Live Transcriptions</p>
        {transcriptions.length === 0 && (
          <p className={styles.transcEmpty}>Transcriptions will appear here during voice chat.</p>
        )}
        {transcriptions.map((t, i) => (
          <div key={i} className={styles.transcLine}>
            <span className={styles.transcUser}>{t.user_name}:</span> {t.text}
          </div>
        ))}
      </div>
    </div>
  );
}
