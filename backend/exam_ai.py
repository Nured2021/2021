"""Exam Prep AI – quizzes, exams, answer keys, and progress feedback."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class ExamAI:
    """Generates quizzes, final exams, answer keys, and feedback reports."""

    def generate(self, prompt: str, exam_type: str = "quiz") -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        # Detect exam type from prompt
        if any(w in lower for w in ["final", "end of year", "end-of-year"]):
            exam_type = "final"
        elif any(w in lower for w in ["midterm", "mid-term", "mid term"]):
            exam_type = "midterm"
        elif any(w in lower for w in ["quiz", "quick test"]):
            exam_type = "quiz"

        label = {"final": "Final Examination", "midterm": "Midterm Examination"}.get(exam_type, "Quiz")
        time_allowed = {"final": "3 hours", "midterm": "90 minutes"}.get(exam_type, "30 minutes")
        total_marks = {"final": "100", "midterm": "60"}.get(exam_type, "20")

        title = f"{label}: {topic}"
        sections = [
            {
                "heading": "Instructions",
                "content": (
                    f"{label}: {topic}\n"
                    f"Subject: {domain.title()}\n\n"
                    f"• Read each question carefully before answering.\n"
                    f"• Show all working where applicable — partial marks are awarded.\n"
                    f"• Time allowed: {time_allowed}\n"
                    f"• Total marks: {total_marks}\n"
                    f"• Answer ALL questions in Sections A and B. Choose ONE from Section C.\n"
                    f"• Write clearly. Illegible answers will not receive marks."
                ),
            },
            {
                "heading": "Section A – Multiple Choice (Multiple marks each)",
                "content": (
                    f"Circle the best answer for each question.\n\n"
                    f"1. Which of the following BEST describes {topic.lower()}?\n"
                    f"   a) A process for managing {kw_str.split(',')[0].strip() if keywords else 'resources'} at scale\n"
                    f"   b) A theoretical framework for understanding {kw_str.split(',')[-1].strip() if keywords else 'systems'}\n"
                    f"   c) A method for evaluating {kw_str.split(',')[1].strip() if len(keywords) > 1 else 'outcomes'}\n"
                    f"   d) A standard applied across {domain} sectors globally\n\n"
                    f"2. What is the PRIMARY purpose of {kw_str.split(',')[0].strip() if keywords else topic.lower()}?\n"
                    f"   a) To reduce operational complexity\n"
                    f"   b) To align outputs with strategic goals in {domain}\n"
                    f"   c) To improve stakeholder communication\n"
                    f"   d) To measure performance against benchmarks\n\n"
                    f"3. In the context of {topic.lower()}, which scenario represents best practice?\n"
                    f"   a) Applying the principle only when problems arise\n"
                    f"   b) Embedding the approach proactively within existing workflows\n"
                    f"   c) Delegating responsibility entirely to external parties\n"
                    f"   d) Reviewing the policy annually without adjustment"
                ),
            },
            {
                "heading": "Section B – Short Answer (marks each)",
                "content": (
                    f"Answer all questions. Be concise but complete.\n\n"
                    f"4. Define '{topic}' in your own words and explain why it matters "
                    f"in the field of {domain.title()}.\n"
                    f"   (4 marks)\n\n"
                    f"5. Explain TWO key differences between {kw_str.split(',')[0].strip() if keywords else 'approach A'} "
                    f"and {kw_str.split(',')[1].strip() if len(keywords) > 1 else 'approach B'} "
                    f"as they apply to {topic.lower()}.\n"
                    f"   (6 marks)\n\n"
                    f"6. Give one real-world example from the {domain} sector that illustrates "
                    f"the core principles of {topic.lower()}. Explain its significance.\n"
                    f"   (5 marks)"
                ),
            },
            {
                "heading": "Section C – Essay / Extended Response",
                "content": (
                    f"Choose ONE of the following. Write a structured essay response.\n\n"
                    f"Option A:\n"
                    f"Critically discuss the strengths and limitations of {topic.lower()} "
                    f"with reference to at least two theoretical perspectives. "
                    f"Support your argument with specific examples from the {domain} field.\n\n"
                    f"Option B:\n"
                    f"To what extent have recent developments in {domain.title()} changed how "
                    f"practitioners approach {topic.lower()}? Use evidence to support your position.\n\n"
                    f"({'30 marks' if exam_type == 'final' else '10 marks'})"
                ),
            },
            {
                "heading": "Answer Key & Marking Guide",
                "content": (
                    f"ANSWER KEY — {label}: {topic}\n\n"
                    f"Section A:\n"
                    f"  1. b) — {topic.title()} is best described as a theoretical framework\n"
                    f"  2. b) — Primary purpose is to align outputs with strategic goals\n"
                    f"  3. b) — Best practice: proactive embedding within workflows\n\n"
                    f"Section B Marking Criteria:\n"
                    f"  4. Award marks for: accurate definition + specific reference to {domain} context.\n"
                    f"  5. Award marks for: two clearly contrasted points with supporting evidence.\n"
                    f"  6. Award marks for: relevant example + clear link to {topic.lower()} principles.\n\n"
                    f"Section C Marking Criteria:\n"
                    f"  Award marks for: structured argument (intro/body/conclusion), two or more "
                    f"  perspectives cited, concrete examples, and a clear analytical conclusion.\n\n"
                    f"Grade Boundaries:\n"
                    f"  Distinction (70%+) | Merit (60–69%) | Pass (50–59%) | Fail (<50%)"
                ),
            },
            {
                "heading": "Student Progress Feedback",
                "content": (
                    f"Student Performance on: {topic}\n\n"
                    f"Strengths demonstrated:\n"
                    f"  ✓ Grasp of foundational concepts in {topic.lower()}\n"
                    f"  ✓ Ability to define key terms from {kw_str}\n"
                    f"  ✓ Use of real-world examples where prompted\n\n"
                    f"Areas for development:\n"
                    f"  △ Analytical depth in extended responses — move beyond description to evaluation\n"
                    f"  △ Strengthen the connection between {kw_str.split(',')[0].strip() if keywords else 'theory'} and evidence\n"
                    f"  △ Review the distinction between key concepts in {topic.lower()}\n\n"
                    f"Recommended next steps:\n"
                    f"  1. Re-read the core sections on {kw_str}\n"
                    f"  2. Practise timed essay writing on {topic.lower()}\n"
                    f"  3. Attend the next tutorial / office hours session\n"
                    f"  4. Review past papers and compare to the marking criteria above"
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
