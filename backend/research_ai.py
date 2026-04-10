"""Research AI – literature reviews, research papers, hypotheses, methodologies."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class ResearchAI:
    """Generates research papers, literature reviews, hypotheses, and methodologies."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_lit_review = any(w in lower for w in ["literature review", "lit review", "review of literature"])
        is_abstract   = any(w in lower for w in ["abstract", "paper summary", "research abstract"])
        is_proposal   = any(w in lower for w in ["research proposal", "grant proposal", "phd proposal"])
        is_hypothesis = any(w in lower for w in ["hypothesis", "hypotheses", "research question"])

        title = f"Research: {topic}"

        if is_abstract:
            return self._abstract(topic, domain, keywords, kw_str)
        if is_lit_review:
            return self._literature_review(topic, domain, keywords, kw_str)
        if is_proposal:
            return self._research_proposal(topic, domain, keywords, kw_str)
        if is_hypothesis:
            return self._hypothesis_framework(topic, domain, keywords, kw_str)
        return self._full_research_paper(topic, domain, keywords, kw_str)

    def _full_research_paper(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Research Paper: {topic}"
        sections = [
            {
                "heading": "Abstract",
                "content": (
                    f"This paper examines {topic.lower()} within the context of {domain.title()}. "
                    f"The study investigates the relationship between {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"and {kw_str.split(',')[-1].strip() if len(keywords) > 1 else 'related outcomes'}, "
                    f"drawing on existing literature and applying [methodology] to a sample of "
                    f"[X participants/cases].\n\n"
                    f"Findings indicate that {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"significantly influences [dependent variable], with implications for "
                    f"[theory / practice / policy] in {domain.title()}. "
                    f"The paper concludes with recommendations for future research and practical application.\n\n"
                    f"Keywords: {kw_str}"
                ),
            },
            {
                "heading": "1. Introduction",
                "content": (
                    f"1.1 Background\n"
                    f"The study of {topic.lower()} has gained increasing attention in the {domain.title()} "
                    f"literature over the past decade (Author & Author, 20XX). This is driven by "
                    f"growing recognition of the role that {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"plays in [broader context — social/economic/technological/environmental].\n\n"
                    f"1.2 Research Gap\n"
                    f"Despite extensive research on {kw_str}, few studies have specifically examined "
                    f"[the gap this paper addresses]. Existing literature tends to focus on "
                    f"[what has been studied] but overlooks [what this paper investigates].\n\n"
                    f"1.3 Research Objectives\n"
                    f"This paper aims to:\n"
                    f"  (1) Examine the nature and extent of {topic.lower()} in [context]\n"
                    f"  (2) Analyse the relationship between {kw_str}\n"
                    f"  (3) Propose a framework for understanding and addressing {topic.lower()}\n\n"
                    f"1.4 Significance\n"
                    f"This research contributes to the growing body of knowledge on {topic.lower()} "
                    f"and has practical implications for [professionals / policymakers / educators] "
                    f"in {domain.title()}."
                ),
            },
            {
                "heading": "2. Literature Review",
                "content": (
                    f"2.1 Theoretical Foundations of {topic}\n"
                    f"Seminal work by [Author (Year)] established the foundational understanding of "
                    f"{kw_str.split(',')[0].strip() if keywords else topic.lower()}, proposing that "
                    f"[key theoretical claim]. Subsequent scholars have built on this, extending "
                    f"the framework to include {kw_str.split(',')[-1].strip() if len(keywords) > 1 else 'broader dimensions'} "
                    f"(Author, Year; Author, Year).\n\n"
                    f"2.2 Empirical Evidence\n"
                    f"Empirical studies on {topic.lower()} have yielded mixed findings. "
                    f"[Author (Year)] found that [positive result], while [Author (Year)] reported "
                    f"[contrasting finding] in a sample of [context]. A meta-analysis by [Author (Year)] "
                    f"concluded that the effect of {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"on [outcome] is [magnitude] under [conditions].\n\n"
                    f"2.3 Gaps and Limitations in Existing Research\n"
                    f"The reviewed literature reveals three key gaps:\n"
                    f"  • Lack of longitudinal data on {kw_str}\n"
                    f"  • Over-reliance on WEIRD samples (Western, Educated, Industrialised, Rich, Democratic)\n"
                    f"  • Insufficient examination of {topic.lower()} in [specific under-studied context]"
                ),
            },
            {
                "heading": "3. Methodology",
                "content": (
                    f"3.1 Research Design\n"
                    f"This study adopts a [qualitative / quantitative / mixed-methods] approach "
                    f"to investigate {topic.lower()}. A [case study / survey / experiment / document analysis] "
                    f"design was selected because it is best suited to answering the research questions "
                    f"about {kw_str}.\n\n"
                    f"3.2 Data Collection\n"
                    f"  Sample: [X participants / cases] selected through [sampling method]\n"
                    f"  Instruments: [Survey / interview protocol / observation checklist]\n"
                    f"  Data sources: [Primary data / secondary data / both]\n"
                    f"  Collection period: [Timeframe]\n\n"
                    f"3.3 Analysis\n"
                    f"Data on {kw_str} were analysed using [thematic analysis / regression / "
                    f"content analysis / statistical method]. Validity and reliability were "
                    f"ensured through [triangulation / inter-rater reliability / pilot testing].\n\n"
                    f"3.4 Ethical Considerations\n"
                    f"  • Informed consent obtained from all participants\n"
                    f"  • Anonymity and confidentiality maintained\n"
                    f"  • Ethics approval: [Institution Reference Number]"
                ),
            },
            {
                "heading": "4. Findings & Discussion",
                "content": (
                    f"4.1 Key Findings on {topic}\n\n"
                    f"Finding 1: {kw_str.split(',')[0].strip().title() if keywords else topic} and [Outcome A]\n"
                    f"  The data reveal a [strong/moderate/weak] relationship between "
                    f"  {kw_str.split(',')[0].strip() if keywords else topic.lower()} and [outcome]. "
                    f"  This aligns with the theoretical prediction of [Author, Year].\n\n"
                    f"Finding 2: The role of {kw_str.split(',')[1].strip() if len(keywords)>1 else 'context'}\n"
                    f"  Contextual factors significantly moderate the effect of {topic.lower()}. "
                    f"  Specifically, [factor X] amplifies while [factor Y] attenuates the relationship.\n\n"
                    f"Finding 3: Unexpected results\n"
                    f"  Contrary to our hypothesis, [unexpected finding]. This may be explained by "
                    f"  [alternative explanation] and warrants further investigation.\n\n"
                    f"4.2 Discussion\n"
                    f"These findings extend our theoretical understanding of {topic.lower()} by "
                    f"demonstrating [contribution]. Practically, they suggest that [practitioners/policymakers] "
                    f"should [recommendation based on findings]."
                ),
            },
            {
                "heading": "5. Conclusion & Future Research",
                "content": (
                    f"5.1 Summary\n"
                    f"This paper examined {topic.lower()} and its relationship with {kw_str}. "
                    f"The findings provide empirical support for [main conclusion] and extend "
                    f"the literature in [domain.title()] by [theoretical contribution].\n\n"
                    f"5.2 Practical Implications\n"
                    f"  • Professionals in {domain.title()} should [action 1 based on findings]\n"
                    f"  • Organisations can improve {topic.lower()} outcomes by [recommendation]\n"
                    f"  • Policy should account for [finding] when addressing {kw_str}\n\n"
                    f"5.3 Limitations\n"
                    f"  • Sample size may limit generalisability\n"
                    f"  • Self-report bias in [measurement of {kw_str.split(',')[0].strip() if keywords else topic.lower()}]\n"
                    f"  • Cross-sectional design prevents causal inference\n\n"
                    f"5.4 Future Research Directions\n"
                    f"  • Longitudinal studies tracking {topic.lower()} over time\n"
                    f"  • Cross-cultural comparisons of {kw_str} effects\n"
                    f"  • Experimental designs to establish causality"
                ),
            },
            {
                "heading": "References",
                "content": (
                    f"[Format all references in the required citation style — APA, Harvard, OSCOLA, etc.]\n\n"
                    f"Examples (APA 7th):\n"
                    f"  Author, A. A., & Author, B. B. (Year). Title of article on {topic.lower()}. "
                    f"  Journal Name, volume(issue), page–page. https://doi.org/xxxxx\n\n"
                    f"  Author, C. (Year). Book title: Subtitle. Publisher.\n\n"
                    f"  [Add all sources cited in the body of the paper here in alphabetical order.]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _abstract(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Research Abstract: {topic}"
        sections = [
            {
                "heading": "Abstract",
                "content": (
                    f"Purpose: This study investigates {topic.lower()} in the context of {domain.title()}, "
                    f"focusing specifically on {kw_str}.\n\n"
                    f"Methodology: A [research design] approach was employed, drawing on data from "
                    f"[sample/source]. Data were analysed using [method].\n\n"
                    f"Findings: Results indicate that {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"is significantly associated with [outcome], with a [direction] effect under "
                    f"[conditions]. Three key themes emerged: [Theme 1], [Theme 2], and [Theme 3].\n\n"
                    f"Implications: These findings have important implications for theory and practice "
                    f"in {domain.title()}, suggesting that [practical takeaway] regarding {topic.lower()}.\n\n"
                    f"Originality: This paper makes a novel contribution by [unique contribution — "
                    f"e.g. first study to examine {kw_str.split(',')[-1].strip() if len(keywords)>1 else topic.lower()} "
                    f"in [context]].\n\n"
                    f"Keywords: {kw_str}"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _literature_review(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Literature Review: {topic}"
        sections = [
            {
                "heading": "Introduction to the Review",
                "content": (
                    f"This literature review synthesises research on {topic.lower()} across the "
                    f"{domain.title()} field. The review covers the period [Year–Year] and "
                    f"examines [X] key studies addressing {kw_str}.\n\n"
                    f"Review objectives:\n"
                    f"  (1) Map the theoretical landscape of {topic.lower()}\n"
                    f"  (2) Identify empirical findings on {kw_str}\n"
                    f"  (3) Surface gaps warranting future investigation"
                ),
            },
            {
                "heading": "Theoretical Perspectives",
                "content": (
                    f"Three dominant theoretical frameworks shape scholarly understanding of {topic}:\n\n"
                    f"1. [Theory A] (Author, Year): Proposes that {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"   is best understood as [core claim]. This framework has been widely applied in "
                    f"   {domain.title()} research.\n\n"
                    f"2. [Theory B] (Author, Year): Challenges [Theory A] by emphasising the role of "
                    f"   {kw_str.split(',')[1].strip() if len(keywords)>1 else 'contextual factors'} "
                    f"   in shaping outcomes.\n\n"
                    f"3. [Integrative / Emerging Framework] (Author, Year): Synthesises both perspectives, "
                    f"   arguing that {topic.lower()} is best understood through [integrative lens]."
                ),
            },
            {
                "heading": "Empirical Evidence",
                "content": (
                    f"Empirical studies on {topic}:\n\n"
                    f"Supportive evidence:\n"
                    f"  • [Author (Year)]: [Summary of finding] using [method], n=[X]\n"
                    f"  • [Author (Year)]: [Summary of finding], replicating results in [context]\n\n"
                    f"Contradictory evidence:\n"
                    f"  • [Author (Year)]: Found no significant effect of {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"    on [outcome] in [context], suggesting [explanation]\n\n"
                    f"Meta-analytic evidence:\n"
                    f"  • [Author (Year)] meta-analysis of [X] studies found an overall effect size of "
                    f"    [d/r] = [value] for {topic.lower()}, with significant heterogeneity (I² = [X]%)"
                ),
            },
            {
                "heading": "Research Gaps & Future Directions",
                "content": (
                    f"Despite substantial research, the following gaps persist in the literature on {topic}:\n\n"
                    f"Gap 1: Limited longitudinal research — most studies of {kw_str} are cross-sectional, "
                    f"  preventing conclusions about causation.\n\n"
                    f"Gap 2: Underrepresented contexts — the majority of research was conducted in "
                    f"  [Western/academic/corporate] settings. {topic.lower()} in [other contexts] "
                    f"  remains underexplored.\n\n"
                    f"Gap 3: Measurement inconsistency — different operationalisations of "
                    f"  {kw_str.split(',')[0].strip() if keywords else topic.lower()} make comparisons across "
                    f"  studies difficult. A validated, standardised measure is needed.\n\n"
                    f"Future research should address these gaps by [specific methodological recommendations]."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _research_proposal(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Research Proposal: {topic}"
        sections = [
            {
                "heading": "Research Question & Rationale",
                "content": (
                    f"Primary Research Question:\n"
                    f"  How does {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"  influence {kw_str.split(',')[-1].strip() if len(keywords)>1 else 'outcomes'} "
                    f"  in {domain.title()} contexts?\n\n"
                    f"Sub-questions:\n"
                    f"  RQ1: What are the key determinants of {topic.lower()}?\n"
                    f"  RQ2: How do contextual factors moderate the relationship between {kw_str}?\n"
                    f"  RQ3: What interventions most effectively improve {topic.lower()} outcomes?\n\n"
                    f"Rationale:\n"
                    f"  {topic} represents a critical but under-examined area in {domain.title()} research. "
                    f"  Understanding {kw_str} has direct implications for [theory and/or policy/practice]."
                ),
            },
            {
                "heading": "Proposed Methodology",
                "content": (
                    f"Research design: [Quantitative / Qualitative / Mixed-Methods]\n\n"
                    f"Phase 1 – Literature synthesis (Months 1–2):\n"
                    f"  Conduct a systematic review of existing studies on {topic.lower()} to "
                    f"  identify theoretical frameworks and empirical gaps.\n\n"
                    f"Phase 2 – Data collection (Months 3–6):\n"
                    f"  [Survey / interviews / document analysis] with [N=X participants/cases]\n"
                    f"  Instruments: [validated scales / interview guide / coding framework]\n\n"
                    f"Phase 3 – Analysis (Months 7–9):\n"
                    f"  [Statistical / thematic / comparative] analysis of data on {kw_str}\n\n"
                    f"Phase 4 – Write-up & dissemination (Months 10–12):\n"
                    f"  Research paper + conference presentation + policy brief if applicable"
                ),
            },
            {
                "heading": "Expected Contributions",
                "content": (
                    f"Theoretical contribution:\n"
                    f"  This research will extend [Theory X] by demonstrating how {topic.lower()} "
                    f"  operates under [new conditions not previously studied].\n\n"
                    f"Empirical contribution:\n"
                    f"  The study will provide the first [longitudinal / cross-cultural / experimental] "
                    f"  evidence on {kw_str} in the {domain.title()} context.\n\n"
                    f"Practical contribution:\n"
                    f"  Findings will inform [practitioners / policymakers / educators] on how to "
                    f"  improve {topic.lower()} outcomes in [applied settings]."
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _hypothesis_framework(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Hypothesis Framework: {topic}"
        sections = [
            {
                "heading": "Research Hypotheses",
                "content": (
                    f"Hypotheses for: {topic}\n\n"
                    f"H1 (Main effect): {kw_str.split(',')[0].strip().title() if keywords else topic} "
                    f"   will be positively associated with [dependent variable/outcome].\n\n"
                    f"H2 (Secondary effect): Higher levels of {kw_str.split(',')[1].strip() if len(keywords)>1 else 'the second variable'} "
                    f"   will predict greater [outcome] in {domain.title()} settings.\n\n"
                    f"H3 (Moderation): The relationship between {kw_str.split(',')[0].strip() if keywords else 'X'} "
                    f"   and [outcome] will be moderated by {kw_str.split(',')[2].strip() if len(keywords)>2 else 'context'}.\n\n"
                    f"H4 (Mediation): The effect of {topic.lower()} on [outcome] will be partially "
                    f"   mediated by {kw_str.split(',')[-1].strip() if keywords else 'an intervening variable'}.\n\n"
                    f"Null hypothesis (H0): No significant relationship will be found between "
                    f"{topic.lower()} and the measured outcomes."
                ),
            },
            {
                "heading": "Operationalisation & Measurement",
                "content": (
                    f"Variable definitions for {topic} study:\n\n"
                    + "\n\n".join(
                        f"Variable: {kw.title()}\n"
                        f"  Definition: [Conceptual definition of {kw}]\n"
                        f"  Measure: [How it is measured — scale/questionnaire/observation]\n"
                        f"  Scale: [Likert / interval / categorical]"
                        for kw in keywords[:4]
                    ) if keywords else (
                        f"Variable: {topic}\n"
                        f"  Definition: [Conceptual definition]\n"
                        f"  Measure: [Measurement instrument]\n"
                        f"  Scale: [Scale type]"
                    )
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
