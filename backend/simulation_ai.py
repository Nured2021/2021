"""Real World Simulation AI – business cases, interviews, projects, letters."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class SimulationAI:
    """Generates business case studies, interview simulations, and more."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_interview    = any(w in lower for w in ["interview", "job", "hiring", "recruitment"])
        is_cover_letter = any(w in lower for w in ["cover letter", "application letter"])
        is_rec_letter   = any(w in lower for w in ["recommendation", "reference letter"])
        is_case_study   = any(w in lower for w in ["case study", "business case", "scenario"])

        title = f"Real-World Simulation: {topic}"

        if is_interview:
            return self._interview_simulation(topic, domain, keywords, kw_str, prompt)
        if is_cover_letter:
            return self._cover_letter(topic, domain, keywords, kw_str, prompt)
        if is_rec_letter:
            return self._recommendation_letter(topic, keywords, prompt)

        # Default: business case + interview + project
        return self._full_simulation(topic, domain, keywords, kw_str, prompt)

    def _full_simulation(self, topic, domain, keywords, kw_str, prompt) -> dict:
        title = f"Real-World Simulation: {topic}"
        sections = [
            {
                "heading": "Scenario Overview",
                "content": (
                    f"Simulation: {topic}\n"
                    f"Domain: {domain.title()}\n\n"
                    f"This simulation replicates professional conditions encountered in the "
                    f"{domain} sector. Participants engage with real-world constraints, "
                    f"stakeholder dynamics, and decision-making pressures.\n\n"
                    f"Core themes: {kw_str}"
                ),
            },
            {
                "heading": "Business Case Study",
                "content": (
                    f"Organisation: Nexus {domain.title()} Group (Scenario)\n"
                    f"Challenge: {topic}\n\n"
                    f"Background:\n"
                    f"Nexus Group is a mid-sized organisation operating in the {domain} sector. "
                    f"Following recent market shifts, the leadership team has identified {topic.lower()} "
                    f"as a critical strategic priority for the next 12 months.\n\n"
                    f"Key data points:\n"
                    f"  • Annual revenue: $8.5M (flat for 2 consecutive years)\n"
                    f"  • Staff: 120 employees across 4 divisions\n"
                    f"  • Challenge: {kw_str.split(',')[0].strip().title()} is underperforming vs. industry benchmark\n"
                    f"  • Opportunity: Emerging demand in {kw_str.split(',')[-1].strip()} market\n\n"
                    f"Your task: Prepare a 2-page strategic recommendation addressing {topic.lower()}. "
                    f"Include: problem diagnosis, proposed solution, resource requirements, and KPIs."
                ),
            },
            {
                "heading": "Job Interview Simulation",
                "content": (
                    f"Role: Senior {domain.title()} Analyst — {topic}\n\n"
                    f"Interviewer Questions:\n"
                    f"1. Walk us through your experience with {topic.lower()}. What's your most "
                    f"   significant achievement in this area?\n\n"
                    f"2. Describe a time you faced a major obstacle related to {kw_str.split(',')[0].strip() if keywords else topic.lower()}. "
                    f"   How did you resolve it?\n\n"
                    f"3. How do you stay current with developments in {domain.title()} — especially around {topic.lower()}?\n\n"
                    f"4. A key stakeholder disagrees with your approach to {topic.lower()}. "
                    f"   How do you handle it?\n\n"
                    f"5. Where do you see the field of {topic.lower()} heading in the next 3 years?\n\n"
                    f"Preparation tips:\n"
                    f"  • Use the STAR method: Situation → Task → Action → Result\n"
                    f"  • Quantify outcomes wherever possible\n"
                    f"  • Research the organisation's recent activities related to {topic.lower()}"
                ),
            },
            {
                "heading": "Industry Project",
                "content": (
                    f"Project: {topic}\n"
                    f"Duration: 8 weeks | Team: 4–6 people | Sector: {domain.title()}\n\n"
                    f"Phase 1 – Discovery (Weeks 1–2):\n"
                    f"  Conduct stakeholder interviews, map the current state of {topic.lower()}, "
                    f"  identify gaps and opportunities.\n\n"
                    f"Phase 2 – Analysis (Weeks 3–4):\n"
                    f"  Benchmark against best practice, analyse data on {kw_str}, "
                    f"  develop solution options.\n\n"
                    f"Phase 3 – Recommendations (Weeks 5–6):\n"
                    f"  Draft and validate the recommended approach. Build the implementation plan.\n\n"
                    f"Phase 4 – Presentation (Weeks 7–8):\n"
                    f"  Present findings to the executive panel. Respond to questions and refine."
                ),
            },
            {
                "heading": "Recommendation Letter Template",
                "content": (
                    f"[Date]\n\n"
                    f"To Whom It May Concern,\n\n"
                    f"It is my genuine pleasure to recommend [Candidate Name] for [Position/Programme]. "
                    f"During their engagement with our team on {topic.lower()}, they demonstrated "
                    f"exceptional capability in {kw_str}.\n\n"
                    f"Specifically, [Candidate Name] led [specific project or initiative related to {topic.lower()}], "
                    f"delivering [measurable outcome] ahead of schedule and under budget. Their approach "
                    f"to challenges in {domain} reflected both technical depth and strong professional judgement.\n\n"
                    f"I recommend [Candidate Name] without reservation for any role demanding expertise "
                    f"in {topic.lower()} and a proven track record in the {domain} sector.\n\n"
                    f"Sincerely,\n\n"
                    f"[Your Full Name]\n"
                    f"[Title, Organisation]\n"
                    f"[Email | Phone]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _interview_simulation(self, topic, domain, keywords, kw_str, prompt) -> dict:
        title = f"Interview Simulation: {topic}"
        sections = [
            {
                "heading": "Role Overview",
                "content": (
                    f"Position: {topic}\n"
                    f"Sector: {domain.title()}\n"
                    f"Level: Mid to Senior\n\n"
                    f"This simulation prepares you for a real interview for a role in {topic.lower()}. "
                    f"Practise each question out loud, then compare with the model answers below."
                ),
            },
            {
                "heading": "Competency Questions",
                "content": (
                    f"1. Tell me about yourself and why you are interested in {topic.lower()}.\n\n"
                    f"2. Describe your most impactful experience related to {kw_str.split(',')[0].strip() if keywords else topic.lower()}.\n\n"
                    f"3. Give an example of a time you worked across teams to deliver a result in {domain}.\n\n"
                    f"4. How do you handle ambiguity or shifting priorities in a fast-paced {domain} environment?\n\n"
                    f"5. What is your proudest professional achievement and how does it relate to {topic.lower()}?"
                ),
            },
            {
                "heading": "Technical / Knowledge Questions",
                "content": (
                    f"6. What are the most important trends shaping {topic.lower()} today?\n\n"
                    f"7. How would you approach a scenario where {kw_str.split(',')[0].strip() if keywords else 'a key process'} "
                    f"   is failing to meet targets?\n\n"
                    f"8. What tools, frameworks, or methodologies do you use in {domain.title()} work?\n\n"
                    f"9. How do you measure success in {topic.lower()}?\n\n"
                    f"10. What would you do in your first 90 days in this role?"
                ),
            },
            {
                "heading": "Model Answer Framework (STAR)",
                "content": (
                    f"Use the STAR method for every competency question:\n\n"
                    f"Situation: Set the context. What was happening with {topic.lower()}?\n"
                    f"Task: What was your specific responsibility?\n"
                    f"Action: What did YOU do? (Focus on your individual contribution)\n"
                    f"Result: What was the measurable outcome?\n\n"
                    f"Example structure:\n"
                    f"'When I was working on {topic.lower()} at [previous company], "
                    f"I was tasked with [specific challenge]. I [specific actions taken]. "
                    f"As a result, we achieved [quantified outcome].'"
                ),
            },
            {
                "heading": "Questions to Ask the Interviewer",
                "content": (
                    f"1. How does this role contribute to the organisation's strategy around {topic.lower()}?\n"
                    f"2. What does success look like in the first 6 months in this position?\n"
                    f"3. What are the biggest challenges the team faces in {domain.title()} right now?\n"
                    f"4. How does the team approach learning and development?\n"
                    f"5. What are the next steps in the selection process?"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _cover_letter(self, topic, domain, keywords, kw_str, prompt) -> dict:
        title = f"Cover Letter: {topic}"
        sections = [
            {
                "heading": "Header",
                "content": (
                    f"[Your Full Name]\n"
                    f"[Email] | [Phone] | [LinkedIn]\n"
                    f"[Date]\n\n"
                    f"[Hiring Manager Name]\n"
                    f"[Job Title]\n"
                    f"[Organisation Name]\n"
                    f"[Address]"
                ),
            },
            {
                "heading": "Opening Paragraph",
                "content": (
                    f"Dear [Hiring Manager Name],\n\n"
                    f"I am writing to express my strong interest in the {topic} position at "
                    f"[Organisation Name]. With [X] years of experience in {domain.title()} and "
                    f"a track record of delivering results in {kw_str}, I am confident I can "
                    f"make an immediate and lasting contribution to your team."
                ),
            },
            {
                "heading": "Core Experience",
                "content": (
                    f"In my current role as [Your Title] at [Current Organisation], I have:\n\n"
                    f"• Led initiatives focused on {kw_str.split(',')[0].strip() if keywords else topic.lower()}, "
                    f"achieving [specific measurable outcome]\n"
                    f"• Collaborated with cross-functional teams to [relevant achievement]\n"
                    f"• Developed expertise in {kw_str}, which aligns directly with the requirements "
                    f"for this {topic} role\n\n"
                    f"This experience has given me a deep understanding of the challenges and "
                    f"opportunities that define success in {domain.title()} today."
                ),
            },
            {
                "heading": "Why This Role & Organisation",
                "content": (
                    f"I am particularly drawn to [Organisation Name] because of [specific reason — "
                    f"research the company and reference something real, such as a recent initiative, "
                    f"their approach to {topic.lower()}, or their values].\n\n"
                    f"I am excited by the opportunity to bring my expertise in {kw_str} to an "
                    f"organisation that values [what they value] and is focused on [their goals]."
                ),
            },
            {
                "heading": "Closing",
                "content": (
                    f"I would welcome the opportunity to discuss how my background in {topic.lower()} "
                    f"can contribute to [Organisation Name]'s goals. I am available at your convenience "
                    f"for an interview and can be reached at [email] or [phone].\n\n"
                    f"Thank you for your time and consideration. I look forward to the possibility "
                    f"of joining your team.\n\n"
                    f"Yours sincerely,\n\n"
                    f"[Your Full Name]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _recommendation_letter(self, topic, keywords, prompt) -> dict:
        title = f"Recommendation Letter: {topic}"
        sections = [
            {
                "heading": "Letter",
                "content": (
                    f"[Date]\n\n"
                    f"To Whom It May Concern,\n\n"
                    f"I am writing to wholeheartedly recommend [Candidate Name] for {topic}. "
                    f"I have had the privilege of working closely with [Candidate Name] for "
                    f"[duration] in my capacity as [your role].\n\n"
                    f"During this time, [Candidate Name] consistently demonstrated exceptional "
                    f"skills in {', '.join(keywords[:3]) if keywords else topic.lower()}. "
                    f"Their contributions to [specific project or role] were outstanding.\n\n"
                    f"Key strengths:\n"
                    + "\n".join(f"  • {kw.title()}: [specific example of excellence]" for kw in keywords[:3])
                    + f"\n\nI have no hesitation in recommending [Candidate Name] for {topic}. "
                    f"They will be an asset to any team or programme they join.\n\n"
                    f"Please do not hesitate to contact me should you require further information.\n\n"
                    f"Yours faithfully,\n\n"
                    f"[Your Full Name]\n"
                    f"[Title, Organisation]\n"
                    f"[Email | Phone]"
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
