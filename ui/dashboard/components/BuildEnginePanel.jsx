import React, { useEffect, useState } from 'react';

export default function BuildEnginePanel() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/events');
    ws.onmessage = (msg) => {
      setEvents(evts => [JSON.parse(msg.data), ...evts].slice(0, 100));
    };
    ws.onerror = () => ws.close();
    return () => ws.close();
  }, []);

  return (
    <div className="build-engine-panel">
      <h2>ODEX BUILD ENGINE</h2>
      <div className="live-events">
        {events.length === 0 && <div className="empty">Waiting for events...</div>}
        {events.map((evt, i) => (
          <div key={i} className={`event ${evt.type || ''}`}>
            <span className="stage">[{evt.stage}]</span> <span className="engine">{evt.engine}</span>: <span className="msg">{evt.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
import React, { useEffect, useState } from 'react';

export default function BuildEnginePanel() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8080/ws/events');
    ws.onmessage = (msg) => {
      setEvents(evts => [JSON.parse(msg.data), ...evts].slice(0, 100));
    };
    ws.onerror = () => ws.close();
    return () => ws.close();
  }, []);

  return (
    <div className="build-engine-panel">
      <h2>ODEX BUILD ENGINE</h2>
      <div className="live-events">
        {events.length === 0 && <div className="empty">Waiting for events...</div>}
        {events.map((evt, i) => (
          <div key={i} className={`event ${evt.type || ''}`}>
            <span className="stage">[{evt.stage}]</span> <span className="engine">{evt.engine}</span>: <span className="msg">{evt.message}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
