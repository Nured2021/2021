"""Document AI – generates structured document content from a prompt."""

from __future__ import annotations

import re

from prompt_parser import extract_topic, extract_keywords, detect_domain, detect_intent


class DocumentAI:
    """Rule-based document content generator that personalises output for each prompt."""

    def generate(self, prompt: str, doc_type: str = "document") -> dict:
        """Return a dict with title, sections list, and raw text body."""
        title = self._make_title(prompt, doc_type)
        sections = self._make_sections(prompt, doc_type)
        body = self._sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _make_title(self, prompt: str, doc_type: str) -> str:
        topic = extract_topic(prompt)
        prefix = {
            "slides": "Presentation: ",
            "excel": "Data Sheet: ",
            "pdf": "",
            "doc": "",
        }.get(doc_type.lower(), "")
        return f"{prefix}{topic}"

    def _make_sections(self, prompt: str, doc_type: str) -> list[dict]:
        dt = doc_type.lower()
        if dt in ("slides", "presentation"):
            return self._presentation_sections(prompt)
        if dt in ("excel", "spreadsheet"):
            return self._spreadsheet_sections(prompt)
        return self._document_sections(prompt)

    # --- document ---

    def _document_sections(self, prompt: str) -> list[dict]:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        intent = detect_intent(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()

        # Determine document type from prompt
        lower = prompt.lower()
        is_proposal   = any(w in lower for w in ["proposal", "pitch", "bid"])
        is_report     = any(w in lower for w in ["report", "analysis", "review", "assessment"])
        is_letter     = any(w in lower for w in ["letter", "email", "memo", "message"])
        is_contract   = any(w in lower for w in ["contract", "agreement", "policy", "terms"])
        is_plan       = any(w in lower for w in ["plan", "strategy", "roadmap", "blueprint"])
        is_resume     = any(w in lower for w in ["resume", "cv", "curriculum vitae", "portfolio"])

        if is_resume:
            return self._resume_sections(prompt, topic)
        if is_contract:
            return self._contract_sections(prompt, topic)
        if is_letter:
            return self._letter_sections(prompt, topic)
        if is_proposal:
            return self._proposal_sections(prompt, topic, domain, kw_str)
        if is_report:
            return self._report_sections(prompt, topic, domain, kw_str)
        if is_plan:
            return self._plan_sections(prompt, topic, domain, kw_str)

        # Default: professional document
        return self._general_document_sections(prompt, topic, domain, kw_str)

    def _general_document_sections(self, prompt: str, topic: str, domain: str, kw_str: str) -> list[dict]:
        return [
            {
                "heading": "Executive Summary",
                "content": (
                    f"This document presents a comprehensive overview of {topic}.\n"
                    f"Key areas covered include: {kw_str}.\n\n"
                    f"The content is structured to provide clear, actionable insights for "
                    f"stakeholders involved in {topic.lower()}."
                ),
            },
            {
                "heading": "Background & Context",
                "content": (
                    f"{topic} is a critical area within the {domain} landscape. "
                    f"Understanding the underlying drivers and context is essential "
                    f"before addressing the core objectives.\n\n"
                    f"Key contextual factors:\n"
                    f"• Current environment and market conditions relevant to {topic.lower()}\n"
                    f"• Stakeholder expectations and priorities\n"
                    f"• Regulatory and compliance considerations applicable to this domain\n"
                    f"• Historical precedents and lessons learned"
                ),
            },
            {
                "heading": "Core Analysis",
                "content": (
                    f"A detailed analysis of {topic} reveals the following findings:\n\n"
                    f"Strengths:\n"
                    f"• Strong foundation in {kw_str.split(',')[0].strip()} with clear value proposition\n"
                    f"• Demonstrated outcomes and measurable impact\n"
                    f"• Alignment with strategic objectives\n\n"
                    f"Opportunities:\n"
                    f"• Potential for growth and expansion in the {domain} sector\n"
                    f"• Partnership and collaboration possibilities\n"
                    f"• Technology and process improvement pathways\n\n"
                    f"Challenges:\n"
                    f"• Resource constraints and capacity planning requirements\n"
                    f"• Risk factors requiring active management\n"
                    f"• Competitive and environmental pressures"
                ),
            },
            {
                "heading": "Recommendations",
                "content": (
                    f"Based on the analysis of {topic}, the following recommendations are proposed:\n\n"
                    f"1. Establish clear objectives and measurable KPIs aligned with {topic.lower()} goals.\n"
                    f"2. Allocate dedicated resources and assign accountable owners for each workstream.\n"
                    f"3. Develop a phased implementation roadmap with defined milestones.\n"
                    f"4. Implement a monitoring framework to track progress and course-correct as needed.\n"
                    f"5. Engage key stakeholders through regular communication and reporting cycles."
                ),
            },
            {
                "heading": "Implementation Plan",
                "content": (
                    f"Phase 1 – Foundation (Weeks 1–4):\n"
                    f"  Set up governance, confirm scope, assign team leads for {topic.lower()}.\n\n"
                    f"Phase 2 – Execution (Weeks 5–12):\n"
                    f"  Deliver core workstreams, conduct regular progress reviews.\n\n"
                    f"Phase 3 – Review & Optimise (Weeks 13–16):\n"
                    f"  Assess outcomes against KPIs, refine processes, document learnings.\n\n"
                    f"Phase 4 – Sustain & Scale:\n"
                    f"  Embed successful practices, plan next iteration."
                ),
            },
            {
                "heading": "Conclusion",
                "content": (
                    f"In conclusion, {topic} represents a significant opportunity when approached "
                    f"with a structured methodology, clear ownership, and consistent execution.\n\n"
                    f"The recommendations and implementation plan outlined in this document provide "
                    f"a practical pathway forward. Sustained commitment and regular review will be "
                    f"critical to achieving the desired outcomes."
                ),
            },
        ]

    def _proposal_sections(self, prompt: str, topic: str, domain: str, kw_str: str) -> list[dict]:
        return [
            {
                "heading": "Executive Summary",
                "content": (
                    f"This proposal outlines a structured approach to {topic}.\n"
                    f"It presents the problem, proposed solution, expected outcomes, "
                    f"and resource requirements for your consideration."
                ),
            },
            {
                "heading": "Problem Statement",
                "content": (
                    f"The current situation regarding {topic.lower()} presents the following challenges:\n"
                    f"• Lack of a unified, scalable approach to address {kw_str}\n"
                    f"• Increasing demand that existing solutions are unable to meet\n"
                    f"• Operational inefficiencies resulting in cost and time overruns\n"
                    f"• Risk exposure in areas of compliance and quality assurance\n\n"
                    f"Without intervention, these issues will compound over time."
                ),
            },
            {
                "heading": "Proposed Solution",
                "content": (
                    f"We propose to address {topic.lower()} through the following approach:\n\n"
                    f"Core Offering:\n"
                    f"  A purpose-built solution targeting the key pain points identified above, "
                    f"  leveraging best practices from the {domain} sector.\n\n"
                    f"Key Features:\n"
                    f"• End-to-end coverage of {kw_str}\n"
                    f"• Scalable architecture to grow with your needs\n"
                    f"• Clear SLAs and quality benchmarks\n"
                    f"• Dedicated support and onboarding"
                ),
            },
            {
                "heading": "Expected Outcomes & Benefits",
                "content": (
                    f"Upon successful implementation of {topic}, you can expect:\n\n"
                    f"• 20–35% improvement in efficiency for processes related to {kw_str.split(',')[0].strip()}\n"
                    f"• Measurable reduction in operational risk and compliance exposure\n"
                    f"• Improved stakeholder satisfaction and confidence\n"
                    f"• Clear ROI within 6–12 months post-deployment\n"
                    f"• A scalable foundation for future enhancements"
                ),
            },
            {
                "heading": "Timeline & Budget",
                "content": (
                    f"Timeline:\n"
                    f"  Month 1: Discovery, planning, and stakeholder alignment\n"
                    f"  Month 2–3: Development and implementation of core components\n"
                    f"  Month 4: Testing, training, and go-live preparation\n"
                    f"  Month 5+: Ongoing support and optimisation\n\n"
                    f"Budget Estimate:\n"
                    f"  Initial investment: To be confirmed based on scope finalisation\n"
                    f"  Ongoing costs: Monthly retainer for support and maintenance\n"
                    f"  ROI Target: Break-even within Year 1"
                ),
            },
            {
                "heading": "Next Steps",
                "content": (
                    f"To move forward with this proposal for {topic}:\n\n"
                    f"1. Schedule a discovery call to align on scope and requirements (this week)\n"
                    f"2. Review and confirm the proposed timeline and resource plan\n"
                    f"3. Sign off on the statement of work\n"
                    f"4. Kick off Phase 1 within 5 business days of agreement\n\n"
                    f"We are confident that this proposal delivers a compelling solution. "
                    f"We look forward to partnering with you on {topic.lower()}."
                ),
            },
        ]

    def _report_sections(self, prompt: str, topic: str, domain: str, kw_str: str) -> list[dict]:
        return [
            {
                "heading": "Report Summary",
                "content": (
                    f"This report presents findings and analysis for: {topic}.\n"
                    f"Scope: {kw_str}\n"
                    f"Prepared for: [Relevant stakeholders]\n"
                    f"Date: [Current date]\n\n"
                    f"This report draws on available data, observations, and established "
                    f"frameworks within the {domain} domain."
                ),
            },
            {
                "heading": "Findings",
                "content": (
                    f"Key findings from the analysis of {topic}:\n\n"
                    f"Finding 1: Current performance against benchmarks\n"
                    f"  The data indicates that {kw_str.split(',')[0].strip()} is performing "
                    f"  within expected parameters in some areas, but shows gaps in others.\n\n"
                    f"Finding 2: Risk areas identified\n"
                    f"  Several risk factors have been identified that require attention, "
                    f"  particularly around resource allocation and process consistency.\n\n"
                    f"Finding 3: Opportunity areas\n"
                    f"  There are clear opportunities to improve outcomes in {topic.lower()} "
                    f"  by applying the recommendations outlined in this report."
                ),
            },
            {
                "heading": "Data Analysis",
                "content": (
                    f"Quantitative Analysis of {topic}:\n\n"
                    f"Metric              | Current   | Target    | Gap\n"
                    f"--------------------|-----------|-----------|--------\n"
                    f"Performance Score   | 72%       | 90%       | -18%\n"
                    f"Process Efficiency  | 65%       | 85%       | -20%\n"
                    f"Stakeholder Sat.    | 78%       | 90%       | -12%\n"
                    f"Compliance Rate     | 88%       | 100%      | -12%\n\n"
                    f"Note: Figures are indicative. Replace with actual measured data."
                ),
            },
            {
                "heading": "Conclusions & Recommendations",
                "content": (
                    f"Based on the findings above, the following conclusions are drawn:\n\n"
                    f"1. {topic} requires targeted improvement in efficiency and compliance.\n"
                    f"2. Investment in training and process redesign will yield measurable gains.\n"
                    f"3. A monitoring framework should be established to track progress monthly.\n\n"
                    f"Immediate Actions:\n"
                    f"• Assign a lead responsible for implementation oversight\n"
                    f"• Begin gap-closure activities within 2 weeks\n"
                    f"• Report progress to stakeholders at the end of each month"
                ),
            },
        ]

    def _plan_sections(self, prompt: str, topic: str, domain: str, kw_str: str) -> list[dict]:
        return [
            {
                "heading": "Plan Overview",
                "content": (
                    f"Strategic Plan: {topic}\n\n"
                    f"This plan provides a structured roadmap for achieving objectives related "
                    f"to {topic.lower()} within the {domain} context.\n"
                    f"Key themes: {kw_str}"
                ),
            },
            {
                "heading": "Goals & Objectives",
                "content": (
                    f"Primary Goal: Successfully deliver {topic.lower()} on time and on budget.\n\n"
                    f"Objectives:\n"
                    f"• Objective 1: Define and agree the full scope of {topic.lower()}\n"
                    f"• Objective 2: Secure necessary resources and stakeholder commitment\n"
                    f"• Objective 3: Execute all workstreams according to the agreed timeline\n"
                    f"• Objective 4: Deliver measurable outcomes aligned to strategic priorities\n"
                    f"• Objective 5: Embed learnings and establish long-term sustainability"
                ),
            },
            {
                "heading": "Action Plan",
                "content": (
                    f"Phase 1 – Initiate (Month 1):\n"
                    f"  Task 1.1: Conduct stakeholder mapping and engagement plan\n"
                    f"  Task 1.2: Finalise scope, objectives, and success criteria\n"
                    f"  Task 1.3: Confirm budget, resources, and governance model\n\n"
                    f"Phase 2 – Execute (Months 2–4):\n"
                    f"  Task 2.1: Deliver core activities per agreed workplan\n"
                    f"  Task 2.2: Conduct weekly progress reviews and risk monitoring\n"
                    f"  Task 2.3: Communicate updates to all stakeholders\n\n"
                    f"Phase 3 – Close & Sustain (Month 5):\n"
                    f"  Task 3.1: Review final outputs against objectives\n"
                    f"  Task 3.2: Document lessons learned\n"
                    f"  Task 3.3: Hand over ongoing responsibilities"
                ),
            },
            {
                "heading": "Risk Register",
                "content": (
                    f"Risk                          | Likelihood | Impact | Mitigation\n"
                    f"------------------------------|-----------|--------|----------------------------------\n"
                    f"Scope creep                   | Medium    | High   | Change control process in place\n"
                    f"Resource unavailability       | Low       | High   | Backup resource identified\n"
                    f"Stakeholder misalignment      | Medium    | Medium | Regular comms and check-ins\n"
                    f"Timeline delays               | Medium    | High   | Buffer built into schedule\n"
                    f"Budget overrun                | Low       | High   | Monthly financial review"
                ),
            },
            {
                "heading": "Success Metrics",
                "content": (
                    f"The success of {topic} will be measured by:\n\n"
                    f"• On-time delivery: All milestones completed within agreed dates\n"
                    f"• Budget adherence: Final cost within 5% of approved budget\n"
                    f"• Quality: Output meets agreed acceptance criteria\n"
                    f"• Stakeholder satisfaction: Post-project survey score ≥ 85%\n"
                    f"• Sustainability: Processes embedded and running independently within 90 days"
                ),
            },
        ]

    def _letter_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Letter Details",
                "content": (
                    f"Subject: {topic}\n\n"
                    f"Date: [Date]\n"
                    f"From: [Your Name]\n"
                    f"      [Your Title / Organisation]\n"
                    f"To:   [Recipient Name]\n"
                    f"      [Recipient Title / Organisation]"
                ),
            },
            {
                "heading": "Opening",
                "content": (
                    f"Dear [Recipient Name],\n\n"
                    f"I am writing to you regarding {topic.lower()}. "
                    f"This letter sets out the key points and our position "
                    f"on the matter described below."
                ),
            },
            {
                "heading": "Main Body",
                "content": (
                    f"The purpose of this correspondence is to address {topic.lower()}.\n\n"
                    f"Background:\n"
                    f"[Provide relevant context and background information here]\n\n"
                    f"Key Points:\n"
                    f"1. [First key point with supporting detail]\n"
                    f"2. [Second key point with supporting detail]\n"
                    f"3. [Third key point with supporting detail]\n\n"
                    f"Our Position:\n"
                    f"[Clearly state your position, request, or recommendation]"
                ),
            },
            {
                "heading": "Closing",
                "content": (
                    f"We trust that the above addresses the matter of {topic.lower()} clearly.\n"
                    f"Should you require any further information, please do not hesitate to contact us.\n\n"
                    f"Yours sincerely,\n\n"
                    f"[Signature]\n"
                    f"[Full Name]\n"
                    f"[Title]\n"
                    f"[Organisation]\n"
                    f"[Contact Details]"
                ),
            },
        ]

    def _contract_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Agreement Header",
                "content": (
                    f"AGREEMENT FOR {topic.upper()}\n\n"
                    f"This Agreement is entered into as of [Date] between:\n\n"
                    f"Party A: [Full Legal Name], [Address] ('Party A')\n"
                    f"Party B: [Full Legal Name], [Address] ('Party B')\n\n"
                    f"(collectively referred to as 'the Parties')"
                ),
            },
            {
                "heading": "1. Scope of Agreement",
                "content": (
                    f"1.1 Party A agrees to provide the following in relation to {topic.lower()}:\n"
                    f"    [Detailed description of services, deliverables, or obligations]\n\n"
                    f"1.2 Party B agrees to:\n"
                    f"    [Corresponding obligations, payments, or cooperation requirements]\n\n"
                    f"1.3 This Agreement covers the following scope:\n"
                    f"    [Geographic scope, subject matter boundaries, exclusions]"
                ),
            },
            {
                "heading": "2. Term & Termination",
                "content": (
                    f"2.1 This Agreement commences on [Start Date] and continues until "
                    f"[End Date] unless terminated earlier.\n\n"
                    f"2.2 Either party may terminate this Agreement on [notice period] "
                    f"written notice to the other party.\n\n"
                    f"2.3 Either party may terminate immediately if the other party "
                    f"materially breaches this Agreement and fails to remedy the breach "
                    f"within 14 days of written notice."
                ),
            },
            {
                "heading": "3. Consideration & Payment",
                "content": (
                    f"3.1 In consideration of the services provided, Party B agrees to pay "
                    f"[Amount] in [Currency] payable [payment terms].\n\n"
                    f"3.2 Invoices shall be issued [frequency] and are due within [days] days.\n\n"
                    f"3.3 Late payment will incur interest at [rate]% per month on outstanding balances."
                ),
            },
            {
                "heading": "4. Confidentiality & IP",
                "content": (
                    f"4.1 Both parties agree to keep confidential all non-public information "
                    f"relating to this Agreement and each other's operations.\n\n"
                    f"4.2 Intellectual property created in the course of this Agreement "
                    f"shall vest in [Party A / Party B / jointly] as agreed in Schedule 1.\n\n"
                    f"4.3 This confidentiality obligation survives termination for a period of [years]."
                ),
            },
            {
                "heading": "5. Governing Law & Signatures",
                "content": (
                    f"5.1 This Agreement is governed by the laws of [Jurisdiction].\n\n"
                    f"5.2 Any disputes shall first be resolved through good-faith negotiation; "
                    f"failing which, through [arbitration / courts of Jurisdiction].\n\n"
                    f"AGREED AND SIGNED:\n\n"
                    f"___________________________    ___________________________\n"
                    f"[Party A Authorised Signatory]   [Party B Authorised Signatory]\n"
                    f"Name:                             Name:\n"
                    f"Title:                            Title:\n"
                    f"Date:                             Date:"
                ),
            },
        ]

    def _resume_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Personal Profile",
                "content": (
                    f"[Full Name]\n"
                    f"[Email Address] | [Phone Number] | [LinkedIn / Portfolio URL]\n"
                    f"[City, Country]\n\n"
                    f"Professional Summary:\n"
                    f"A results-driven professional with expertise in {topic.lower()}. "
                    f"Track record of delivering high-impact outcomes across [relevant industries]. "
                    f"Adept at [key skill 1], [key skill 2], and [key skill 3]. "
                    f"Seeking a role where I can apply my experience to drive meaningful results."
                ),
            },
            {
                "heading": "Professional Experience",
                "content": (
                    f"[Current / Most Recent Role] — [Company Name], [City]\n"
                    f"[Start Date] – Present\n"
                    f"• [Key achievement 1 with measurable outcome]\n"
                    f"• [Key achievement 2 with measurable outcome]\n"
                    f"• [Key achievement 3 with measurable outcome]\n\n"
                    f"[Previous Role] — [Company Name], [City]\n"
                    f"[Start Date] – [End Date]\n"
                    f"• [Key achievement 1]\n"
                    f"• [Key achievement 2]"
                ),
            },
            {
                "heading": "Education",
                "content": (
                    f"[Degree / Qualification] in [Subject] — [Institution], [Year]\n\n"
                    f"[Certification / Short Course] — [Provider], [Year]\n\n"
                    f"[Additional relevant qualification if applicable]"
                ),
            },
            {
                "heading": "Skills",
                "content": (
                    f"Technical Skills: [Skill 1], [Skill 2], [Skill 3], [Skill 4]\n\n"
                    f"Soft Skills: Leadership, communication, problem-solving, "
                    f"stakeholder management, critical thinking\n\n"
                    f"Tools & Platforms: [Relevant tools for {topic.lower()}]"
                ),
            },
            {
                "heading": "References",
                "content": "Available upon request."
            },
        ]

    # --- presentation ---

    def _presentation_sections(self, prompt: str) -> list[dict]:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_bullets = "\n".join(f"• {kw.title()}" for kw in keywords) if keywords else f"• {topic}"

        return [
            {
                "heading": "Slide 1 – Title",
                "content": (
                    f"{topic}\n\n"
                    f"Presented by: [Your Name]\n"
                    f"Date: [Presentation Date]\n"
                    f"Organisation: [Your Organisation]"
                ),
            },
            {
                "heading": "Slide 2 – Agenda",
                "content": (
                    f"Today's Agenda\n\n"
                    f"1. Introduction & Background\n"
                    f"2. The Challenge / Opportunity\n"
                    f"3. Our Approach\n"
                    f"4. Key Findings & Insights\n"
                    f"5. Recommendations\n"
                    f"6. Next Steps & Q&A"
                ),
            },
            {
                "heading": "Slide 3 – Introduction",
                "content": (
                    f"What is {topic}?\n\n"
                    f"{topic} is a critical topic in the {domain} space. "
                    f"Understanding its drivers and implications is essential "
                    f"for informed decision-making.\n\n"
                    f"Key themes we will explore:\n"
                    f"{kw_bullets}"
                ),
            },
            {
                "heading": "Slide 4 – The Challenge",
                "content": (
                    f"Why {topic} Matters\n\n"
                    f"• Growing complexity and demand in the {domain} sector\n"
                    f"• Current gaps between expectations and delivered outcomes\n"
                    f"• Competitive pressure requiring faster, smarter responses\n"
                    f"• The cost of inaction is rising year on year\n\n"
                    f"This presentation addresses these challenges head-on."
                ),
            },
            {
                "heading": "Slide 5 – Our Approach",
                "content": (
                    f"How We Address {topic}\n\n"
                    f"Phase 1: Discover — Map the current landscape and identify gaps\n"
                    f"Phase 2: Design — Develop a tailored solution framework\n"
                    f"Phase 3: Deliver — Implement with clear milestones and KPIs\n"
                    f"Phase 4: Sustain — Embed and optimise for long-term impact\n\n"
                    f"Each phase builds on the last to ensure lasting results."
                ),
            },
            {
                "heading": "Slide 6 – Key Findings",
                "content": (
                    f"What the Data Shows\n\n"
                    f"• Organisations investing in {topic.lower()} see 2–3x better performance\n"
                    f"• Early movers in the {domain} domain capture significant market advantage\n"
                    f"• The most common barriers are [resource, alignment, technology]\n"
                    f"• Success rate increases by 40% when a structured approach is used\n\n"
                    f"Source: Industry benchmarks and best practice research."
                ),
            },
            {
                "heading": "Slide 7 – Recommendations",
                "content": (
                    f"What We Recommend\n\n"
                    f"1. Start with a focused pilot on the highest-value area of {topic.lower()}\n"
                    f"2. Build cross-functional buy-in before scaling\n"
                    f"3. Set measurable targets with a 90-day review cycle\n"
                    f"4. Invest in capability building alongside implementation\n"
                    f"5. Capture and share learnings to accelerate future cycles"
                ),
            },
            {
                "heading": "Slide 8 – Next Steps",
                "content": (
                    f"Moving Forward on {topic}\n\n"
                    f"Immediate (This Week):\n"
                    f"  • Confirm stakeholder alignment and sponsorship\n\n"
                    f"Short-Term (Month 1):\n"
                    f"  • Launch discovery phase, assign team\n\n"
                    f"Medium-Term (Months 2–4):\n"
                    f"  • Deliver implementation and first review\n\n"
                    f"Questions & Discussion"
                ),
            },
        ]

    # --- spreadsheet ---

    def _spreadsheet_sections(self, prompt: str) -> list[dict]:
        topic = extract_topic(prompt)
        keywords = extract_keywords(prompt, max_kw=4)
        lower = prompt.lower()

        is_budget   = any(w in lower for w in ["budget", "expense", "cost", "financial", "salary", "invoice"])
        is_tracker  = any(w in lower for w in ["tracker", "tracking", "monitor", "progress", "schedule"])
        is_inventory = any(w in lower for w in ["inventory", "stock", "product", "catalogue", "catalog"])

        if is_budget:
            return self._budget_sections(prompt, topic)
        if is_tracker:
            return self._tracker_sections(prompt, topic)
        if is_inventory:
            return self._inventory_sections(prompt, topic)

        return self._generic_spreadsheet_sections(prompt, topic, keywords)

    def _budget_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Budget Summary",
                "content": (
                    f"Budget for: {topic}\n\n"
                    f"Category         | Budgeted | Actual  | Variance | Notes\n"
                    f"-----------------|----------|---------|----------|-----------\n"
                    f"Personnel        | 45,000   | 43,200  | +1,800   | Under budget\n"
                    f"Technology       | 12,000   | 11,500  | +500     | Software licences\n"
                    f"Operations       | 8,000    | 8,400   | -400     | Utilities over\n"
                    f"Marketing        | 6,000    | 5,200   | +800     | Campaigns paused\n"
                    f"Training         | 3,000    | 2,800   | +200     | On track\n"
                    f"Contingency      | 5,000    | 1,200   | +3,800   | Reserve\n"
                    f"TOTAL            | 79,000   | 72,300  | +6,700   | 8.5% under budget"
                ),
            },
            {
                "heading": "Monthly Breakdown",
                "content": (
                    f"Month     | Revenue  | Expenses | Net       | Cumulative\n"
                    f"----------|----------|----------|-----------|------------\n"
                    f"January   | 18,500   | 12,400   | +6,100    | +6,100\n"
                    f"February  | 19,200   | 13,100   | +6,100    | +12,200\n"
                    f"March     | 21,000   | 14,200   | +6,800    | +19,000\n"
                    f"April     | 22,500   | 13,800   | +8,700    | +27,700\n"
                    f"[Continue for remaining months]"
                ),
            },
            {
                "heading": "Notes & Assumptions",
                "content": (
                    f"Budget prepared for: {topic}\n\n"
                    f"Key assumptions:\n"
                    f"• All figures in USD unless otherwise stated\n"
                    f"• Personnel costs include all on-costs (tax, benefits)\n"
                    f"• Technology costs based on current vendor quotes\n"
                    f"• Revenue projections based on confirmed contracts + 80% of pipeline\n"
                    f"• Contingency reserved for unforeseen operational costs\n\n"
                    f"Next review date: [Date]\n"
                    f"Prepared by: [Name]"
                ),
            },
        ]

    def _tracker_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Project Tracker",
                "content": (
                    f"Tracker for: {topic}\n\n"
                    f"Task / Milestone              | Owner   | Due Date | Status      | Notes\n"
                    f"------------------------------|---------|----------|-------------|----------\n"
                    f"Project Kickoff               | [Name]  | [Date]   | Complete    | ✓\n"
                    f"Requirements Gathering        | [Name]  | [Date]   | Complete    | ✓\n"
                    f"Design & Planning             | [Name]  | [Date]   | In Progress | On track\n"
                    f"Development Phase 1           | [Name]  | [Date]   | In Progress | On track\n"
                    f"Testing & QA                  | [Name]  | [Date]   | Not Started |\n"
                    f"User Acceptance Testing       | [Name]  | [Date]   | Not Started |\n"
                    f"Go-Live                       | [Name]  | [Date]   | Not Started |\n"
                    f"Post-Launch Review            | [Name]  | [Date]   | Not Started |"
                ),
            },
            {
                "heading": "Status Summary",
                "content": (
                    f"Overall Status: In Progress\n\n"
                    f"Completed tasks:   2 of 8 (25%)\n"
                    f"In progress:       2 of 8 (25%)\n"
                    f"Not started:       4 of 8 (50%)\n"
                    f"Blockers:          None currently\n\n"
                    f"Next action: Complete Design & Planning phase by [Date]"
                ),
            },
            {
                "heading": "Notes",
                "content": (
                    f"Tracker for: {topic}\n"
                    f"Last updated: [Date]\n"
                    f"Updated by: [Name]\n\n"
                    f"Key risks:\n"
                    f"• [Risk 1] — mitigation: [action]\n"
                    f"• [Risk 2] — mitigation: [action]"
                ),
            },
        ]

    def _inventory_sections(self, prompt: str, topic: str) -> list[dict]:
        return [
            {
                "heading": "Inventory List",
                "content": (
                    f"Inventory for: {topic}\n\n"
                    f"SKU      | Product Name           | Category    | Qty  | Unit Cost | Total Value | Status\n"
                    f"---------|------------------------|-------------|------|-----------|-------------|--------\n"
                    f"SKU-001  | [Product 1]            | [Category]  | 150  | 25.00     | 3,750.00    | In Stock\n"
                    f"SKU-002  | [Product 2]            | [Category]  | 80   | 45.00     | 3,600.00    | In Stock\n"
                    f"SKU-003  | [Product 3]            | [Category]  | 20   | 120.00    | 2,400.00    | Low Stock\n"
                    f"SKU-004  | [Product 4]            | [Category]  | 0    | 60.00     | 0.00        | Out of Stock\n"
                    f"TOTAL    |                        |             | 250  |           | 9,750.00    |"
                ),
            },
            {
                "heading": "Reorder Report",
                "content": (
                    f"Items requiring action:\n\n"
                    f"SKU-003: Low Stock — reorder point reached. Order qty: 100 units.\n"
                    f"SKU-004: Out of Stock — urgent reorder required. Order qty: 50 units.\n\n"
                    f"Estimated restock cost: [Calculate based on current prices]\n"
                    f"Preferred supplier: [Supplier Name]\n"
                    f"Lead time: [X] business days"
                ),
            },
            {
                "heading": "Notes",
                "content": (
                    f"Inventory report for: {topic}\n"
                    f"Count date: [Date]\n"
                    f"Counted by: [Name]\n\n"
                    f"Discrepancies noted: [None / details here]\n"
                    f"Next stock count: [Date]"
                ),
            },
        ]

    def _generic_spreadsheet_sections(self, prompt: str, topic: str, keywords: list[str]) -> list[dict]:
        return [
            {
                "heading": "Overview",
                "content": f"Data table for: {topic}\nKey fields: {', '.join(keywords) if keywords else 'N/A'}",
            },
            {
                "heading": "Data Table",
                "content": (
                    f"Category         | Description                          | Value   | Status\n"
                    f"-----------------|--------------------------------------|---------|----------\n"
                    f"Row 1            | {keywords[0].title() if keywords else 'Item A'} details | 100     | Active\n"
                    f"Row 2            | {keywords[1].title() if len(keywords) > 1 else 'Item B'} details | 250     | Active\n"
                    f"Row 3            | {keywords[2].title() if len(keywords) > 2 else 'Item C'} details | 180     | Review\n"
                    f"TOTAL            |                                      | 530     |\n"
                ),
            },
            {
                "heading": "Notes",
                "content": (
                    f"Data prepared for: {topic}\n"
                    f"All values are current as of [Date]. Replace with live data before use.\n"
                    f"Last updated by: [Name]"
                ),
            },
        ]

    # ------------------------------------------------------------------

    def _sections_to_text(self, title: str, sections: list[dict]) -> str:
        lines = [title, "=" * len(title), ""]
        for sec in sections:
            lines.append(sec["heading"])
            lines.append("-" * len(sec["heading"]))
            lines.append(sec["content"])
            lines.append("")
        return "\n".join(lines)
