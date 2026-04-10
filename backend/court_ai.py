"""Court AI – mock trials, legal analysis, contracts, and briefs."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class CourtAI:
    """Generates mock trial scripts, legal analysis, contracts, and legal briefs."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_contract   = any(w in lower for w in ["contract", "agreement", "terms", "mou", "nda"])
        is_brief      = any(w in lower for w in ["brief", "submission", "memorandum of law"])
        is_opening    = any(w in lower for w in ["opening statement", "opening argument"])
        is_closing    = any(w in lower for w in ["closing argument", "closing statement", "summation"])
        is_cross      = any(w in lower for w in ["cross-examination", "cross examination", "deposition"])
        is_motion     = any(w in lower for w in ["motion", "injunction", "application"])
        is_mock_trial = any(w in lower for w in ["mock trial", "mock hearing", "arbitration", "tribunal"])

        title = f"Legal Document: {topic}"

        if is_contract:
            return self._contract(topic, keywords, kw_str)
        if is_brief:
            return self._legal_brief(topic, keywords, kw_str)
        if is_opening:
            return self._opening_statement(topic, keywords, kw_str)
        if is_closing:
            return self._closing_argument(topic, keywords, kw_str)
        if is_cross:
            return self._cross_examination(topic, keywords, kw_str)
        if is_motion:
            return self._motion(topic, keywords, kw_str)

        # Default: full mock trial / case package
        return self._full_case_package(topic, keywords, kw_str, prompt)

    def _full_case_package(self, topic, keywords, kw_str, prompt) -> dict:
        title = f"Legal Case Package: {topic}"
        sections = [
            {
                "heading": "Case Summary",
                "content": (
                    f"Matter: {topic}\n"
                    f"Key issues: {kw_str}\n\n"
                    f"This document package is prepared for educational and simulation purposes. "
                    f"It includes a case summary, arguments for both parties, legal analysis, "
                    f"and a contract/brief template. All names, facts, and references are "
                    f"illustrative unless otherwise specified.\n\n"
                    f"Nature of dispute: {topic}\n"
                    f"Legal domain: {self._detect_legal_domain(kw_str)}\n"
                    f"Applicable standard of proof: Balance of probabilities (civil) / "
                    f"Beyond reasonable doubt (criminal)"
                ),
            },
            {
                "heading": "Opening Statement – Claimant / Prosecution",
                "content": (
                    f"Your Honour, members of the tribunal,\n\n"
                    f"This case concerns {topic.lower()}. The evidence will demonstrate, "
                    f"clearly and conclusively, that {kw_str.split(',')[0].strip() if keywords else 'the respondent'} "
                    f"failed to meet the obligations required under applicable law and agreement.\n\n"
                    f"The claimant will establish:\n"
                    f"  1. That a clear duty existed in relation to {topic.lower()}\n"
                    f"  2. That this duty was breached in the manner described in our submissions\n"
                    f"  3. That the breach directly caused the harm suffered\n"
                    f"  4. That the remedy sought is appropriate and proportionate\n\n"
                    f"We will present documentary evidence, expert testimony, and binding "
                    f"precedents that leave no room for reasonable doubt on the central question "
                    f"of {kw_str.split(',')[-1].strip() if keywords else topic.lower()}."
                ),
            },
            {
                "heading": "Opening Statement – Respondent / Defence",
                "content": (
                    f"Your Honour,\n\n"
                    f"The defence respectfully submits that the claimant's case is unsupported "
                    f"by the evidence. Far from establishing a breach, the facts show that our "
                    f"client acted reasonably, lawfully, and in full compliance with all "
                    f"obligations relevant to {topic.lower()}.\n\n"
                    f"We will demonstrate:\n"
                    f"  1. No duty of the kind alleged existed or was triggered\n"
                    f"  2. Our client's conduct met or exceeded the required standard\n"
                    f"  3. The claimant's losses, if any, are attributable to their own conduct\n"
                    f"  4. The remedy sought is excessive and unsupported in law\n\n"
                    f"The issues of {kw_str} will be fully addressed in our submissions."
                ),
            },
            {
                "heading": "Legal Analysis & Case Law",
                "content": (
                    f"Applicable Legal Framework for {topic}:\n\n"
                    f"Key Principles:\n"
                    f"  • Duty of care / contractual obligation established by [relevant statute or case]\n"
                    f"  • Standard of breach: objective test — what would a reasonable person have done?\n"
                    f"  • Causation: 'but for' test — would the harm have occurred without the breach?\n"
                    f"  • Remoteness: harm must have been a foreseeable consequence\n\n"
                    f"Relevant Authorities:\n"
                    f"  • [Case A] — establishes the principle applicable to {kw_str.split(',')[0].strip() if keywords else 'this matter'}\n"
                    f"  • [Case B] — defines the scope of liability in {self._detect_legal_domain(kw_str)} cases\n"
                    f"  • [Statute/Regulation] — governs the procedural requirements for this claim\n\n"
                    f"Analysis:\n"
                    f"Applying the above to the facts of {topic}, the stronger argument on "
                    f"the central issue appears to favour the party that can demonstrate [key fact]. "
                    f"The outcome will turn on the tribunal's assessment of credibility and "
                    f"the weight given to the documentary evidence on {kw_str.split(',')[-1].strip() if keywords else topic.lower()}."
                ),
            },
            {
                "heading": "Closing Argument – Claimant",
                "content": (
                    f"Your Honour,\n\n"
                    f"The evidence presented in this matter on {topic.lower()} has been clear "
                    f"and compelling. Allow me to summarise the key points:\n\n"
                    f"First, the evidence establishes beyond question that a duty existed. "
                    f"[Reference to specific evidence on {kw_str.split(',')[0].strip() if keywords else 'this point'}].\n\n"
                    f"Second, the respondent's own documents confirm the breach. "
                    f"[Reference to Exhibit X / witness statement].\n\n"
                    f"Third, the causal link between the breach and our client's loss is "
                    f"direct and unchallenged. The respondent has offered no credible "
                    f"alternative explanation.\n\n"
                    f"We respectfully submit that the evidence supports a finding in favour "
                    f"of the claimant and the remedy sought: [specific relief requested]."
                ),
            },
            {
                "heading": "Closing Argument – Respondent",
                "content": (
                    f"Your Honour,\n\n"
                    f"After hearing all of the evidence on {topic.lower()}, it is clear that "
                    f"the claimant has failed to meet the required burden of proof. Let me address "
                    f"the three core deficiencies in their case:\n\n"
                    f"First, no clear duty of the type alleged was ever established. "
                    f"The claimant has relied on [characterisation], but the actual obligation "
                    f"relating to {kw_str.split(',')[0].strip() if keywords else 'the matter'} was different in scope.\n\n"
                    f"Second, our client's actions were objectively reasonable in the circumstances. "
                    f"Any other person in that position, facing those constraints, would have acted identically.\n\n"
                    f"Third, even if some failing existed, the claimant's own conduct was a "
                    f"significant contributing factor.\n\n"
                    f"We respectfully submit that the claim should be dismissed in its entirety."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _contract(self, topic, keywords, kw_str) -> dict:
        title = f"Contract: {topic}"
        sections = [
            {
                "heading": "Parties & Recitals",
                "content": (
                    f"AGREEMENT FOR {topic.upper()}\n\n"
                    f"This Agreement ('Agreement') is made and entered into as of [Date] between:\n\n"
                    f"  PARTY A: [Full Legal Name], a [company/individual] registered/residing at [Address]\n"
                    f"           ('Party A' or 'Service Provider')\n\n"
                    f"  PARTY B: [Full Legal Name], a [company/individual] registered/residing at [Address]\n"
                    f"           ('Party B' or 'Client')\n\n"
                    f"WHEREAS:\n"
                    f"  (a) Party A has expertise and capability in {topic.lower()};\n"
                    f"  (b) Party B desires to engage Party A for services related to {kw_str};\n"
                    f"  (c) The Parties wish to set out their respective rights and obligations."
                ),
            },
            {
                "heading": "1. Scope of Services",
                "content": (
                    f"1.1 Party A shall provide the following in relation to {topic.lower()}:\n"
                    f"    (a) {kw_str.split(',')[0].strip().title() if keywords else 'Core service delivery'} as specified in Schedule 1\n"
                    f"    (b) Regular progress reporting to Party B\n"
                    f"    (c) Cooperation with Party B's reasonable requests\n\n"
                    f"1.2 Party A shall NOT be obligated to:\n"
                    f"    (a) Perform services outside the agreed scope without a written change order\n"
                    f"    (b) Guarantee outcomes that depend on factors outside Party A's control\n\n"
                    f"1.3 Schedule 1 (attached) details the full deliverables for {topic.lower()}."
                ),
            },
            {
                "heading": "2. Payment Terms",
                "content": (
                    f"2.1 In consideration of the services, Party B shall pay Party A:\n"
                    f"    [Amount] in [Currency], payable as follows:\n"
                    f"    (a) [X]% upfront upon signing\n"
                    f"    (b) [Y]% upon completion of milestone 1 ([Date])\n"
                    f"    (c) [Z]% upon final delivery and acceptance\n\n"
                    f"2.2 Invoices are due within 30 days of issue. Late payments accrue interest "
                    f"at [rate]% per annum on the outstanding balance.\n\n"
                    f"2.3 All fees are exclusive of applicable taxes unless otherwise stated."
                ),
            },
            {
                "heading": "3. Intellectual Property",
                "content": (
                    f"3.1 All pre-existing intellectual property of either party remains that "
                    f"party's sole property.\n\n"
                    f"3.2 Work product created specifically for {topic.lower()} under this Agreement "
                    f"shall vest in Party B upon full payment of all fees.\n\n"
                    f"3.3 Party A retains the right to reference the engagement in their portfolio "
                    f"(without disclosing confidential information) unless Party B objects in writing."
                ),
            },
            {
                "heading": "4. Confidentiality & Term",
                "content": (
                    f"4.1 Both parties agree to keep all confidential information relating to "
                    f"{topic.lower()} and each other's operations strictly confidential.\n\n"
                    f"4.2 This Agreement commences on [Start Date] and terminates on [End Date] "
                    f"or upon completion of all deliverables, whichever is earlier.\n\n"
                    f"4.3 Either party may terminate on [30] days' written notice. Fees earned "
                    f"to the date of termination remain payable."
                ),
            },
            {
                "heading": "5. Governing Law & Execution",
                "content": (
                    f"5.1 This Agreement is governed by the laws of [Jurisdiction].\n\n"
                    f"5.2 Any disputes shall be resolved first by good-faith negotiation, "
                    f"then by [arbitration / courts of Jurisdiction].\n\n"
                    f"IN WITNESS WHEREOF, the parties have executed this Agreement:\n\n"
                    f"PARTY A:                            PARTY B:\n"
                    f"Signature: ___________________      Signature: ___________________\n"
                    f"Name:      ___________________      Name:      ___________________\n"
                    f"Title:     ___________________      Title:     ___________________\n"
                    f"Date:      ___________________      Date:      ___________________"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _legal_brief(self, topic, keywords, kw_str) -> dict:
        title = f"Legal Brief: {topic}"
        sections = [
            {
                "heading": "Header & Introduction",
                "content": (
                    f"IN THE MATTER OF: {topic.upper()}\n\n"
                    f"LEGAL BRIEF / MEMORANDUM OF LAW\n\n"
                    f"Submitted by: [Counsel's Name]\n"
                    f"On behalf of: [Party Name]\n"
                    f"Date: [Date]\n\n"
                    f"I. INTRODUCTION\n"
                    f"This brief addresses the legal issues arising from {topic.lower()}. "
                    f"The central questions for the tribunal are: whether {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"gives rise to actionable liability, and what remedy, if any, is appropriate."
                ),
            },
            {
                "heading": "Statement of Facts",
                "content": (
                    f"II. STATEMENT OF FACTS\n\n"
                    f"The following facts are relevant to the determination of {topic.lower()}:\n\n"
                    f"1. [Background fact establishing the relationship between the parties]\n"
                    f"2. [Key event / act / omission that forms the basis of the claim]\n"
                    f"3. [Evidence of harm or breach — reference to Exhibit A / document]\n"
                    f"4. [Timeline of relevant events in chronological order]\n"
                    f"5. [Any prior communications, agreements, or warnings relevant to {kw_str}]"
                ),
            },
            {
                "heading": "Legal Argument",
                "content": (
                    f"III. LEGAL ARGUMENT\n\n"
                    f"A. The Law on {topic}\n"
                    f"   The applicable legal standard requires [cite principle]. In [Case Authority], "
                    f"   the court held that [relevant holding]. This principle applies directly "
                    f"   to the facts of the present matter.\n\n"
                    f"B. Application to the Facts\n"
                    f"   Applying the test to {topic.lower()}: first, [element 1 satisfied because...]; "
                    f"   second, [element 2 satisfied because...]; third, [causation/damages].\n\n"
                    f"C. Distinguishing Contrary Authorities\n"
                    f"   The respondent may rely on [Case X]. However, that case is distinguishable "
                    f"   on its facts because [specific distinction relating to {kw_str}]."
                ),
            },
            {
                "heading": "Relief Sought",
                "content": (
                    f"IV. RELIEF SOUGHT\n\n"
                    f"For the reasons above, [Party Name] respectfully requests that the tribunal:\n\n"
                    f"  1. Find that the respondent breached their obligations with respect to {topic.lower()}\n"
                    f"  2. Award damages in the amount of [$ / appropriate remedy]\n"
                    f"  3. Issue [injunctive relief / specific performance / declaration] as appropriate\n"
                    f"  4. Award costs of these proceedings to the claimant\n\n"
                    f"  [Alternatively, if this is a respondent's brief:]\n"
                    f"  1. Dismiss the claim in its entirety\n"
                    f"  2. Award costs to the respondent"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _opening_statement(self, topic, keywords, kw_str) -> dict:
        title = f"Opening Statement: {topic}"
        sections = [
            {
                "heading": "Opening Statement",
                "content": (
                    f"Your Honour / Members of the Tribunal,\n\n"
                    f"This case is about {topic.lower()}.\n\n"
                    f"Let me tell you what the evidence will show:\n\n"
                    f"First, you will hear that {kw_str.split(',')[0].strip().title() if keywords else 'the claimant'} "
                    f"had a clear and enforceable right — and that right was violated.\n\n"
                    f"Second, you will see documents — [Exhibit A through Exhibit X] — that "
                    f"establish, without question, that the events of {topic.lower()} occurred "
                    f"exactly as we describe.\n\n"
                    f"Third, you will hear from witnesses who were there. Their testimony will "
                    f"confirm the facts as set out in our submissions.\n\n"
                    f"By the end of this hearing, the evidence will compel only one conclusion: "
                    f"that our client is entitled to the relief sought.\n\n"
                    f"Thank you."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _closing_argument(self, topic, keywords, kw_str) -> dict:
        title = f"Closing Argument: {topic}"
        sections = [
            {
                "heading": "Closing Argument",
                "content": (
                    f"Your Honour,\n\n"
                    f"We have now heard all of the evidence on {topic.lower()}. "
                    f"I want to take a few moments to summarise what that evidence established.\n\n"
                    f"THE FACTS ARE NOT IN DISPUTE:\n"
                    f"  • {kw_str.split(',')[0].strip().title() if keywords else 'The obligation'} existed. "
                    f"    This is confirmed by [Document / Witness].\n"
                    f"  • The {kw_str.split(',')[1].strip() if len(keywords) > 1 else 'breach'} occurred. "
                    f"    The respondent's own records prove it.\n"
                    f"  • The harm followed directly and foreseeably.\n\n"
                    f"THE LAW IS CLEAR:\n"
                    f"  [Case authority] establishes that when [condition], liability follows. "
                    f"  Every element of that test is met on these facts.\n\n"
                    f"THE REMEDY IS PROPORTIONATE:\n"
                    f"  We seek [specific relief]. This is not excessive — it is exactly what "
                    f"  the law requires to make our client whole.\n\n"
                    f"Your Honour, we respectfully submit that a finding in favour of our client "
                    f"is the only conclusion supported by the evidence. Thank you."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _cross_examination(self, topic, keywords, kw_str) -> dict:
        title = f"Cross-Examination Questions: {topic}"
        sections = [
            {
                "heading": "Cross-Examination Plan",
                "content": (
                    f"Witness: [Witness Name / Role]\n"
                    f"Topic: {topic}\n"
                    f"Objective: Establish [key fact] / Undermine credibility on {kw_str}\n\n"
                    f"Core strategy: Lead with closed questions. Control the witness. "
                    f"Never ask a question you don't know the answer to."
                ),
            },
            {
                "heading": "Suggested Questions",
                "content": (
                    f"Establishing the Baseline:\n"
                    f"  Q: You were present when [event related to {topic.lower()}] occurred?\n"
                    f"  Q: At that time, you were responsible for {kw_str.split(',')[0].strip() if keywords else topic.lower()}?\n"
                    f"  Q: You had access to the relevant documents?\n\n"
                    f"Challenging the Evidence:\n"
                    f"  Q: You told us [X], but [Exhibit A] says something different — correct?\n"
                    f"  Q: Isn't it true that you did not follow the required procedure on [date]?\n"
                    f"  Q: You have no written evidence to support that claim, do you?\n\n"
                    f"Closing the Cross:\n"
                    f"  Q: So to summarise — you acknowledge that [key concession]?\n"
                    f"  Q: And despite knowing that, you chose to [act/omit] — is that right?\n"
                    f"  Q: Thank you, no further questions."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _motion(self, topic, keywords, kw_str) -> dict:
        title = f"Motion / Application: {topic}"
        sections = [
            {
                "heading": "Motion Header",
                "content": (
                    f"IN THE MATTER OF: {topic.upper()}\n\n"
                    f"NOTICE OF MOTION / APPLICATION\n\n"
                    f"Moving Party: [Party Name]\n"
                    f"Responding Party: [Party Name]\n"
                    f"Date of Hearing: [Date]\n"
                    f"Relief Sought: [Specific order requested]"
                ),
            },
            {
                "heading": "Grounds for the Motion",
                "content": (
                    f"The moving party seeks relief on the following grounds:\n\n"
                    f"1. [Primary legal basis — statute or rule authorising the relief]\n"
                    f"2. [Factual basis — what happened that justifies this motion in {topic.lower()}]\n"
                    f"3. [Urgency / irreparable harm if applicable]\n\n"
                    f"The law on {topic.lower()} clearly supports the relief sought. "
                    f"Specifically, [cite authority] establishes that [relevant principle]."
                ),
            },
            {
                "heading": "Supporting Argument & Relief",
                "content": (
                    f"ARGUMENT:\n"
                    f"The test for the relief sought requires:\n"
                    f"  (a) A strong prima facie case — MET: [brief explanation]\n"
                    f"  (b) Irreparable harm without the order — MET: [brief explanation]\n"
                    f"  (c) Balance of convenience favours the order — MET: [brief explanation]\n\n"
                    f"ORDER SOUGHT:\n"
                    f"The moving party respectfully requests an order:\n"
                    f"  1. [Specific order 1]\n"
                    f"  2. [Specific order 2 if needed]\n"
                    f"  3. Costs of this motion in the cause"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    @staticmethod
    def _detect_legal_domain(kw_str: str) -> str:
        lower = kw_str.lower()
        if any(w in lower for w in ["employment", "labour", "labor", "wrongful", "dismissal", "union"]):
            return "Employment Law"
        if any(w in lower for w in ["contract", "breach", "agreement", "commercial"]):
            return "Contract Law"
        if any(w in lower for w in ["criminal", "fraud", "theft", "assault"]):
            return "Criminal Law"
        if any(w in lower for w in ["property", "land", "lease", "tenant"]):
            return "Property Law"
        if any(w in lower for w in ["family", "divorce", "custody", "matrimonial"]):
            return "Family Law"
        return "Civil Litigation"


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
