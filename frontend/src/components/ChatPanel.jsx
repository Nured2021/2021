import { useEffect, useRef, useState } from "react";
import { educationChat } from "../api/educationApi";
import styles from "./ChatPanel.module.css";

export default function ChatPanel({ module }) {
  const [messages, setMessages] = useState([]); // { role, content }
  const [input, setInput]       = useState("");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const bottomRef               = useRef(null);

  // Scroll to latest message whenever messages change
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Clear history when module changes
  useEffect(() => {
    setMessages([]);
    setError(null);
  }, [module]);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // Optimistically show user message
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setInput("");
    setLoading(true);
    setError(null);

    try {
      const data = await educationChat({ message: text, module });
      // Use authoritative history from server if available
      if (data.history && data.history.length > 0) {
        setMessages(data.history);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply || "" },
        ]);
      }
    } catch (err) {
      setError(err.message);
      // Remove the optimistic user message on failure
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={styles.panel}>
      <p className={styles.heading}>💬 Chat with AI</p>

      <div className={styles.history}>
        {messages.length === 0 && (
          <p className={styles.empty}>Ask a question about this topic…</p>
        )}
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`${styles.bubble} ${
              msg.role === "user" ? styles.user : styles.assistant
            }`}
          >
            <span className={styles.role}>
              {msg.role === "user" ? "You" : "AI"}
            </span>
            <p className={styles.text}>{msg.content}</p>
          </div>
        ))}
        {loading && (
          <div className={`${styles.bubble} ${styles.assistant}`}>
            <span className={styles.role}>AI</span>
            <p className={`${styles.text} ${styles.thinking}`}>Thinking…</p>
          </div>
        )}
        {error && <p className={styles.error}>⚠ {error}</p>}
        <div ref={bottomRef} />
      </div>

      <div className={styles.inputRow}>
        <textarea
          className={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send)"
          rows={2}
          disabled={loading}
        />
        <button
          className={styles.sendBtn}
          onClick={handleSend}
          disabled={loading || !input.trim()}
          title="Send"
        >
          ➤
        </button>
      </div>
    </div>
  );
}
