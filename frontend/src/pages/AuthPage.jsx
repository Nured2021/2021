import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import styles from "./AuthPage.module.css";

const ROLES = [
  { value: "student",   label: "Student" },
  { value: "teacher",   label: "Teacher" },
  { value: "professor", label: "Professor / Researcher" },
  { value: "lawyer",    label: "Lawyer / Legal Professional" },
  { value: "admin",     label: "Administrator" },
];

export default function AuthPage({ onDone }) {
  const [mode, setMode] = useState("login"); // "login" | "signup"
  const [email, setEmail]       = useState("");
  const [password, setPassword] = useState("");
  const [name, setName]         = useState("");
  const [role, setRole]         = useState("student");
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  const { login, signup } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        if (!name.trim()) { setError("Name is required."); setLoading(false); return; }
        await signup(email, password, name, role);
      }
      onDone?.();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.card}>
        <div className={styles.logo}>
          <span className={styles.logoIcon}>✦</span>
          <span className={styles.logoText}>Easy AI</span>
        </div>

        <h2 className={styles.heading}>
          {mode === "login" ? "Sign in to your workspace" : "Create your account"}
        </h2>

        <form className={styles.form} onSubmit={handleSubmit}>
          {mode === "signup" && (
            <div className={styles.field}>
              <label className={styles.label}>Full Name</label>
              <input className={styles.input} type="text" value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Jane Smith" required />
            </div>
          )}

          <div className={styles.field}>
            <label className={styles.label}>Email</label>
            <input className={styles.input} type="email" value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com" required />
          </div>

          <div className={styles.field}>
            <label className={styles.label}>Password</label>
            <input className={styles.input} type="password" value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder={mode === "signup" ? "At least 8 characters" : "Your password"} required />
          </div>

          {mode === "signup" && (
            <div className={styles.field}>
              <label className={styles.label}>Your Role</label>
              <select className={styles.select} value={role} onChange={(e) => setRole(e.target.value)}>
                {ROLES.map((r) => (
                  <option key={r.value} value={r.value}>{r.label}</option>
                ))}
              </select>
            </div>
          )}

          {error && <p className={styles.error}>{error}</p>}

          <button className={styles.btn} type="submit" disabled={loading}>
            {loading ? "Please wait…" : mode === "login" ? "Sign In" : "Create Account"}
          </button>
        </form>

        <p className={styles.switchText}>
          {mode === "login" ? "Don't have an account? " : "Already have an account? "}
          <button className={styles.switchBtn}
            onClick={() => { setMode(mode === "login" ? "signup" : "login"); setError(""); }}>
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </p>

        <button className={styles.guestBtn} onClick={() => onDone?.()}>
          Continue as guest (no saving)
        </button>
      </div>
    </div>
  );
}
