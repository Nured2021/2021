import { useEffect, useRef, useState } from "react";
import styles from "./PromptPanel.module.css";
import ChatPanel from "./ChatPanel";
import MaterialPicker from "./MaterialPicker";

/* ── Module metadata ──────────────────────────────────────────────── */

const TITLES = {
  // Office
  document:      "Documents AI",
  excel:         "Excel AI",
  presentation:  "Slides AI",
  uploads:       "Upload AI – File Reader",
  // Education
  edu_professor:    "Senior Professor AI",
  edu_teacher:      "Teacher AI",
  edu_exam:         "Exam Prep AI",
  edu_simulation:   "Simulations AI",
  edu_court:        "Court AI",
  edu_student:      "Student Assistant AI",
  edu_admin:        "Administrative AI",
  edu_multilingual: "Languages AI",
  edu_integrity:    "Academic Integrity AI",
  // Business & Pro
  business:  "Business AI",
  research:  "Research AI",
  analytics: "Analytics AI",
  content:   "Content AI",
  course:    "Course Builder AI",
};

const SUBTITLES = {
  document:         "Generate professional documents, reports, proposals, contracts, resumes and letters.",
  excel:            "Build real spreadsheets with data tables, formulas, and charts.",
  presentation:     "Create polished slide decks with layouts, bullet points, and speaker notes.",
  uploads:          "Upload any file (PDF, Word, Excel, TXT). AI reads it, summarises it, and suggests next steps.",
  edu_professor:    "Advanced academic content — syllabi, research papers, journal-level explanations.",
  edu_teacher:      "Lesson plans, topic explanations, classroom activities, and homework assignments.",
  edu_exam:         "Quizzes, exams, answer keys, flashcard sets and marking guides.",
  edu_simulation:   "Role-play scenarios, case studies, cover letters, and mock business situations.",
  edu_court:        "Legal documents — opening statements, contracts, briefs, cross-examination questions.",
  edu_student:      "Study guides, plain-language summaries, flashcards, and revision schedules.",
  edu_admin:        "Schedules, task trackers, deadline reminders, and file organisation plans.",
  edu_multilingual: "Translate documents, build bilingual glossaries, and localise content.",
  edu_integrity:    "Originality reviews, citation guides, AI-detection guidance, and ethics checks.",
  business:         "Business plans, investor pitch decks, SWOT analysis, marketing strategies, financial models.",
  research:         "Literature reviews, research papers, methodology guides, abstracts, and proposals.",
  analytics:        "KPI dashboards, trend analyses, data insights reports, and forecasts.",
  content:          "Blog posts, social media packs, email campaigns, press releases, and ad copy.",
  course:           "Full course curricula, syllabi, assessment plans, learning objectives, and reading lists.",
};

const PLACEHOLDERS = {
  document:         "e.g. Write a business proposal for an AI-powered tutoring platform...",
  excel:            "e.g. Create a project budget tracker with monthly targets and variance formulas...",
  presentation:     "e.g. Build a 7-slide investor pitch deck for an edtech startup...",
  uploads:          "Upload a file above — AI will read it and generate a summary automatically.",
  edu_professor:    "e.g. Create a university syllabus for Organisational Behaviour at postgraduate level...",
  edu_teacher:      "e.g. Lesson plan for teaching photosynthesis to Year 8 biology students...",
  edu_exam:         "e.g. Generate a 15-question quiz on the French Revolution with an answer key...",
  edu_simulation:   "e.g. Create a mock job interview simulation for a Senior Product Manager role...",
  edu_court:        "e.g. Prepare a full legal case package for an employment discrimination hearing...",
  edu_student:      "e.g. Create a 5-day study guide with flashcards for Newton's Laws of Motion...",
  edu_admin:        "e.g. Build a weekly schedule and task tracker for a 3-day academic conference...",
  edu_multilingual: "e.g. Translate this business proposal into French and Spanish...",
  edu_integrity:    "e.g. Review my research essay for plagiarism guidance and citation issues...",
  business:         "e.g. Write a full business plan for a SaaS startup in the education technology market...",
  research:         "e.g. Write a literature review on AI's impact on higher education outcomes...",
  analytics:        "e.g. Create a KPI dashboard report for a customer success team — retention and NPS...",
  content:          "e.g. Write an SEO blog post on the top 10 benefits of AI for small businesses...",
  course:           "e.g. Build a 10-week Data Science course curriculum for beginners...",
};

