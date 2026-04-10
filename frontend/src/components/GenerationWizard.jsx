import { useState, useEffect, useRef } from 'react';
import styles from './GenerationWizard.module.css';

const API_BASE = import.meta.env.VITE_API_URL || '';

const STYLES_LIST = [
  { id: 'professional', label: 'Professional', icon: '💼', color: '#3b82f6' },
  { id: 'casual',       label: 'Casual',       icon: '😊', color: '#10b981' },
  { id: 'academic',     label: 'Academic',     icon: '🎓', color: '#8b5cf6' },
  { id: 'legal',        label: 'Legal',        icon: '⚖️', color: '#ef4444' },
  { id: 'creative',     label: 'Creative',     icon: '🎨', color: '#f59e0b' },
  { id: 'persuasive',   label: 'Persuasive',   icon: '📢', color: '#ec4899' },
];

const TONES_LIST = [
  { id: 'formal',      label: 'Formal',      icon: '👔' },
  { id: 'friendly',    label: 'Friendly',    icon: '🤝' },
  { id: 'persuasive',  label: 'Persuasive',  icon: '🎯' },
  { id: 'informative', label: 'Informative', icon: '📚' },
  { id: 'humorous',    label: 'Humorous',    icon: '😄' },
];

const PROGRESS_MESSAGES = [
  'Analyzing request…',
  'Planning structure…',
  'Writing content…',
  'Adding details…',
  'Polishing output…',
  'Finalizing…',
];

