"""Real World Simulation AI – business cases, interviews, projects, letters."""

from __future__ import annotations


class SimulationAI:
    """Generates business case studies, interview simulations, and more."""

    def generate(self, prompt: str) -> dict:
        title = f"Real-World Simulation: {prompt[:65]}"
        sections = [
            {
                "heading": "Scenario Overview",
                "content": (
                    f"Simulation request: {prompt}\n\n"
                    "This simulation is designed to replicate conditions encountered in "
                    "professional practice. Participants should engage as they would in a "
                    "real workplace or institutional setting."
                ),
            },
            {
                "heading": "Business Case Study",
                "content": (
                    "Company: GlobalVenture Inc. (fictional)\n"
                    "Industry: Relevant to the prompt topic\n"
                    "Challenge: The organisation faces a critical strategic decision "
                    "requiring analysis of market data, stakeholder interests, and "
                    "regulatory constraints.\n\n"
                    "Key Data Points:\n"
                    "• Annual revenue: $4.2M (declining 8% YoY)\n"
                    "• Headcount: 85 employees across three departments\n"
                    "• Primary constraint: Limited capital and upcoming compliance audit\n\n"
                    "Task: Prepare a recommendation memo addressing the core challenge."
                ),
            },
            {
                "heading": "Job Interview Simulation",
                "content": (
                    "Role: Senior Analyst / Associate (relevant to topic)\n\n"
                    "Interviewer Questions:\n"
                    "1. Walk me through a time you solved a complex problem under pressure.\n"
                    "2. How do you approach stakeholder management in a cross-functional team?\n"
                    "3. What is your understanding of the key regulatory framework in this area?\n"
                    "4. Describe your process for analysing ambiguous or incomplete data.\n\n"
                    "Preparation Tips:\n"
                    "• Use the STAR method (Situation, Task, Action, Result).\n"
                    "• Research the organisation's recent projects and challenges.\n"
                    "• Prepare two to three questions for the interviewer."
                ),
            },
            {
                "heading": "Industry Project",
                "content": (
                    "Project Title: [Derived from prompt]\n"
                    "Deliverable: A structured project plan with defined scope, milestones, "
                    "resource requirements, and success metrics.\n\n"
                    "Phase 1 – Discovery (Weeks 1–2): Stakeholder interviews, data gathering\n"
                    "Phase 2 – Analysis (Weeks 3–4): Gap analysis, benchmarking\n"
                    "Phase 3 – Recommendations (Week 5): Report drafting and review\n"
                    "Phase 4 – Presentation (Week 6): Final delivery to panel"
                ),
            },
            {
                "heading": "Recommendation Letter Template",
                "content": (
                    "[Date]\n\n"
                    "To Whom It May Concern,\n\n"
                    "It is my pleasure to recommend [Candidate Name] for [Position/Program]. "
                    "During their time working with me on [Project/Course], they demonstrated "
                    "exceptional analytical ability, professional conduct, and a genuine "
                    "commitment to excellence.\n\n"
                    "[Specific example of achievement or contribution.]\n\n"
                    "I recommend them without reservation.\n\n"
                    "Sincerely,\n"
                    "[Your Name]\n"
                    "[Title, Institution]"
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
