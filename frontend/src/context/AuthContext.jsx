import { createContext, useCallback, useContext, useEffect, useState } from "react";

const API_BASE = import.meta.env.VITE_API_URL || "";
const TOKEN_KEY = "easy_ai_token";

const AuthCtx = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser]     = useState(null);
  const [ready, setReady]   = useState(false);  // true once initial check done

  // On mount: check stored token
  useEffect(() => {
    const token = localStorage.getItem(TOKEN_KEY);
    if (!token) { setReady(true); return; }
    fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((r) => r.ok ? r.json() : null)
      .then((u) => { setUser(u); setReady(true); })
      .catch(() => { setReady(true); });
  }, []);

  const login = useCallback(async (email, password) => {
    const r = await fetch(`${API_BASE}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: "Login failed" }));
      throw new Error(err.detail || "Login failed");
    }
    const { token, user: u } = await r.json();
    localStorage.setItem(TOKEN_KEY, token);
    setUser(u);
    return u;
  }, []);

  const signup = useCallback(async (email, password, name, role = "student") => {
    const r = await fetch(`${API_BASE}/auth/signup`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password, name, role }),
    });
    if (!r.ok) {
      const err = await r.json().catch(() => ({ detail: "Sign-up failed" }));
      throw new Error(err.detail || "Sign-up failed");
    }
    const { token, user: u } = await r.json();
    localStorage.setItem(TOKEN_KEY, token);
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setUser(null);
  }, []);

  const authHeader = useCallback(() => {
    const t = localStorage.getItem(TOKEN_KEY);
    return t ? { Authorization: `Bearer ${t}` } : {};
  }, []);

  return (
    <AuthCtx.Provider value={{ user, ready, login, signup, logout, authHeader }}>
      {children}
    </AuthCtx.Provider>
  );
}

export const useAuth = () => useContext(AuthCtx);
