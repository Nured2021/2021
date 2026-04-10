"""Course Builder AI – course curriculum, learning objectives, lesson sequences."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class CourseBuilderAI:
    """Builds full course curricula, learning objectives, and lesson sequences."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_module   = any(w in lower for w in ["module", "unit", "chapter"])
        is_bootcamp = any(w in lower for w in ["bootcamp", "intensive", "crash course"])
        is_online   = any(w in lower for w in ["online", "e-learning", "mooc", "asynchronous"])
        num_weeks = 12 if "12" in lower else (8 if "8" in lower else (4 if "4" in lower else 10))

        title = f"Course: {topic}"
        sections = [
            {
                "heading": "Course Overview",
                "content": (
                    f"Course Title: {topic}\n"
                    f"Subject Domain: {domain.title()}\n"
                    f"Duration: {num_weeks} weeks\n"
                    f"Level: [Beginner / Intermediate / Advanced]\n"
                    f"Format: {'Online / Asynchronous' if is_online else 'In-person / Hybrid / Online'}\n"
                    f"Prerequisites: [What students need to know before starting]\n\n"
                    f"Course Description:\n"
                    f"This course provides a comprehensive, structured pathway through {topic.lower()}. "
                    f"Students will master {kw_str} through a combination of theory, "
                    f"applied exercises, case studies, and assessments. By the end, "
                    f"graduates will be equipped to [professional outcome]."
                ),
            },
            {
                "heading": "Learning Outcomes",
                "content": (
                    f"By completing {topic}, students will be able to:\n\n"
                    f"Knowledge (KNOW):\n"
                    + "\n".join(
                        f"  K{i+1}. Define and explain {kw.title()} in the context of {topic.lower()}"
                        for i, kw in enumerate(keywords[:3])
                    )
                    + f"\n  K{len(keywords[:3])+1}. Identify the key frameworks and theories underlying {topic.lower()}\n\n"
                    f"Skills (DO):\n"
                    + "\n".join(
                        f"  S{i+1}. Apply {kw.title()} to real-world {domain} scenarios"
                        for i, kw in enumerate(keywords[:3])
                    )
                    + f"\n  S{len(keywords[:3])+1}. Produce professional-quality work in {topic.lower()}\n\n"
                    f"Attitudes (BE):\n"
                    f"  A1. Demonstrate ethical and professional conduct in {domain.title()}\n"
                    f"  A2. Approach {topic.lower()} with critical thinking and evidence-based reasoning\n"
                    f"  A3. Collaborate effectively with peers on {kw_str} projects"
                ),
            },
            {
                "heading": "Curriculum Map",
                "content": (
                    f"Week-by-Week Curriculum: {topic}\n\n"
                    + self._build_curriculum(topic, domain, keywords, num_weeks, kw_str)
                ),
            },
            {
                "heading": "Assessment Structure",
                "content": (
                    f"Assessment plan for {topic}:\n\n"
                    f"Formative assessments (ongoing feedback — do not count toward final grade):\n"
                    f"  • Weekly quizzes on {kw_str} concepts (10 minutes, auto-graded)\n"
                    f"  • Peer discussion posts: 2 per module\n"
                    f"  • Reflective journal entries after key lessons\n\n"
                    f"Summative assessments (count toward final grade):\n\n"
                    f"  Assignment 1 (25%): [Written analysis of a {topic.lower()} scenario]\n"
                    f"    Due: End of Week {num_weeks // 4}\n\n"
                    f"  Assignment 2 (25%): [Applied project using {kw_str.split(',')[0].strip() if keywords else topic.lower()}]\n"
                    f"    Due: End of Week {num_weeks // 2}\n\n"
                    f"  Group Project (25%): [Collaborative case study on {topic.lower()}]\n"
                    f"    Due: End of Week {int(num_weeks * 0.75)}\n\n"
                    f"  Final Examination (25%): [Comprehensive assessment covering all modules]\n"
                    f"    Date: End of Week {num_weeks}\n\n"
                    f"Grading scale: A (90–100%), B (80–89%), C (70–79%), D (60–69%), F (<60%)"
                ),
            },
            {
                "heading": "Resources & Materials",
                "content": (
                    f"Required resources for {topic}:\n\n"
                    f"Core Textbook:\n"
                    f"  [Author (Year). Title of textbook on {topic.lower()}. Publisher.]\n\n"
                    f"Supplementary Reading:\n"
                    f"  • [Journal article 1 on {kw_str.split(',')[0].strip() if keywords else topic.lower()}]\n"
                    f"  • [Journal article 2 on {kw_str.split(',')[-1].strip() if keywords else 'related topic'}]\n"
                    f"  • [Industry report or policy document relevant to {topic.lower()}]\n\n"
                    f"Online Resources:\n"
                    f"  • Course portal: [LMS URL]\n"
                    f"  • Video lectures: [Platform URL]\n"
                    f"  • Discussion forum: [Community URL]\n\n"
                    f"Tools / Software (if applicable):\n"
                    f"  • [Tool 1 for {kw_str.split(',')[0].strip() if keywords else topic.lower()}]\n"
                    f"  • [Tool 2]"
                ),
            },
            {
                "heading": "Instructor Notes",
                "content": (
                    f"Delivery guidance for {topic}:\n\n"
                    f"Pacing: Each week covers approximately [X] hours of content. "
                    f"Allow extra time on {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"— this is where most students struggle.\n\n"
                    f"Engagement strategies:\n"
                    f"  • Open each session with a real-world example related to {topic.lower()}\n"
                    f"  • Use think-pair-share for complex concepts in {kw_str}\n"
                    f"  • Invite guest speakers from the {domain.title()} industry for Weeks "
                    f"  {num_weeks // 3} and {num_weeks // 2}\n\n"
                    f"Differentiation:\n"
                    f"  • Advanced learners: Extension readings on {kw_str.split(',')[-1].strip() if keywords else 'advanced topics'}\n"
                    f"  • Learners needing support: Provide {topic.lower()} concept cheat sheet + office hours\n\n"
                    f"Common misconceptions to address:\n"
                    f"  1. [Misconception about {kw_str.split(',')[0].strip() if keywords else topic.lower()}] → Correct by [teaching approach]\n"
                    f"  2. [Second misconception] → Correct by [example or demonstration]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    @staticmethod
    def _build_curriculum(topic: str, domain: str, keywords: list[str], num_weeks: int, kw_str: str) -> str:
        lines = []
        phases = [
            ("Foundations", keywords[:2] if len(keywords) >= 2 else [topic.split()[0]]),
            ("Core Concepts", keywords[2:4] if len(keywords) >= 4 else keywords[:2]),
            ("Applied Practice", keywords[4:] if len(keywords) >= 5 else keywords[-2:]),
            ("Advanced & Assessment", []),
        ]
        week = 1
        for phase_name, phase_kws in phases:
            weeks_in_phase = max(1, num_weeks // 4)
            lines.append(f"PHASE: {phase_name}")
            for _ in range(weeks_in_phase):
                if week > num_weeks:
                    break
                kw = phase_kws[(_ % len(phase_kws))] if phase_kws else topic.split()[0]
                lines.append(
                    f"  Week {week:>2}: Introduction to {kw.title()} — "
                    f"Lecture + workshop + quiz"
                )
                week += 1
            lines.append("")
        # Fill remaining weeks
        while week <= num_weeks:
            lines.append(f"  Week {week:>2}: Review, capstone project, and final examination prep")
            week += 1
        return "\n".join(lines)


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
