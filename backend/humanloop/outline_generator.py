"""Outline Generator – creates editable outlines before full generation."""

from typing import List, Optional
from dataclasses import dataclass, field


@dataclass
class OutlineSection:
    title:       str
    description: str
    is_required: bool        = True
    subsections: List[str]   = field(default_factory=list)


class OutlineGenerator:
    """Generates structured, editable outlines based on document type."""

    OUTLINES: dict[str, List[OutlineSection]] = {
        "business_plan": [
            OutlineSection("1. Executive Summary",      "High-level overview: mission, product, market, financials"),
            OutlineSection("2. Company Description",    "What the company does, its mission and vision"),
            OutlineSection("3. Market Analysis",        "Industry size, target market, competitive landscape"),
            OutlineSection("4. Products & Services",    "What you're offering and the value it provides"),
            OutlineSection("5. Marketing Strategy",     "How you'll attract and retain customers"),
            OutlineSection("6. Operations Plan",        "Day-to-day operations, supply chain, staffing"),
            OutlineSection("7. Management Team",        "Key founders and team members with roles"),
            OutlineSection("8. Financial Plan",         "Revenue projections, funding needs, break-even"),
            OutlineSection("9. Risk Assessment",        "Potential risks and mitigation strategies"),
            OutlineSection("10. Appendix",              "Supporting data, charts, and references"),
        ],
        "marketing_plan": [
            OutlineSection("1. Executive Summary",      "Goals and highlights of the marketing plan"),
            OutlineSection("2. Market Research",        "Customer personas, market size, and trends"),
            OutlineSection("3. Competitive Analysis",   "Who your competitors are and how you differ"),
            OutlineSection("4. Target Audience",        "Detailed profile of your ideal customer"),
            OutlineSection("5. Marketing Goals",        "SMART goals tied to business objectives"),
            OutlineSection("6. Marketing Channels",     "Social media, SEO, email, ads, partnerships"),
            OutlineSection("7. Content Strategy",       "Types of content and editorial calendar"),
            OutlineSection("8. Budget",                 "Allocation across channels and campaigns"),
            OutlineSection("9. KPIs & Metrics",         "How success will be measured"),
            OutlineSection("10. Timeline",              "Month-by-month execution roadmap"),
        ],
        "legal_contract": [
            OutlineSection("1. Parties",                "Full legal names and contact information of all parties"),
            OutlineSection("2. Recitals",               "Background context and purpose of the agreement"),
            OutlineSection("3. Definitions",            "Key terms used throughout the contract"),
            OutlineSection("4. Scope of Work",          "Services or deliverables being provided"),
            OutlineSection("5. Payment Terms",          "Fees, invoicing schedule, late payment terms"),
            OutlineSection("6. Term & Termination",     "Contract duration and exit conditions"),
            OutlineSection("7. Confidentiality",        "Non-disclosure obligations and exceptions"),
            OutlineSection("8. Intellectual Property",  "Ownership of work created under this agreement"),
            OutlineSection("9. Warranties & Liability", "Representations, guarantees, and liability limits"),
            OutlineSection("10. General Provisions",    "Governing law, dispute resolution, amendments, signatures"),
        ],
        "essay": [
            OutlineSection("1. Introduction",           "Hook, background context, and thesis statement"),
            OutlineSection("2. Body Paragraph 1",       "First main argument with supporting evidence"),
            OutlineSection("3. Body Paragraph 2",       "Second main argument with supporting evidence"),
            OutlineSection("4. Body Paragraph 3",       "Third main argument with supporting evidence"),
            OutlineSection("5. Counterargument",        "Acknowledge and rebut the opposing view"),
            OutlineSection("6. Conclusion",             "Restate thesis, summarize key points, call to action"),
        ],
        "lesson_plan": [
            OutlineSection("1. Lesson Overview",        "Topic, grade level, subject, and duration"),
            OutlineSection("2. Learning Objectives",    "What students will know and be able to do"),
            OutlineSection("3. Materials & Resources",  "Tools, handouts, technology needed"),
            OutlineSection("4. Introduction / Hook",    "Engaging opener to activate prior knowledge"),
            OutlineSection("5. Main Instruction",       "Core teaching content and explanation"),
            OutlineSection("6. Guided Practice",        "Teacher-led practice activities"),
            OutlineSection("7. Independent Practice",   "Student tasks done independently"),
            OutlineSection("8. Assessment",             "Formative or summative checks for understanding"),
            OutlineSection("9. Differentiation",        "Accommodations for diverse learners"),
            OutlineSection("10. Closure & Reflection",  "Wrap-up, review, and homework assignment"),
        ],
        "syllabus": [
            OutlineSection("1. Course Information",     "Title, code, credits, term, instructor details"),
            OutlineSection("2. Course Description",     "Overview and purpose of the course"),
            OutlineSection("3. Learning Outcomes",      "What students will achieve by the end"),
            OutlineSection("4. Required Materials",     "Textbooks, software, and resources"),
            OutlineSection("5. Course Schedule",        "Week-by-week topics and activities"),
            OutlineSection("6. Assessment & Grading",   "Breakdown of assignments, exams, participation"),
            OutlineSection("7. Course Policies",        "Attendance, academic integrity, late work"),
            OutlineSection("8. Resources & Support",    "Office hours, tutoring, library resources"),
        ],
        "study_guide": [
            OutlineSection("1. Topic Overview",         "Brief summary of the subject area"),
            OutlineSection("2. Key Concepts",           "Core ideas and definitions to remember"),
            OutlineSection("3. Important Formulas / Rules", "Any equations, rules, or frameworks"),
            OutlineSection("4. Key People / Events",    "Notable figures, dates, or milestones"),
            OutlineSection("5. Practice Questions",     "Sample exam-style questions"),
            OutlineSection("6. Answer Key",             "Answers and brief explanations"),
            OutlineSection("7. Memory Aids",            "Mnemonics, diagrams, or tables"),
        ],
        "presentation": [
            OutlineSection("1. Title Slide",            "Company/topic name, presenter, date"),
            OutlineSection("2. Agenda",                 "Overview of what will be covered"),
            OutlineSection("3. Problem / Opportunity",  "What challenge or gap exists"),
            OutlineSection("4. Solution",               "How you address the problem"),
            OutlineSection("5. Market / Audience",      "Who you serve and market size"),
            OutlineSection("6. Key Benefits",           "Top 3 reasons to care"),
            OutlineSection("7. Evidence / Data",        "Statistics, case studies, testimonials"),
            OutlineSection("8. Roadmap / Next Steps",   "What happens next"),
            OutlineSection("9. Q&A / Call to Action",   "Closing slide with clear CTA"),
        ],
        "report": [
            OutlineSection("1. Executive Summary",      "Key findings and recommendations at a glance"),
            OutlineSection("2. Introduction",           "Purpose, scope, and background of the report"),
            OutlineSection("3. Methodology",            "How data was collected and analyzed"),
            OutlineSection("4. Findings",               "Main data, results, and observations"),
            OutlineSection("5. Analysis",               "What the findings mean"),
            OutlineSection("6. Recommendations",        "Actionable steps based on the analysis"),
            OutlineSection("7. Conclusion",             "Summary of key takeaways"),
            OutlineSection("8. Appendix",               "Raw data, charts, and supporting materials"),
        ],
        "proposal": [
            OutlineSection("1. Executive Summary",      "Brief overview of the entire proposal"),
            OutlineSection("2. Problem Statement",      "The challenge this proposal addresses"),
            OutlineSection("3. Proposed Solution",      "Your approach and methodology"),
            OutlineSection("4. Scope of Work",          "Deliverables, milestones, and timeline"),
            OutlineSection("5. Team & Qualifications",  "Who will do the work and why they're qualified"),
            OutlineSection("6. Budget",                 "Cost breakdown and payment schedule"),
            OutlineSection("7. Terms & Conditions",     "Legal and administrative terms"),
            OutlineSection("8. Call to Action",         "Next steps and how to accept the proposal"),
        ],
        "resume": [
            OutlineSection("1. Contact Information",    "Name, phone, email, LinkedIn, location"),
            OutlineSection("2. Professional Summary",   "2-3 sentence career pitch"),
            OutlineSection("3. Work Experience",        "Roles in reverse-chronological order with achievements"),
            OutlineSection("4. Education",              "Degrees, certifications, institutions"),
            OutlineSection("5. Skills",                 "Technical and soft skills"),
            OutlineSection("6. Achievements / Awards",  "Notable accomplishments"),
            OutlineSection("7. Volunteer / Extra",      "Optional: relevant activities or projects"),
        ],
        "email": [
            OutlineSection("1. Subject Line",           "Clear and compelling subject"),
            OutlineSection("2. Greeting",               "Appropriate salutation"),
            OutlineSection("3. Opening Line",           "Context or reason for writing"),
            OutlineSection("4. Main Body",              "Core message or request"),
            OutlineSection("5. Call to Action",         "What you want the reader to do"),
            OutlineSection("6. Closing",                "Sign-off and signature"),
        ],
    }

    _DEFAULT_OUTLINE: List[OutlineSection] = [
        OutlineSection("1. Introduction",      "Context and purpose"),
        OutlineSection("2. Main Content",      "Core information and arguments"),
        OutlineSection("3. Supporting Points", "Evidence, examples, and analysis"),
        OutlineSection("4. Conclusion",        "Summary and next steps"),
    ]

    def generate_outline(
        self,
        doc_type: str,
        custom_topics: Optional[List[str]] = None,
    ) -> List[OutlineSection]:
        """Return an outline list for the given document type."""
        base = list(self.OUTLINES.get(doc_type, self._DEFAULT_OUTLINE))

        if custom_topics:
            for i, topic in enumerate(custom_topics[:3]):
                slot = i + 1
                if slot < len(base):
                    base[slot] = OutlineSection(
                        title       = f"{slot + 1}. {topic.strip().title()}",
                        description = f"Details and analysis about {topic.strip()}",
                    )
        return base

    def outline_to_text(self, outline: List[OutlineSection]) -> str:
        lines = ["📋 Document Outline:", ""]
        for s in outline:
            lines.append(f"  ☑ {s.title}")
            lines.append(f"     └ {s.description}")
        return "\n".join(lines)

    def outline_to_prompt_fragment(self, outline: List[OutlineSection]) -> str:
        """Convert outline to an instruction block for the AI prompt."""
        items = "\n".join(f"  {s.title}: {s.description}" for s in outline)
        return f"Follow this structure exactly:\n{items}"
