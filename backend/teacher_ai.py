"""Teacher AI – lesson planning, topic explanations, homework help."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class TeacherAI:
    """Generates lesson plans, explanations, class activities, and study notes."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()

        title = f"Lesson Material: {topic}"
        sections = [
            {
                "heading": "Lesson Objectives",
                "content": (
                    f"Topic: {topic}\n"
                    f"Subject area: {domain.title()}\n\n"
                    f"By the end of this lesson, students will be able to:\n"
                    f"• Explain {topic.lower()} in their own words with clear examples.\n"
                    f"• Identify and apply the core principles of {kw_str.split(',')[0].strip()}.\n"
                    f"• Analyse how {topic.lower()} connects to real-world situations.\n"
                    f"• Evaluate competing perspectives on {kw_str.split(',')[-1].strip() if keywords else topic.lower()}."
                ),
            },
            {
                "heading": "Lesson Plan (60 minutes)",
                "content": (
                    f"Lesson: {topic}\n\n"
                    f"0–5 min   : Warm-up — Ask: 'What do you already know about {topic.lower()}?'\n"
                    f"5–15 min  : Direct instruction — Introduce key terms: {kw_str}\n"
                    f"15–30 min : Guided practice — Work through 2–3 examples of {topic.lower()} together\n"
                    f"30–45 min : Group activity — Students apply {kw_str.split(',')[0].strip()} to a scenario\n"
                    f"45–55 min : Class discussion — Review findings, address misconceptions\n"
                    f"55–60 min : Exit ticket — 'Name one key thing you learned about {topic.lower()} today'"
                ),
            },
            {
                "heading": "Topic Explanation",
                "content": (
                    f"Introduction to {topic}:\n\n"
                    f"{topic} is a fundamental concept in {domain.title()}. "
                    f"At its core, it refers to {kw_str}.\n\n"
                    f"How to explain it simply:\n"
                    f"Imagine you are explaining {topic.lower()} to someone with no background "
                    f"in {domain}. Start with a familiar analogy, then introduce the technical "
                    f"vocabulary step by step.\n\n"
                    f"Key vocabulary to teach:\n"
                    + "\n".join(f"  • {kw.title()}: [definition and example]" for kw in keywords[:4])
                    + f"\n\nCommon student misconceptions about {topic.lower()} and how to address them:\n"
                    f"  • Misconception 1: [common error] → Clarification: [correct understanding]\n"
                    f"  • Misconception 2: [common error] → Clarification: [correct understanding]"
                ),
            },
            {
                "heading": "Homework Assignment",
                "content": (
                    f"Homework: {topic}\n\n"
                    f"Task 1 (Comprehension): Read the assigned section on {topic.lower()} and "
                    f"write a 150-word summary in your own words.\n\n"
                    f"Task 2 (Application): Find one real-world example of {topic.lower()} in "
                    f"the news or your community. Explain how it relates to what we learned today.\n\n"
                    f"Task 3 (Reflection): Answer: 'What is the most important thing to understand "
                    f"about {topic.lower()} and why?' (3–5 sentences)\n\n"
                    f"Due: Next lesson. Bring your answers to share with the class."
                ),
            },
            {
                "heading": "Class Activity & Study Notes",
                "content": (
                    f"Activity: Think-Pair-Share on {topic}\n\n"
                    f"Step 1 – Think (2 min): Each student writes their thoughts on: "
                    f"'How does {topic.lower()} affect everyday life?'\n"
                    f"Step 2 – Pair (3 min): Discuss with a partner, identify two points of agreement.\n"
                    f"Step 3 – Share (5 min): Pairs share key insights with the class.\n\n"
                    f"Key Study Notes:\n"
                    + "\n".join(f"  • {kw.title()}: [Core definition and importance]" for kw in keywords)
                    + f"\n\nRevision checklist:\n"
                    f"  □ I can define {topic.lower()} accurately\n"
                    f"  □ I can give 2 examples from real life\n"
                    f"  □ I can explain the key concepts in {kw_str}\n"
                    f"  □ I am ready for the next assessment"
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
