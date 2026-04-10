"""Senior Professor AI – subject-expert academic content generation."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class ProfessorAI:
    """Generates high-level academic content: syllabi, research papers, exams."""

    def generate(self, prompt: str, subject: str = "general") -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        actual_subject = subject if subject != "general" else domain.title()

        title = f"Academic Content: {topic}"
        sections = [
            {
                "heading": "Course / Topic Overview",
                "content": (
                    f"Subject area: {actual_subject}\n"
                    f"Topic: {topic}\n"
                    f"Level: Senior Undergraduate / Postgraduate\n\n"
                    f"This material on {topic.lower()} is prepared at an advanced academic level. "
                    f"It integrates current scholarship, theoretical frameworks, and applied "
                    f"analysis relevant to {kw_str}. Students are expected to engage critically "
                    f"with primary sources and articulate well-supported independent arguments."
                ),
            },
            {
                "heading": "Syllabus",
                "content": (
                    f"Course: {topic}\n\n"
                    f"Week 1 – Foundations: Historical context and development of {topic.lower()}\n"
                    f"Week 2 – Theoretical Frameworks: Key theories and models applied to {kw_str.split(',')[0].strip()}\n"
                    f"Week 3 – Core Principles: In-depth examination of fundamental concepts\n"
                    f"Week 4 – Applied Analysis: Case studies and real-world applications in {actual_subject}\n"
                    f"Week 5 – Contemporary Issues: Current debates and emerging trends in {topic.lower()}\n"
                    f"Week 6 – Research Methods: Academic writing, citation, and research design\n"
                    f"Week 7 – Synthesis & Assessment: Review of key themes, final examination preparation\n\n"
                    f"Assessment:\n"
                    f"  • Coursework essay (40%): Critical analysis of a key concept in {topic.lower()}\n"
                    f"  • Group presentation (20%): Applied case study on {kw_str.split(',')[0].strip()}\n"
                    f"  • Final examination (40%): Structured essay questions"
                ),
            },
            {
                "heading": "Academic Explanation",
                "content": (
                    f"{topic} is examined through multiple analytical lenses within the field of "
                    f"{actual_subject}. Primary sources, landmark cases or foundational texts, and "
                    f"peer-reviewed literature form the backbone of this course.\n\n"
                    f"Key conceptual pillars:\n"
                    + "\n".join(f"  • {kw.title()}: Its role and significance in {topic.lower()}" for kw in keywords[:4])
                    + f"\n\nStudents will develop the ability to synthesise diverse perspectives on "
                    f"{topic.lower()} and apply theoretical knowledge to practical scenarios."
                ),
            },
            {
                "heading": "High-Level Exam Questions",
                "content": (
                    f"Examination: {topic}\n\n"
                    f"1. Critically evaluate the historical development of {topic.lower()} and its "
                    f"   contemporary relevance to {actual_subject}. (Essay, 2,500 words)\n\n"
                    f"2. Compare and contrast the two dominant theoretical frameworks used to "
                    f"   analyse {kw_str.split(',')[0].strip() if keywords else topic.lower()}. "
                    f"   Support your answer with specific examples. (40 marks)\n\n"
                    f"3. Using a case study of your choice, critically assess how {topic.lower()} "
                    f"   principles are applied in professional practice. (30 marks)\n\n"
                    f"4. To what extent have recent developments in {actual_subject} challenged "
                    f"   established doctrines in {topic.lower()}? (30 marks)"
                ),
            },
            {
                "heading": "Recommended Reading",
                "content": (
                    f"Essential Reading for {topic}:\n\n"
                    f"Primary Sources:\n"
                    f"  • Foundational textbook on {topic.lower()} (assigned by institution)\n"
                    f"  • Landmark works / cases relevant to {kw_str}\n\n"
                    f"Peer-Reviewed Journals:\n"
                    f"  • Journal of {actual_subject} (recent issues)\n"
                    f"  • Annual Review of {actual_subject.split()[0] if actual_subject else 'the Field'}\n\n"
                    f"Supplementary:\n"
                    f"  • Industry reports and policy documents\n"
                    f"  • Lecture notes and seminar readings (provided via course portal)\n"
                    f"  • Recommended online resources (see module guide)"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
