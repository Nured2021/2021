import { useState } from "react";
import styles from "./Sidebar.module.css";

const DOC_ITEMS = [
  { id: "document",      label: "Documents",      icon: "📄" },
  { id: "excel",         label: "Excel",          icon: "📊" },
  { id: "presentation",  label: "Presentation",   icon: "📽️" },
  { id: "uploads",       label: "Upload File",    icon: "📁" },
];

const EDU_ITEMS = [
  { id: "edu_professor",    label: "Senior Professors", icon: "🎓" },
  { id: "edu_teacher",      label: "Teachers",          icon: "📚" },
  { id: "edu_exam",         label: "Exam Prep",         icon: "📝" },
  { id: "edu_simulation",   label: "Simulations",       icon: "💼" },
  { id: "edu_court",        label: "Court",             icon: "⚖️" },
  { id: "edu_student",      label: "Student Assistant", icon: "🙋" },
  { id: "edu_admin",        label: "Admin",             icon: "🗂️" },
  { id: "edu_multilingual", label: "Languages",         icon: "🌐" },
  { id: "edu_integrity",    label: "Integrity",         icon: "🛡️" },
];

const BIZ_ITEMS = [
  { id: "business",   label: "Business AI",       icon: "🏢" },
  { id: "research",   label: "Research AI",        icon: "🔬" },
  { id: "analytics",  label: "Analytics AI",       icon: "📈" },
  { id: "content",    label: "Content AI",         icon: "✍️" },
  { id: "course",     label: "Course Builder AI",  icon: "🏫" },
];

const DOC_FORMATS = [
  { id: "doc",    label: "Doc"    },
  { id: "pdf",    label: "PDF"    },
  { id: "slides", label: "Slides" },
  { id: "excel",  label: "Excel"  },
];

export default function Sidebar({ active, onSelect, docFormat, onDocFormat }) {
  const [collapsed, setCollapsed] = useState({ office: false, education: false, business: false });

  const toggle = (section) =>
    setCollapsed((prev) => ({ ...prev, [section]: !prev[section] }));

  const isOfficeActive = !active.startsWith("edu_") &&
    !BIZ_ITEMS.some((b) => b.id === active);

  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>✦</span>
        <span className={styles.logoText}>Easy AI</span>
      </div>

      <nav className={styles.nav}>

        {/* ── Office ───────────────────────────── */}
        <button className={styles.sectionBtn} onClick={() => toggle("office")}>
          <span className={styles.sectionLabel}>Office</span>
          <span className={styles.chevron}>{collapsed.office ? "›" : "⌄"}</span>
        </button>

        {!collapsed.office && (
          <>
            <div className={styles.formatRow}>
              {DOC_FORMATS.map((f) => (
                <button
                  key={f.id}
                  className={`${styles.formatPill} ${
                    isOfficeActive && docFormat === f.id ? styles.formatActive : ""
                  }`}
                  onClick={() => {
                    onDocFormat(f.id);
                    if (f.id === "slides") onSelect("presentation");
                    else if (f.id === "excel") onSelect("excel");
                    else onSelect("document");
                  }}
                >
                  {f.label}
                </button>
              ))}
            </div>

            {DOC_ITEMS.map((item) => (
              <button
                key={item.id}
                className={`${styles.navItem} ${active === item.id ? styles.active : ""}`}
                onClick={() => onSelect(item.id)}
              >
                <span className={styles.icon}>{item.icon}</span>
                <span className={styles.label}>{item.label}</span>
              </button>
            ))}
          </>
        )}

        {/* ── Education ────────────────────────── */}
        <button className={styles.sectionBtn} onClick={() => toggle("education")}>
          <span className={styles.sectionLabel}>Education</span>
          <span className={styles.chevron}>{collapsed.education ? "›" : "⌄"}</span>
        </button>

        {!collapsed.education &&
          EDU_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`${styles.navItem} ${active === item.id ? styles.active : ""}`}
              onClick={() => onSelect(item.id)}
            >
              <span className={styles.icon}>{item.icon}</span>
              <span className={styles.label}>{item.label}</span>
            </button>
          ))}

        {/* ── Business & Professional ───────────── */}
        <button className={styles.sectionBtn} onClick={() => toggle("business")}>
          <span className={styles.sectionLabel}>Business & Pro</span>
          <span className={styles.chevron}>{collapsed.business ? "›" : "⌄"}</span>
        </button>

        {!collapsed.business &&
          BIZ_ITEMS.map((item) => (
            <button
              key={item.id}
              className={`${styles.navItem} ${active === item.id ? styles.active : ""}`}
              onClick={() => onSelect(item.id)}
            >
              <span className={styles.icon}>{item.icon}</span>
              <span className={styles.label}>{item.label}</span>
            </button>
          ))}

      </nav>
    </aside>
  );
}
