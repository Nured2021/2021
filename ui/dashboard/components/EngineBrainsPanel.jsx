import { useEffect, useState } from "react";
import axios from "axios";

export default function EngineBrainsPanel() {
  const [brains, setBrains] = useState([]);

  useEffect(() => {
    axios.get("http://localhost:8080/brains")
      .then(res => {
        if (res.data.brains) {
          setBrains(res.data.brains);
        } else {
          setBrains(res.data);
        }
      })
      .catch(err => {
        console.error("Failed to load brains:", err);
      });
  }, []);

  return (
    <div style={{
      padding: "10px",
      background: "#0f172a",
      color: "#fff",
      height: "100%",
      overflowY: "auto"
    }}>
      <h3 style={{marginBottom:"10px"}}>🧠 Engine Brains</h3>

      <div style={{
        display: "grid",
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: "8px"
      }}>
        {brains.map((brain, index) => (
          <div key={index} style={{
            border: "1px solid #334155",
            padding: "8px",
            borderRadius: "6px",
            background: "#1e293b"
          }}>
            <strong>{brain.name || brain}</strong>
            <p style={{fontSize:"12px",opacity:0.7}}>
              {brain.route || "active"}
            </p>
          </div>
        ))}
      </div>

      {brains.length === 0 && (
        <p style={{opacity:0.5}}>No brains loaded...</p>
      )}
    </div>
  );
}
