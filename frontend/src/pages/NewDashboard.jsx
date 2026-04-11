import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import GenerationWizard from '../components/GenerationWizard';
import styles from './NewDashboard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';

/* ── Module catalogue ──────────────────────────────────────────────────── */
const ALL_MODULES = [
  { id: 'document',   icon: '📄', label: 'Document AI',    color: '#3b82f6', desc: 'Contracts, reports, proposals' },
  { id: 'excel',      icon: '📊', label: 'Excel AI',       color: '#10b981', desc: 'Spreadsheets, budgets, data' },
  { id: 'slides',     icon: '📽️', label: 'Slides AI',      color: '#8b5cf6', desc: 'Presentations & pitch decks' },
  { id: 'business',   icon: '💼', label: 'Business AI',    color: '#f59e0b', desc: 'Plans, SWOT, marketing' },
  { id: 'research',   icon: '🔬', label: 'Research AI',    color: '#06b6d4', desc: 'Literature reviews, papers' },
  { id: 'analytics',  icon: '📈', label: 'Analytics AI',   color: '#ec4899', desc: 'KPIs, insights, dashboards' },
  { id: 'court',      icon: '⚖️', label: 'Court AI',       color: '#ef4444', desc: 'Legal briefs, arguments' },
  { id: 'content',    icon: '✍️', label: 'Content AI',     color: '#a855f7', desc: 'Blog, social, marketing copy' },
  { id: 'course',     icon: '🎓', label: 'Course Builder',  color: '#14b8a6', desc: 'Full curricula & modules' },
];

/* ── Brain steps ────────────────────────────────────────────────────────── */
const BRAIN_STEPS = [
  { num: 1, icon: '🤖', title: 'Intent Analysis',    desc: 'AI detects doc type, industry, audience & complexity' },
  { num: 2, icon: '✍️', title: 'Style & Tone',       desc: '6 writing styles × 5 tones — you choose before generating' },
  { num: 3, icon: '📋', title: 'Editable Outline',   desc: 'Review and customise the structure before generation starts' },
  { num: 4, icon: '🚀', title: 'Live Generation',    desc: 'Real-time progress bar with animated status messages' },
  { num: 5, icon: '✅', title: 'Output + Feedback',  desc: 'Download PDF / Word, regenerate sections, rate the result' },
];

/* ── Quick-start prompts ─────────────────────────────────────────────────── */
const QUICK_PROMPTS = [
  { label: 'Business Plan',       prompt: 'Write a detailed business plan for a coffee shop startup', module: 'business'  },
  { label: 'Research Paper',      prompt: 'Write a research paper on the impact of AI on education',  module: 'research'  },
  { label: 'Legal Contract',      prompt: 'Draft a freelance service contract for a web developer',   module: 'document'  },
  { label: 'Marketing Strategy',  prompt: 'Create a digital marketing strategy for a SaaS product',  module: 'business'  },
  { label: 'Investor Pitch Deck', prompt: 'Write a Series-A investor pitch deck for an AI startup',  module: 'slides'    },
  { label: 'Excel Budget',        prompt: 'Build a monthly budget spreadsheet for a small business',  module: 'excel'     },
];

/* ── Small sub-components ──────────────────────────────────────────────── */
function StatCard({ icon, value, label, color }) {
  return (
    <div className={styles.statCard} style={{ '--card-color': color }}>
      <div className={styles.statIcon}>{icon}</div>
      <div className={styles.statBody}>
        <p className={styles.statValue}>{value ?? '—'}</p>
        <p className={styles.statLabel}>{label}</p>
      </div>
    </div>
  );
}

function ModuleChip({ mod, onActivate }) {
  return (
    <button
      className={styles.moduleChip}
      style={{ '--chip-color': mod.color }}
      onClick={() => onActivate(mod.id)}
      title={mod.desc}
    >
      <span className={styles.chipIcon}>{mod.icon}</span>
      <span className={styles.chipLabel}>{mod.label}</span>
      <span className={styles.chipDesc}>{mod.desc}</span>
    </button>
  );
}

function BrainStep({ step }) {
  return (
    <div className={styles.brainStep}>
      <div className={styles.brainNum}>{step.num}</div>
      <div className={styles.brainIcon}>{step.icon}</div>
      <div className={styles.brainText}>
        <strong>{step.title}</strong>
        <p>{step.desc}</p>
      </div>
    </div>
  );
}

