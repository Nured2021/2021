"""Citation AI – generates academic and legal citations in APA, MLA, Chicago, Harvard, Bluebook, OSCOLA."""

from __future__ import annotations

import re
from prompt_parser import extract_keywords


# Common legal case patterns
_CASE_PATTERNS = [
    (r"([A-Z][A-Za-z\s&']+)\s+v\.?\s+([A-Z][A-Za-z\s&']+)\s+\((\d{4})\)",  "case_with_year"),
    (r"([A-Z][A-Za-z\s&']+)\s+v\.?\s+([A-Z][A-Za-z\s&']+)",                 "case_no_year"),
]


class CitationAI:
    """Generates citations in multiple formats from prompts or raw case/author info."""

    def generate(self, prompt: str) -> dict:
        """Generate a full citation reference guide tailored to the prompt."""
        kws = extract_keywords(prompt, max_kw=6)
        topic = kws[0].title() if kws else "the topic"

        # Detect format preference
        fmt = self._detect_format(prompt)
        cases = self._extract_cases(prompt)

        sections = [
            {
                "heading": f"Citation Format Selected: {fmt.upper()}",
                "content": self._format_overview(fmt, prompt),
            },
            {
                "heading": "Citation Examples for Your Topic",
                "content": self._build_topic_citations(prompt, topic, fmt),
            },
            {
                "heading": "Legal Case Citations" if cases else "Academic Source Citations",
                "content": self._build_case_citations(cases, fmt) if cases
                           else self._build_academic_citations(topic, fmt),
            },
            {
                "heading": "Table of Authorities / Bibliography Template",
                "content": self._build_bibliography(topic, fmt),
            },
            {
                "heading": "Cite-As-You-Type Quick Reference",
                "content": self._quick_reference(fmt),
            },
        ]
        title = f"Citation Guide: {fmt.upper()} Format — {topic.title()}"
        body  = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body, "module": "citation"}

    # ── Format detection ─────────────────────────────────────────────

    def _detect_format(self, prompt: str) -> str:
        p = prompt.lower()
        if any(w in p for w in ["bluebook", "blue book", "law review", "us legal"]):    return "bluebook"
        if any(w in p for w in ["oscola", "uk legal", "oxford legal", "english law"]):  return "oscola"
        if any(w in p for w in ["canadian", "mcgill", "canada"]):                       return "canadian"
        if any(w in p for w in ["mla", "humanities", "literature"]):                    return "mla"
        if any(w in p for w in ["chicago", "turabian", "history", "humanities"]):       return "chicago"
        if any(w in p for w in ["harvard"]):                                            return "harvard"
        if any(w in p for w in ["legal", "court", "arbitration", "statute", "case"]):  return "oscola"
        return "apa"  # default academic

    # ── Case extraction ──────────────────────────────────────────────

    def _extract_cases(self, prompt: str) -> list[dict]:
        cases = []
        for pat, pat_type in _CASE_PATTERNS:
            for m in re.finditer(pat, prompt):
                if pat_type == "case_with_year":
                    cases.append({"party1": m.group(1).strip(), "party2": m.group(2).strip(), "year": m.group(3)})
                else:
                    cases.append({"party1": m.group(1).strip(), "party2": m.group(2).strip(), "year": None})
        return cases

    # ── Format overview ──────────────────────────────────────────────

    def _format_overview(self, fmt: str, prompt: str) -> str:
        overviews = {
            "apa": (
                "APA (American Psychological Association) — 7th Edition\n\n"
                "Used in: Social sciences, psychology, education, nursing, business\n"
                "In-text citation: (Author, Year) or (Author, Year, p. XX)\n"
                "Reference list: Alphabetical by first author surname\n\n"
                "Key rules:\n"
                "  • Author surname, Initial(s). (Year). Title in sentence case. Publisher.\n"
                "  • DOI or URL always included when available\n"
                "  • No full stop after DOI/URL\n"
                "  • Et al. used for 3+ authors after first citation"
            ),
            "mla": (
                "MLA (Modern Language Association) — 9th Edition\n\n"
                "Used in: Literature, arts, humanities, language studies\n"
                "In-text citation: (Author Page) — e.g., (Smith 47)\n"
                "Works Cited page at end of document\n\n"
                "Key rules:\n"
                "  • Author. 'Article Title.' Book/Journal Title, vol., no., Year, pp. XX–XX.\n"
                "  • Titles of short works in quotation marks; long works in italics\n"
                "  • DOI preferred over URL\n"
                "  • Works Cited: double-spaced, hanging indent"
            ),
            "chicago": (
                "Chicago Manual of Style — 17th Edition\n\n"
                "Used in: History, social sciences, some humanities\n"
                "Two systems: Notes-Bibliography (humanities) or Author-Date (sciences)\n"
                "Footnotes: ¹ Firstname Lastname, Title (City: Publisher, Year), page.\n\n"
                "Key rules:\n"
                "  • Bibliography: Lastname, Firstname. Title. City: Publisher, Year.\n"
                "  • Ibid. for repeated consecutive citations\n"
                "  • Journal: Author, 'Title,' Journal Name vol. no. (Year): pages."
            ),
            "harvard": (
                "Harvard Referencing Style\n\n"
                "Used in: UK/Australian universities, many disciplines\n"
                "In-text: (Author Year) or (Author Year, p. XX)\n"
                "Reference list: Alphabetical by author\n\n"
                "Key rules:\n"
                "  • Author, Initial(s) Year, Title, Publisher, Place.\n"
                "  • Year immediately after author name\n"
                "  • Journal: Author Year, 'Article title', Journal, vol., no., pp. XX–XX.\n"
                "  • Viewed [date] <URL> for online sources"
            ),
            "bluebook": (
                "The Bluebook: A Uniform System of Citation — 21st Edition\n\n"
                "Used in: US legal writing, law reviews, courts\n"
                "Case format: Party v. Party, Volume Reporter Page (Court Year).\n"
                "Statute format: Name of Act § Section (Year).\n\n"
                "Key rules:\n"
                "  • Party names italicised in law review articles; underlined in court documents\n"
                "  • Short form after first full citation: Party, Volume Reporter at Page.\n"
                "  • Use SMALL CAPS for book/journal titles in law review footnotes\n"
                "  • Id. for immediately preceding authority"
            ),
            "oscola": (
                "OSCOLA (Oxford University Standard for the Citation of Legal Authorities) — 4th Edition\n\n"
                "Used in: UK legal writing, English law journals\n"
                "Case format: Party v Party [Year] Court Report\n"
                "Statute: Title of Act Year, s Section Number\n\n"
                "Key rules:\n"
                "  • No full stops after abbreviated reporter names\n"
                "  • Pinpoint: [Year] Court Report, para/p XX\n"
                "  • Ibid for identical consecutive citations\n"
                "  • Secondary sources in footnotes only"
            ),
            "canadian": (
                "Canadian Guide to Uniform Legal Citation (McGill Guide) — 9th Edition\n\n"
                "Used in: Canadian legal writing, law reviews\n"
                "Case format: Party v Party, Year Court Report (Court)\n\n"
                "Key rules:\n"
                "  • Neutral citations preferred when available: Party v Party, Year Court para\n"
                "  • Statute: Title, RS/SBC Year, c Chapter, s Section\n"
                "  • Ibid + pinpoint for consecutive same-source citations"
            ),
        }
        return overviews.get(fmt, overviews["apa"])

    # ── Topic-specific citations ─────────────────────────────────────

    def _build_topic_citations(self, prompt: str, topic: str, fmt: str) -> str:
        year = "2023"
        author1 = "Smith, J."
        author2 = "Johnson, A. & Williams, B."
        journal = f"Journal of {topic.title()} Studies"
        if fmt == "apa":
            return (
                f"JOURNAL ARTICLE:\n"
                f"  {author1} ({year}). Advances in {topic}: A systematic review. "
                f"{journal}, 15(3), 45–67. https://doi.org/10.xxxx/example\n\n"
                f"BOOK:\n"
                f"  {author2} ({year}). {topic.title()}: Theory and Practice (3rd ed.). Academic Press.\n\n"
                f"WEBSITE:\n"
                f"  Organisation Name. ({year}, January 15). {topic.title()} guidelines. "
                f"Retrieved from https://example.org/{topic.lower().replace(' ', '-')}\n\n"
                f"IN-TEXT EXAMPLES:\n"
                f"  (Smith, {year})  |  (Smith, {year}, p. 47)  |  Smith ({year}) found that…"
            )
        elif fmt == "mla":
            return (
                f"JOURNAL ARTICLE:\n"
                f"  Smith, John. 'Advances in {topic.title()}: A Systematic Review.' "
                f"{journal}, vol. 15, no. 3, {year}, pp. 45–67.\n\n"
                f"BOOK:\n"
                f"  Johnson, Alice, and Brian Williams. {topic.title()}: Theory and Practice. "
                f"3rd ed., Academic Press, {year}.\n\n"
                f"WEBSITE:\n"
                f"  Organisation Name. '{topic.title()} Guidelines.' Example.org, 15 Jan. {year}, "
                f"www.example.org/{topic.lower().replace(' ', '-')}. Accessed 1 Mar. {year}.\n\n"
                f"IN-TEXT EXAMPLES:\n"
                f"  (Smith 47)  |  Smith argues that…  |  (Johnson and Williams 112)"
            )
        elif fmt in ("bluebook", "oscola", "canadian"):
            return self._build_legal_topic_citations(topic, fmt, year)
        else:  # harvard, chicago
            return (
                f"JOURNAL ARTICLE:\n"
                f"  Smith, J {year}, 'Advances in {topic.title()}', {journal}, "
                f"vol. 15, no. 3, pp. 45–67.\n\n"
                f"BOOK:\n"
                f"  Johnson, A & Williams, B {year}, {topic.title()}: Theory and Practice, "
                f"3rd edn, Academic Press.\n\n"
                f"IN-TEXT:\n"
                f"  (Smith {year})  |  Smith ({year}, p. 47) found that…"
            )

    def _build_legal_topic_citations(self, topic: str, fmt: str, year: str) -> str:
        if fmt == "bluebook":
            return (
                f"CASE (Bluebook):\n"
                f"  Smith v. Johnson, 234 F.3d 456, 461 (9th Cir. {year}).\n"
                f"  Short form: Smith, 234 F.3d at 462.\n\n"
                f"STATUTE:\n"
                f"  Employment Standards Act, RS O 1990, c E.14, s 5 (Can).\n\n"
                f"SECONDARY SOURCE:\n"
                f"  JAMES A. SMITH, {topic.upper()}: LAW AND PRACTICE 47 (3d ed. {year}).\n\n"
                f"IN-TEXT: Smith, 234 F.3d at 461  |  Id. at 462  |  Id."
            )
        elif fmt == "oscola":
            return (
                f"CASE (OSCOLA):\n"
                f"  Smith v Johnson [{year}] EWCA Civ 123\n"
                f"  Pinpoint: Smith v Johnson [{year}] EWCA Civ 123, [47]\n\n"
                f"STATUTE:\n"
                f"  Employment Rights Act 1996, s 98\n\n"
                f"SECONDARY SOURCE (OSCOLA footnote):\n"
                f"  James Smith, {topic.title()}: Law and Practice (3rd edn, OUP {year}) 47\n\n"
                f"  Ibid 52  (consecutive citation to same source, different page)"
            )
        else:  # canadian
            return (
                f"CASE (McGill/Canadian):\n"
                f"  Smith v Johnson, {year} ONCA 123\n"
                f"  Pinpoint: Smith v Johnson, {year} ONCA 123 at para 47\n\n"
                f"STATUTE:\n"
                f"  Employment Standards Act, 2000, SO 2000, c 41, s 5\n\n"
                f"SECONDARY SOURCE:\n"
                f"  James Smith, {topic.title()}: Law and Practice, 3rd ed (Toronto: LexisNexis, {year}) at 47"
            )

    # ── Case-specific citations ──────────────────────────────────────

    def _build_case_citations(self, cases: list[dict], fmt: str) -> str:
        if not cases:
            return "No specific case citations detected in prompt."
        lines = [f"DETECTED CASES ({fmt.upper()} FORMAT):\n"]
        for c in cases[:5]:
            p1, p2, yr = c["party1"], c["party2"], c.get("year") or "Year"
            if fmt in ("oscola",):
                lines.append(f"  {p1} v {p2} [{yr}] [Reporter] [Page]")
                lines.append(f"  Pinpoint: {p1} v {p2} [{yr}] [Reporter] [Page], para XX\n")
            elif fmt == "bluebook":
                lines.append(f"  {p1} v. {p2}, [Vol] [Reporter] [Page] ([Court] {yr}).")
                lines.append(f"  Short form: {p1}, [Vol] [Reporter] at [Pinpoint].\n")
            elif fmt == "canadian":
                lines.append(f"  {p1} v {p2}, {yr} [Court] [Para/Page]")
                lines.append(f"  Neutral citation preferred where available.\n")
            else:
                lines.append(f"  {p1} v. {p2} ({yr}). [Court/Reporter].")
        return "\n".join(lines)

    # ── Academic citations ───────────────────────────────────────────

    def _build_academic_citations(self, topic: str, fmt: str) -> str:
        return (
            f"SAMPLE ACADEMIC SOURCES FOR '{topic.upper()}':\n\n"
            f"Peer-reviewed journal articles, books, and reports related to {topic} would appear here.\n\n"
            f"TIP — How to cite sources as you write:\n"
            f"  1. Note the author surname, year, and page number as you read\n"
            f"  2. Insert in-text citation immediately after the quoted/paraphrased text\n"
            f"  3. Add full reference to your reference list / bibliography at the end\n"
            f"  4. Use a reference manager (Zotero, Mendeley, or EndNote) for large projects\n\n"
            f"CITATION MANAGER FORMATS: {fmt.upper()} format is supported by all major citation managers.\n"
            f"  Export your library as {fmt.upper()} → paste directly into your document."
        )

    # ── Bibliography template ────────────────────────────────────────

    def _build_bibliography(self, topic: str, fmt: str) -> str:
        if fmt in ("bluebook", "oscola", "canadian"):
            return (
                f"TABLE OF AUTHORITIES TEMPLATE ({fmt.upper()}):\n\n"
                f"CASES\n"
                f"  [Case Name] . . . . . . . . . . . . . . . . . . . [Page]\n"
                f"  [Case Name] . . . . . . . . . . . . . . . . . . . [Page]\n\n"
                f"STATUTES\n"
                f"  [Statute Name] . . . . . . . . . . . . . . . . . . [Page]\n\n"
                f"SECONDARY SOURCES\n"
                f"  [Author, Title] . . . . . . . . . . . . . . . . . . [Page]\n\n"
                f"Note: List all authorities in alphabetical order within each category.\n"
                f"Include page numbers of every reference in the document."
            )
        label = {"apa": "REFERENCE LIST", "mla": "WORKS CITED",
                 "chicago": "BIBLIOGRAPHY", "harvard": "REFERENCE LIST"}.get(fmt, "BIBLIOGRAPHY")
        return (
            f"{label} TEMPLATE ({fmt.upper()}):\n\n"
            f"[Arrange entries alphabetically by first author surname]\n\n"
            f"[Author A]\n  [Full citation in {fmt.upper()} format]\n\n"
            f"[Author B]\n  [Full citation in {fmt.upper()} format]\n\n"
            f"FORMATTING RULES:\n"
            f"  • Hanging indent: first line flush left, subsequent lines indented 0.5 inch\n"
            f"  • Double-spaced throughout\n"
            f"  • No blank lines between entries (unless journal style requires)\n"
            f"  • Page title centred at top: '{label}'"
        )

    # ── Quick reference ──────────────────────────────────────────────

    def _quick_reference(self, fmt: str) -> str:
        refs = {
            "apa": (
                "APA QUICK REFERENCE:\n"
                "  Article: Author, A. (Year). Title. Journal, vol(no), pp. DOI\n"
                "  Book:    Author, A. (Year). Title. Publisher.\n"
                "  Chapter: Author, A. (Year). Chapter title. In Ed. Name (Ed.), Book title (pp. XX-XX). Publisher.\n"
                "  Web:     Author, A. (Year, Month Day). Title. URL\n"
                "  In-text: (Author, Year)  |  (Author, Year, p. X)  |  Author (Year)"
            ),
            "mla": (
                "MLA QUICK REFERENCE:\n"
                "  Article: Author. 'Title.' Journal, vol., no., Year, pp.\n"
                "  Book:    Author. Title. Publisher, Year.\n"
                "  Web:     Author. 'Title.' Website, Date, URL. Accessed Date.\n"
                "  In-text: (Author Page)  |  (Author)  if no page"
            ),
            "oscola": (
                "OSCOLA QUICK REFERENCE:\n"
                "  Case:    Party v Party [Year] Court Reporter\n"
                "  Act:     Title Year, s X\n"
                "  Book:    Author, Title (edn, Publisher Year) page\n"
                "  Article: Author, 'Title' (Year) Vol Journal Page\n"
                "  Same:    Ibid  |  Ibid page  |  (n X) page  for earlier footnote"
            ),
            "bluebook": (
                "BLUEBOOK QUICK REFERENCE:\n"
                "  Case:    Party v. Party, Vol Rep Page (Court Year).\n"
                "  Statute: Name § Sec (Year).\n"
                "  Book:    AUTHOR, TITLE page (Year).\n"
                "  Article: Author, Title, Vol J. Page (Year).\n"
                "  Same:    Id.  |  Id. at page  |  supra note X, at page"
            ),
        }
        return refs.get(fmt, refs["apa"])


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines += [sec["heading"], "-" * len(sec["heading"]), sec["content"], ""]
    return "\n".join(lines)
