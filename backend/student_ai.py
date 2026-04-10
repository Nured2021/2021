"""Student Assistant AI – 24/7 learning companion, summaries, study guides."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class StudentAI:
    """Generates study guides, summaries, flashcards, and exam prep for students."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_flashcards = any(w in lower for w in ["flashcard", "flash card", "review cards"])
        is_summary    = any(w in lower for w in ["summary", "summarize", "summarise", "tldr", "overview"])
        is_notes      = any(w in lower for w in ["notes", "note-taking", "revision"])
        is_schedule   = any(w in lower for w in ["study plan", "study schedule", "revision schedule"])

        title = f"Study Guide: {topic}"
        sections = [
            {
                "heading": "What You Need to Know",
                "content": (
                    f"Topic: {topic}\n"
                    f"Subject: {domain.title()}\n"
                    f"Key areas: {kw_str}\n\n"
                    f"This study guide is designed to help you master {topic.lower()} efficiently. "
                    f"Work through each section in order. Test yourself at each stage before moving on. "
                    f"The goal is not just to memorise — it's to understand and apply."
                ),
            },
            {
                "heading": f"Core Concepts in {topic}",
                "content": (
                    "\n".join(
                        f"Concept {i+1}: {kw.title()}\n"
                        f"  What it means: {kw.title()} is a key element of {topic.lower()} that "
                        f"involves the principles and practices relevant to {domain} contexts.\n"
                        f"  Why it matters: Understanding {kw} is essential for answering exam "
                        f"  questions and applying {topic.lower()} in practice.\n"
                        f"  Remember: Connect {kw} to the broader theme of {kw_str.split(',')[0].strip() if keywords else topic.lower()}.\n"
                        for i, kw in enumerate(keywords[:4])
                    ) if keywords else (
                        f"Core Concept: {topic}\n"
                        f"  What it means: {topic} is a central topic in {domain.title()} that "
                        f"requires understanding of its definition, application, and significance.\n"
                        f"  Why it matters: Mastery of {topic.lower()} is tested in assessments "
                        f"and applied in professional practice."
                    )
                ),
            },
            {
                "heading": "Plain-Language Summary",
                "content": (
                    f"Here is {topic} explained simply:\n\n"
                    f"Imagine you are explaining {topic.lower()} to a friend who has never studied "
                    f"{domain}. You would say:\n\n"
                    f"'{topic} is basically about {kw_str}. "
                    f"The most important thing to understand is that {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"affects how we [act / think / make decisions] in {domain} situations. "
                    f"A simple example is: [imagine a situation where {kw_str.split(',')[-1].strip() if keywords else topic.lower()} "
                    f"applies in everyday life — that is what this topic is really about.]'\n\n"
                    f"Key things to remember:\n"
                    + "\n".join(f"  • {kw.title()} plays a role in how {topic.lower()} works" for kw in keywords[:3])
                ),
            },
            {
                "heading": "Self-Test Questions",
                "content": (
                    f"Test yourself on {topic} — try answering without notes first:\n\n"
                    f"1. Define {topic} in your own words. What are its key features?\n\n"
                    f"2. How does {kw_str.split(',')[0].strip() if keywords else 'the main concept'} "
                    f"   relate to {kw_str.split(',')[1].strip() if len(keywords) > 1 else 'its applications'}?\n\n"
                    f"3. Give a real-world example of {topic.lower()} in action. "
                    f"   Why is this example relevant?\n\n"
                    f"4. What are TWO common mistakes students make when studying {topic.lower()}? "
                    f"   How would you avoid them?\n\n"
                    f"5. If this came up in an exam, what would be the key points to cover "
                    f"   in a strong answer about {topic.lower()}?\n\n"
                    f"(Check your answers against your notes and the summary above.)"
                ),
            },
            {
                "heading": "Flashcards",
                "content": (
                    f"FLASHCARD SET: {topic}\n\n"
                    + "\n\n".join(
                        f"Card {i+1}\n"
                        f"FRONT: What is {kw.title()} in the context of {topic.lower()}?\n"
                        f"BACK:  {kw.title()} refers to the core principle / element of {topic.lower()} "
                        f"that involves [specific definition]. It matters because [significance in {domain}]."
                        for i, kw in enumerate(keywords[:5])
                    ) if keywords else (
                        f"Card 1\n"
                        f"FRONT: What is {topic}?\n"
                        f"BACK:  {topic} is the study of [definition] in the field of {domain.title()}.\n\n"
                        f"Card 2\n"
                        f"FRONT: Why does {topic.lower()} matter?\n"
                        f"BACK:  It matters because [significance and real-world application]."
                    )
                ),
            },
            {
                "heading": "Study Schedule",
                "content": (
                    f"Recommended 5-Day Revision Plan for {topic}:\n\n"
                    f"Day 1 (45 min): Read the core material on {topic.lower()}. "
                    f"Highlight key terms: {kw_str}.\n\n"
                    f"Day 2 (30 min): Write your own summary from memory. "
                    f"Don't look at your notes until you're done.\n\n"
                    f"Day 3 (20 min): Answer the self-test questions above without looking. "
                    f"Note which areas need more review.\n\n"
                    f"Day 4 (25 min): Focus only on your weak areas. "
                    f"Re-read and re-summarise those sections of {topic.lower()}.\n\n"
                    f"Day 5 (40 min): Practise with a past exam question on {topic.lower()}. "
                    f"Time yourself. Review against the marking criteria.\n\n"
                    f"Tips:\n"
                    f"  • Teach {topic.lower()} to a classmate — if you can explain it, you know it\n"
                    f"  • Use spaced repetition: revisit your flashcards on Days 1, 3, 7, 14\n"
                    f"  • Take breaks (Pomodoro: 25 min study → 5 min break)"
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