export default function GenerationWizard({ prompt, module, authHeader, onGenerate, onClose }) {
  const [step,          setStep]         = useState(1);
  const [analysis,      setAnalysis]     = useState(null);
  const [analyzeError,  setAnalyzeError] = useState(false);
  const [selectedStyle, setStyle]        = useState('professional');
  const [selectedTone,  setTone]         = useState('formal');
  const [outline,       setOutline]      = useState([]);
  const [newSection,    setNewSection]   = useState('');
  const [progress,      setProgress]     = useState(0);
  const [progressMsg,   setProgressMsg]  = useState(PROGRESS_MESSAGES[0]);
  const [generating,    setGenerating]   = useState(false);
  const [result,        setResult]       = useState(null);
  const [genError,      setGenError]     = useState('');
  const progressRef = useRef(null);

  /* ── Step 1: analyze on mount ─────────────────────────────────────────── */
  useEffect(() => {
    (async () => {
      try {
        const r = await fetch(`${API_BASE}/api/humanloop/analyze`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeader?.() },
          body: JSON.stringify({ prompt }),
        });
        if (!r.ok) throw new Error();
        const d = await r.json();
        setAnalysis(d);
        setStyle(d.suggested_style || 'professional');
        setTone(d.suggested_tone   || 'formal');

        // fetch outline
        const o = await fetch(`${API_BASE}/api/humanloop/outline`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeader?.() },
          body: JSON.stringify({ doc_type: d.document_type }),
        });
        if (!o.ok) throw new Error();
        const od = await o.json();
        setOutline(od.outline);
      } catch {
        setAnalyzeError(true);
        // use fallback
        setAnalysis({
          document_type:    'general_document',
          industry:         null,
          target_audience:  'general',
          estimated_length: '3–5 pages',
          complexity:       'Medium',
        });
        setOutline([
          { title: '1. Introduction',      description: 'Context and purpose',             selected: true },
          { title: '2. Main Content',      description: 'Core information and arguments',  selected: true },
          { title: '3. Supporting Points', description: 'Evidence, examples, and analysis',selected: true },
          { title: '4. Conclusion',        description: 'Summary and next steps',          selected: true },
        ]);
      }
    })();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* ── Generation ──────────────────────────────────────────────────────── */
  const handleGenerate = async () => {
    setGenerating(true);
    setGenError('');
    setProgress(0);
    setStep(4);

    // Animate progress bar
    let pct = 0;
    let msgIdx = 0;
    progressRef.current = setInterval(() => {
      pct = Math.min(pct + 7, 92);
      setProgress(pct);
      msgIdx = Math.min(Math.floor(pct / 18), PROGRESS_MESSAGES.length - 1);
      setProgressMsg(PROGRESS_MESSAGES[msgIdx]);
    }, 400);

    try {
      const r = await fetch(`${API_BASE}/api/humanloop/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...authHeader?.() },
        body: JSON.stringify({
          prompt,
          style:   selectedStyle,
          tone:    selectedTone,
          outline: outline.filter((s) => s.selected !== false),
          module:  module || '',
        }),
      });
      clearInterval(progressRef.current);
      if (!r.ok) {
        const err = await r.json().catch(() => ({}));
        throw new Error(err.detail || 'Generation failed');
      }
      const data = await r.json();
      setProgress(100);
      setProgressMsg('Done!');
      setResult(data);
      setStep(5);
    } catch (e) {
      clearInterval(progressRef.current);
      setGenError(e.message || 'Generation failed. Please try again.');
      setStep(3);
    } finally {
      setGenerating(false);
    }
  };

  const toggleSection = (i) => {
    setOutline((prev) => prev.map((s, idx) => idx === i ? { ...s, selected: !s.selected } : s));
  };

  const addSection = () => {
    if (!newSection.trim()) return;
    const num = outline.length + 1;
    setOutline((prev) => [...prev, { title: `${num}. ${newSection.trim()}`, description: 'Custom section', selected: true }]);
    setNewSection('');
  };

  const removeSection = (i) => setOutline((prev) => prev.filter((_, idx) => idx !== i));

  const stepLabels = ['Analyze', 'Style', 'Outline', 'Generate', 'Complete'];

  return (
    <div className={styles.overlay}>
      <div className={styles.wizard}>
        {/* Header */}
        <div className={styles.header}>
          <h2>✨ Generation Wizard</h2>
          <button className={styles.closeBtn} onClick={onClose} title="Close">✕</button>
        </div>

        {/* Step indicators */}
        <div className={styles.steps}>
          {stepLabels.map((label, i) => (
            <div key={label} className={`${styles.stepItem} ${step >= i + 1 ? styles.active : ''} ${step === i + 1 ? styles.current : ''}`}>
              <span className={styles.stepNum}>{i + 1}</span>
              <span className={styles.stepLabel}>{label}</span>
              {i < stepLabels.length - 1 && <span className={styles.stepLine} />}
            </div>
          ))}
        </div>

        <div className={styles.body}>
          {/* ── Step 1: Intent Analysis ──────────────────────────────── */}
          {step === 1 && (
            <div className={styles.stepContent}>
              <h3>🤖 Intent Analysis</h3>
              {!analysis ? (
                <div className={styles.loadingRow}><span className={styles.spin}>⟳</span> Analyzing your request…</div>
              ) : (
                <>
                  {analyzeError && <p className={styles.warnBanner}>⚠️ Could not reach server – using offline analysis.</p>}
                  <div className={styles.analysisCard}>
                    {[
                      ['📄 Document Type', analysis.document_type?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())],
                      ['🏭 Industry',       analysis.industry?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'General'],
                      ['🎯 Audience',       analysis.target_audience?.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()) || 'General'],
                      ['📏 Length',         analysis.estimated_length],
                      ['🔧 Complexity',     analysis.complexity],
                    ].map(([label, value]) => (
                      <div key={label} className={styles.analysisRow}>
                        <span className={styles.analysisLabel}>{label}</span>
                        <span className={styles.analysisValue}>{value}</span>
                      </div>
                    ))}
                  </div>
                  <button className={styles.primaryBtn} onClick={() => setStep(2)}>Continue →</button>
                </>
              )}
            </div>
          )}

          {/* ── Step 2: Style & Tone ──────────────────────────────────── */}
          {step === 2 && (
            <div className={styles.stepContent}>
              <h3>✍️ Choose Writing Style</h3>
              <div className={styles.styleGrid}>
                {STYLES_LIST.map((s) => (
                  <button
                    key={s.id}
                    className={`${styles.styleBtn} ${selectedStyle === s.id ? styles.selected : ''}`}
                    style={{ '--accent': s.color }}
                    onClick={() => setStyle(s.id)}
                  >
                    <span className={styles.styleIcon}>{s.icon}</span>
                    <span>{s.label}</span>
                  </button>
                ))}
              </div>

              <h3>🎭 Choose Tone</h3>
              <div className={styles.toneGrid}>
                {TONES_LIST.map((t) => (
                  <button
                    key={t.id}
                    className={`${styles.toneBtn} ${selectedTone === t.id ? styles.selected : ''}`}
                    onClick={() => setTone(t.id)}
                  >
                    <span>{t.icon}</span>
                    <span>{t.label}</span>
                  </button>
                ))}
              </div>

              <div className={styles.navRow}>
                <button className={styles.secondaryBtn} onClick={() => setStep(1)}>← Back</button>
                <button className={styles.primaryBtn} onClick={() => setStep(3)}>Continue →</button>
              </div>
            </div>
          )}

          {/* ── Step 3: Outline ──────────────────────────────────────── */}
          {step === 3 && (
            <div className={styles.stepContent}>
              <h3>📋 Edit Outline</h3>
              <p className={styles.hint}>Check the sections you want included. Uncheck to skip.</p>
              {genError && <p className={styles.errorBanner}>❌ {genError}</p>}
              <div className={styles.outlineList}>
                {outline.map((section, idx) => (
                  <label key={idx} className={`${styles.outlineItem} ${section.selected === false ? styles.unchecked : ''}`}>
                    <input
                      type="checkbox"
                      checked={section.selected !== false}
                      onChange={() => toggleSection(idx)}
                      className={styles.outlineCheck}
                    />
                    <div className={styles.outlineText}>
                      <strong>{section.title}</strong>
                      <span className={styles.outlineDesc}>{section.description}</span>
                    </div>
                    <button
                      type="button"
                      className={styles.removeBtn}
                      onClick={() => removeSection(idx)}
                      title="Remove section"
                    >✕</button>
                  </label>
                ))}
              </div>

              <div className={styles.addRow}>
                <input
                  type="text"
                  className={styles.addInput}
                  placeholder="Add a custom section…"
                  value={newSection}
                  onChange={(e) => setNewSection(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && addSection()}
                />
                <button type="button" className={styles.addBtn} onClick={addSection}>+ Add</button>
              </div>

              <div className={styles.navRow}>
                <button className={styles.secondaryBtn} onClick={() => setStep(2)}>← Back</button>
                <button
                  className={styles.generateBtn}
                  onClick={handleGenerate}
                  disabled={generating || outline.every((s) => s.selected === false)}
                >
                  🚀 Generate Document
                </button>
              </div>
            </div>
          )}

          {/* ── Step 4: Generating ───────────────────────────────────── */}
          {step === 4 && (
            <div className={styles.stepContent}>
              <h3>🚀 Generating your document…</h3>
              <div className={styles.progressWrap}>
                <div className={styles.progressBar}>
                  <div className={styles.progressFill} style={{ width: `${progress}%` }} />
                </div>
                <span className={styles.progressPct}>{progress}%</span>
              </div>
              <p className={styles.progressMsg}>{progressMsg}</p>
              <div className={styles.progressDetails}>
                <span>Style: <strong>{selectedStyle}</strong></span>
                <span>Tone: <strong>{selectedTone}</strong></span>
                <span>Sections: <strong>{outline.filter((s) => s.selected !== false).length}</strong></span>
              </div>
            </div>
          )}

          {/* ── Step 5: Result ────────────────────────────────────────── */}
          {step === 5 && result && (
            <div className={styles.stepContent}>
              <div className={styles.successBadge}>✅ Document Generated!</div>
              <h3 className={styles.resultTitle}>{result.title}</h3>

              <div className={styles.resultPreview}>
                <p>{result.body?.substring(0, 400)}{result.body?.length > 400 ? '…' : ''}</p>
              </div>

              <div className={styles.downloadRow}>
                {result.pdf_url  && <a className={styles.dlBtn} href={result.pdf_url}  target="_blank" rel="noreferrer">📄 PDF</a>}
                {result.docx_url && <a className={styles.dlBtn} href={result.docx_url} target="_blank" rel="noreferrer">📝 Word</a>}
                {result.pptx_url && <a className={styles.dlBtn} href={result.pptx_url} target="_blank" rel="noreferrer">📊 PPTX</a>}
                {result.xlsx_url && <a className={styles.dlBtn} href={result.xlsx_url} target="_blank" rel="noreferrer">📊 Excel</a>}
              </div>

              <div className={styles.feedbackRow}>
                <span>Was this helpful?</span>
                <button className={styles.feedbackBtn} title="Good result">👍</button>
                <button className={styles.feedbackBtn} title="Needs improvement">👎</button>
              </div>

              <div className={styles.navRow}>
                <button className={styles.secondaryBtn} onClick={() => { setStep(3); setResult(null); }}>🔄 Regenerate</button>
                <button className={styles.primaryBtn} onClick={() => onGenerate(result)}>Use This Document →</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