/* Quick-start template prompts per module */
const TEMPLATES = {
  document:         ["Business proposal for an AI tutoring platform", "Executive report on remote work trends in tech", "Service contract for a software development project"],
  excel:            ["Annual budget for a 20-person tech startup", "Project tracker with milestones, owners, and deadlines", "Sales pipeline tracker with conversion rate formulas"],
  presentation:     ["8-slide business presentation on AI in healthcare", "Investor pitch deck for a Series A edtech startup", "Quarterly review presentation for Q3 2024"],
  edu_professor:    ["University syllabus for Organisational Behaviour", "Advanced research paper on arbitration law", "PhD-level academic explanation of cognitive load theory"],
  edu_teacher:      ["Lesson plan on photosynthesis for Year 8", "Classroom activity on critical thinking skills", "Homework assignment on the causes of World War I"],
  edu_exam:         ["15-question quiz on the French Revolution with answer key", "Multiple choice exam on contract law principles", "Flashcard set for Newton's Laws of Motion"],
  edu_court:        ["Full case package for employment discrimination case", "Service contract for a digital marketing agency", "Legal brief for a contract dispute case"],
  edu_student:      ["5-day study guide for Newton's Laws of Motion", "Flashcards for human anatomy — cardiovascular system", "Summary of Dominion Stores v. UFCW for a first-year law student"],
  edu_simulation:   ["Mock interview for a Senior Product Manager role at Google", "Business case study on a startup in a regulatory crisis", "Cover letter for a Data Scientist at a top AI company"],
  edu_admin:        ["Weekly schedule for a fall semester with office hours", "Task tracker for a 3-day academic conference", "Deadline reminder schedule for final exam submissions"],
  edu_multilingual: ["Translate business proposal into French and Spanish", "Bilingual glossary of legal terms in English and Arabic", "Translate closing argument into German"],
  edu_integrity:    ["Originality check for my research paper on climate change", "Citation guide in APA format for my literature review", "AI detection review for my final essay on economics"],
  business:         ["Full business plan for an edtech SaaS startup", "Investor pitch deck for a Series A fundraise", "SWOT analysis for a consulting firm entering the AI market"],
  research:         ["Literature review on AI in higher education", "Research paper on effectiveness of online vs classroom learning", "PhD research proposal on social media and adolescent mental health"],
  analytics:        ["KPI dashboard for a customer success team", "Trend analysis on e-commerce growth in emerging markets", "Data insights report on employee productivity metrics"],
  content:          ["SEO blog post on AI benefits for small businesses", "LinkedIn, Twitter, Instagram content pack on productivity", "3-email drip campaign for an online course launch"],
  course:           ["10-week Data Science curriculum for beginners", "Full syllabus for a university course on Business Law", "Assessment plan for a 12-week software engineering bootcamp"],
};

/* Voice input hook — uses browser Web Speech API */
function useVoiceInput(onTranscript) {
  const [listening, setListening] = useState(false);
  const recognitionRef = useRef(null);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Voice input is not supported in your browser. Please use Chrome or Edge.");
      return;
    }
    const rec = new SpeechRecognition();
    rec.continuous = false;
    rec.interimResults = false;
    rec.lang = "en-US";
    rec.onresult = (e) => {
      const transcript = e.results[0][0].transcript;
      onTranscript(transcript);
    };
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    recognitionRef.current = rec;
    rec.start();
    setListening(true);
  };

  const stopListening = () => {
    recognitionRef.current?.stop();
    setListening(false);
  };

  return { listening, startListening, stopListening };
}

/* ── Component ───────────────────────────────────────────────────── */

