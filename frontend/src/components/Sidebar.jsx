import styles from "./Sidebar.module.css";

const DOC_ITEMS = [
  { id: "document", label: "Documents", icon: "📄" },
  { id: "excel", label: "Excel", icon: "📊" },
  { id: "presentation", label: "Presentation", icon: "📽️" },
  { id: "uploads", label: "Uploads", icon: "📁" },
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

export default function Sidebar({ active, onSelect }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>✦</span>
        <span className={styles.logoText}>DocGen AI</span>
      </div>

      <nav className={styles.nav}>
        <span className={styles.sectionLabel}>Office</span>
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

        <span className={styles.sectionLabel}>Education</span>
        {EDU_ITEMS.map((item) => (
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