/* ── Main component ──────────────────────────────────────────────────────── */
export default function NewDashboard({ onClose, onActivateModule, onGenerate }) {
  const { user, authHeader } = useAuth();
  const [stats,        setStats]       = useState(null);
  const [recentDocs,   setRecentDocs]  = useState([]);
  const [wizardPrompt, setWizardPrompt]= useState('');
  const [wizardModule, setWizardModule]= useState('document');
  const [showWizard,   setShowWizard]  = useState(false);
  const [quickInput,   setQuickInput]  = useState('');

  /* Fetch stats */
  useEffect(() => {
    const headers = user ? authHeader() : {};
    fetch(`${API_BASE}/api/dashboard`, { headers })
      .then((r) => r.ok ? r.json() : null)
      .then((d) => {
        if (d) {
          setStats(d.stats);
          setRecentDocs(d.recent_documents || []);
        }
      })
      .catch(() => {});
  }, [user]);

  const openWizard = (prompt, module = 'document') => {
    setWizardPrompt(prompt);
    setWizardModule(module);
    setShowWizard(true);
  };

  const handleQuickLaunch = () => {
    if (!quickInput.trim()) return;
    openWizard(quickInput.trim(), 'document');
    setQuickInput('');
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.dashboard}>
        {/* ── Header ───────────────────────────────────────────────────── */}
        <div className={styles.header}>
          <div className={styles.headerLeft}>
            <div className={styles.brandBadge}>✦ Easy AI</div>
            <h1 className={styles.title}>
              {user ? `Welcome back, ${user.name || user.email}!` : 'Easy AI — New Dashboard'}
            </h1>
            <p className={styles.subtitle}>
              HumanLoop Brain · 5-Step Wizard · 9 AI Modules · Real-file Generation
            </p>
          </div>
          <button className={styles.closeBtn} onClick={onClose} title="Close">✕</button>
        </div>

        {/* ── Stats row ─────────────────────────────────────────────────── */}
        <div className={styles.statsRow}>
          <StatCard icon="📄" value={stats?.total_generated ?? '∞'} label="Documents Created" color="#3b82f6" />
          <StatCard icon="🤖" value="9"                              label="AI Modules"         color="#8b5cf6" />
          <StatCard icon="✨" value="5"                              label="Wizard Steps"        color="#10b981" />
          <StatCard icon="💎" value={stats?.plan?.toUpperCase() ?? 'FREE'} label="Your Plan"   color="#f59e0b" />
        </div>

        {/* ── Quick launcher ────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>✨ Quick Launch — HumanLoop Wizard</h2>
          <p className={styles.sectionSub}>
            Type any request and the AI Brain will analyze intent, suggest style &amp; tone, show an editable outline, then generate your document.
          </p>
          <div className={styles.quickBox}>
            <input
              className={styles.quickInput}
              placeholder='e.g. "Write a business plan for a coffee shop" …'
              value={quickInput}
              onChange={(e) => setQuickInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleQuickLaunch()}
            />
            <button className={styles.quickBtn} onClick={handleQuickLaunch}>
              ✨ Open Wizard
            </button>
          </div>
        </section>

        {/* ── HumanLoop Brain Architecture ──────────────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>🧠 HumanLoop Brain — 5-Step Generation</h2>
          <p className={styles.sectionSub}>
            Unlike simple text generation, the HumanLoop Brain understands your intent deeply and walks you through every step.
          </p>
          <div className={styles.brainFlow}>
            {BRAIN_STEPS.map((step, idx) => (
              <div key={step.num} className={styles.brainStepWrap}>
                <BrainStep step={step} />
                {idx < BRAIN_STEPS.length - 1 && <div className={styles.brainArrow}>→</div>}
              </div>
            ))}
          </div>
        </section>

        {/* ── Quick-start prompts ───────────────────────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>⚡ Quick-Start Templates</h2>
          <div className={styles.quickGrid}>
            {QUICK_PROMPTS.map((q) => (
              <button
                key={q.label}
                className={styles.quickCard}
                onClick={() => openWizard(q.prompt, q.module)}
              >
                <span className={styles.quickLabel}>{q.label}</span>
                <span className={styles.quickPromptPreview}>{q.prompt}</span>
                <span className={styles.quickOpenBtn}>Open in Wizard →</span>
              </button>
            ))}
          </div>
        </section>

        {/* ── All AI Modules ────────────────────────────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>🤖 All AI Modules</h2>
          <div className={styles.moduleGrid}>
            {ALL_MODULES.map((mod) => (
              <ModuleChip
                key={mod.id}
                mod={mod}
                onActivate={(id) => { onActivateModule?.(id); onClose(); }}
              />
            ))}
          </div>
        </section>

        {/* ── Writing Styles & Tones ────────────────────────────────────── */}
        <section className={styles.section}>
          <div className={styles.stylesRow}>
            <div className={styles.stylesBox}>
              <h3 className={styles.boxTitle}>✍️ 6 Writing Styles</h3>
              <div className={styles.tagList}>
                {['💼 Professional','😊 Casual','🎓 Academic','⚖️ Legal','🎨 Creative','📢 Persuasive'].map((s) => (
                  <span key={s} className={styles.tag}>{s}</span>
                ))}
              </div>
            </div>
            <div className={styles.stylesBox}>
              <h3 className={styles.boxTitle}>🎭 5 Tones</h3>
              <div className={styles.tagList}>
                {['👔 Formal','🤝 Friendly','🎯 Persuasive','📚 Informative','😄 Humorous'].map((t) => (
                  <span key={t} className={styles.tag}>{t}</span>
                ))}
              </div>
            </div>
            <div className={styles.stylesBox}>
              <h3 className={styles.boxTitle}>📄 Output Formats</h3>
              <div className={styles.tagList}>
                {['PDF','Word DOCX','Excel XLSX','PowerPoint PPTX','HTML','Markdown'].map((f) => (
                  <span key={f} className={styles.tag}>{f}</span>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ── Recent Documents ─────────────────────────────────────────── */}
        {recentDocs.length > 0 && (
          <section className={styles.section}>
            <h2 className={styles.sectionTitle}>📁 Recent Documents</h2>
            <div className={styles.recentList}>
              {recentDocs.slice(0, 6).map((doc) => (
                <div key={doc.id} className={styles.recentItem}>
                  <span className={styles.recentIcon}>📄</span>
                  <div className={styles.recentInfo}>
                    <p className={styles.recentTitle}>{doc.title || 'Untitled'}</p>
                    <p className={styles.recentMeta}>{doc.module} · {doc.created_at ? new Date(doc.created_at).toLocaleDateString() : ''}</p>
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* ── Feature highlights ────────────────────────────────────────── */}
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>🌟 System Features</h2>
          <div className={styles.featureGrid}>
            {[
              { icon: '🧠', title: 'Deep Intent Analysis',        desc: 'Detects document type, industry, audience & complexity before generating' },
              { icon: '📋', title: 'Editable Outline',            desc: 'Review and modify the document outline before any content is written' },
              { icon: '🔄', title: 'Regenerate Sections',         desc: 'Redo specific sections without regenerating the whole document' },
              { icon: '💾', title: 'Preference Memory',           desc: 'Saves your preferred writing style and tone across sessions' },
              { icon: '📡', title: 'Live Progress Stream',        desc: 'Real-time animated status messages during generation' },
              { icon: '👍', title: 'Feedback Loop',               desc: 'Rate outputs to help the system learn your preferences over time' },
              { icon: '🌐', title: 'Multi-language Support',      desc: 'Translate documents or generate content in multiple languages' },
              { icon: '🔗', title: 'Workflow Automation',         desc: 'Auto-convert documents to slides or extract data to Excel' },
            ].map((f) => (
              <div key={f.title} className={styles.featureCard}>
                <span className={styles.featureIcon}>{f.icon}</span>
                <div>
                  <strong className={styles.featureTitle}>{f.title}</strong>
                  <p className={styles.featureDesc}>{f.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* ── CTA bar ──────────────────────────────────────────────────── */}
        <div className={styles.ctaBar}>
          <button className={styles.ctaPrimary} onClick={() => openWizard('Write a professional business plan for a tech startup', 'business')}>
            ✨ Try HumanLoop Wizard Now
          </button>
          <button className={styles.ctaSecondary} onClick={() => { onActivateModule?.('document'); onClose(); }}>
            📄 Quick Generate
          </button>
          <button className={styles.ctaSecondary} onClick={() => { onActivateModule?.('classroom'); onClose(); }}>
            🏫 Open Classroom
          </button>
        </div>
      </div>

      {/* ── GenerationWizard modal ────────────────────────────────────── */}
      {showWizard && (
        <GenerationWizard
          prompt={wizardPrompt}
          module={wizardModule}
          authHeader={authHeader}
          onClose={() => setShowWizard(false)}
          onGenerate={(result) => {
            setShowWizard(false);
            onGenerate?.(result, wizardModule);
            onClose();
          }}
        />
      )}
    </div>
  );
}
