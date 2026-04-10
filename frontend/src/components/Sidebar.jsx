import styles from "./Sidebar.module.css";

const NAV_ITEMS = [
  { id: "document", label: "Documents", icon: "📄" },
  { id: "excel", label: "Excel", icon: "📊" },
  { id: "presentation", label: "Presentation", icon: "📽️" },
  { id: "uploads", label: "Uploads", icon: "📁" },
];

export default function Sidebar({ active, onSelect }) {
  return (
    <aside className={styles.sidebar}>
      <div className={styles.logo}>
        <span className={styles.logoIcon}>✦</span>
        <span className={styles.logoText}>DocGen AI</span>
      </div>
      <nav className={styles.nav}>
        {NAV_ITEMS.map((item) => (
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