export default function PromptPanel({
  docType,
  docFormat,
  onGenerate,
  onTranslate,
  loading,
  status,
  uploadedFileName,
  externalPrompt,
  onPromptConsumed,
}) {
  const [prompt, setPrompt]             = useState("");
  const [showTemplates, setShowTemplates] = useState(false);

  const { listening, startListening, stopListening } = useVoiceInput((text) =>
    setPrompt((prev) => (prev ? prev + " " + text : text))
  );

  useEffect(() => {
    if (externalPrompt != null) {
      setPrompt(externalPrompt);
      onPromptConsumed?.();
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [externalPrompt]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (prompt.trim()) onGenerate(prompt.trim());
  };

  const handleTranslate = () => {
    if (prompt.trim()) onTranslate(prompt.trim());
  };

  const handleMaterialPick = (snippet) => {
    setPrompt((prev) => snippet + (prev ? "\n\n" + prev : ""));
  };

  const handleTemplateClick = (tpl) => {
    setPrompt(tpl);
    setShowTemplates(false);
  };

  const isEducation = docType.startsWith("edu_");
  const isBusiness  = ["business","research","analytics","content","course"].includes(docType);
  const title       = TITLES[docType]     || "Easy AI";
  const subtitle    = SUBTITLES[docType]  || "Describe your request and let AI create it.";
  const placeholder = PLACEHOLDERS[docType] || "Type your request here...";
  const templates   = TEMPLATES[docType]  || [];
  const chatModule  = isEducation ? docType.replace("edu_", "") : null;

  return (
    <div className={styles.panel}>
      <div className={styles.header}>
        <h2 className={styles.title}>{title}</h2>
        <p className={styles.subtitle}>{subtitle}</p>
        {uploadedFileName && (
          <span className={styles.uploadBadge}>📎 {uploadedFileName}</span>
        )}
      </div>

      <form className={styles.form} onSubmit={handleSubmit}>
        <div className={styles.textareaWrapper}>
          <textarea
            className={styles.textarea}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder={placeholder}
            rows={8}
            disabled={loading}
          />
          {/* Voice input button */}
          <button
            type="button"
            className={`${styles.voiceBtn} ${listening ? styles.voiceActive : ""}`}
            onClick={listening ? stopListening : startListening}
            title={listening ? "Stop listening" : "Speak your prompt (voice input)"}
            disabled={loading}
          >
            {listening ? "🔴" : "🎤"}
          </button>
        </div>

        {/* Template quick-starts */}
        {templates.length > 0 && (
          <div className={styles.templateSection}>
            <button
              type="button"
              className={styles.templateToggle}
              onClick={() => setShowTemplates((v) => !v)}
            >
              {showTemplates ? "▲ Hide templates" : "▼ Quick start templates"}
            </button>
            {showTemplates && (
              <div className={styles.templateGrid}>
                {templates.map((tpl) => (
                  <button
                    key={tpl}
                    type="button"
                    className={styles.templateChip}
                    onClick={() => handleTemplateClick(tpl)}
                  >
                    {tpl}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Material picker row */}
        <div className={styles.materialRow}>
          <MaterialPicker onPick={handleMaterialPick} />
        </div>

        <div className={styles.actionRow}>
          <button
            type="submit"
            className={styles.button}
            disabled={loading || !prompt.trim()}
          >
            {loading ? (
              <>
                <span className={styles.spinner} />
                {status || "Generating…"}
              </>
            ) : (
              <>✦ Generate</>
            )}
          </button>

          <button
            type="button"
            className={`${styles.button} ${styles.outlineBtn}`}
            disabled={loading || !prompt.trim()}
            onClick={handleTranslate}
            title="Translate content using Languages AI"
          >
            🌐 Translate
          </button>

          {prompt.trim() && (
            <button
              type="button"
              className={`${styles.button} ${styles.clearBtn}`}
              disabled={loading}
              onClick={() => setPrompt("")}
              title="Clear prompt"
            >
              ✕
            </button>
          )}
        </div>

        {status && status !== "Ready" && (
          <p className={styles.statusText}>{status}</p>
        )}
      </form>

      {/* Education chat panel */}
      {chatModule && <ChatPanel module={chatModule} />}
    </div>
  );
}
