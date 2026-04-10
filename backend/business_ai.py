"""Business AI – business plans, strategies, financial models, marketing."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class BusinessAI:
    """Generates business plans, strategies, pitches, and financial documents."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_pitch     = any(w in lower for w in ["pitch", "pitch deck", "investor", "funding", "startup"])
        is_marketing = any(w in lower for w in ["marketing", "campaign", "brand", "customer", "audience"])
        is_financial = any(w in lower for w in ["financial", "revenue", "profit", "budget", "forecast"])
        is_swot      = any(w in lower for w in ["swot", "analysis", "competitive", "market analysis"])

        title = f"Business Plan: {topic}"

        if is_pitch:
            return self._investor_pitch(topic, keywords, kw_str)
        if is_marketing:
            return self._marketing_strategy(topic, keywords, kw_str)
        if is_financial:
            return self._financial_model(topic, keywords, kw_str)
        if is_swot:
            return self._strategic_analysis(topic, keywords, kw_str)
        return self._full_business_plan(topic, keywords, kw_str)

    def _full_business_plan(self, topic, keywords, kw_str) -> dict:
        title = f"Business Plan: {topic}"
        sections = [
            {
                "heading": "Executive Summary",
                "content": (
                    f"Business: {topic}\n"
                    f"Core focus: {kw_str}\n\n"
                    f"{topic} is a business venture designed to address a clear market need "
                    f"in the {kw_str.split(',')[0].strip() if keywords else 'target'} sector. "
                    f"This plan outlines the opportunity, strategy, operations, and financial "
                    f"projections for {topic.lower()}.\n\n"
                    f"Mission: To deliver [value proposition] through {kw_str.split(',')[-1].strip() if keywords else topic.lower()}\n"
                    f"Vision: To become the leading provider of {topic.lower()} in [target market] within 5 years\n"
                    f"Target customers: [Primary customer segment]\n"
                    f"Funding required: [Amount if applicable]\n"
                    f"Expected Year 1 revenue: [Projection]"
                ),
            },
            {
                "heading": "Market Opportunity",
                "content": (
                    f"Market Analysis: {topic}\n\n"
                    f"Total Addressable Market (TAM): The global market for {kw_str.split(',')[0].strip() if keywords else topic.lower()} "
                    f"is estimated at $[X] billion and growing at [Y]% CAGR.\n\n"
                    f"Target Segment: [Specific niche within the broader market]\n"
                    f"  • Size: [Number of potential customers / $ value]\n"
                    f"  • Growth rate: [Annual growth]\n"
                    f"  • Key drivers: {kw_str}\n\n"
                    f"Customer Pain Points:\n"
                    f"  1. Current solutions for {topic.lower()} are too expensive / complex / slow\n"
                    f"  2. Customers lack a single, unified platform for {kw_str.split(',')[0].strip() if keywords else 'this need'}\n"
                    f"  3. Existing providers fail to deliver on [quality / speed / customisation]\n\n"
                    f"Our Solution: {topic} solves these problems by [key differentiator]."
                ),
            },
            {
                "heading": "Products & Services",
                "content": (
                    f"What {topic} Offers:\n\n"
                    f"Core Offering:\n"
                    f"  [{topic} main product/service]: [Description of what it does and who it's for]\n\n"
                    f"Features:\n"
                    + "\n".join(f"  • {kw.title()}: [How this feature delivers value]" for kw in keywords[:4])
                    + f"\n\nPricing Model:\n"
                    f"  • Tier 1 (Basic): $[price]/month — [What's included]\n"
                    f"  • Tier 2 (Professional): $[price]/month — [What's included + extras]\n"
                    f"  • Tier 3 (Enterprise): Custom pricing — Full suite + dedicated support"
                ),
            },
            {
                "heading": "Go-To-Market Strategy",
                "content": (
                    f"How {topic} Reaches Customers:\n\n"
                    f"Phase 1 – Launch (Month 1–3):\n"
                    f"  • Beta launch with [X] pilot customers from {kw_str.split(',')[0].strip() if keywords else 'target segment'}\n"
                    f"  • Collect feedback, refine product, build case studies\n\n"
                    f"Phase 2 – Growth (Month 4–12):\n"
                    f"  • Digital marketing: SEO, content marketing, LinkedIn/social\n"
                    f"  • Partnerships with [complementary businesses in the {kw_str.split(',')[-1].strip() if keywords else 'space'}]\n"
                    f"  • Sales team targeting [customer segment]\n\n"
                    f"Phase 3 – Scale (Year 2+):\n"
                    f"  • Expand to new markets/geographies\n"
                    f"  • Product extensions based on user feedback\n"
                    f"  • Potential channel partnerships and reseller network"
                ),
            },
            {
                "heading": "Financial Projections",
                "content": (
                    f"3-Year Financial Forecast: {topic}\n\n"
                    f"Year 1:\n"
                    f"  Revenue:         $[projection]\n"
                    f"  Gross Margin:    [X]%\n"
                    f"  Operating Costs: $[projection]\n"
                    f"  Net Position:    $[projection] (break-even target: Month [X])\n\n"
                    f"Year 2:\n"
                    f"  Revenue:         $[2x Year 1 target]\n"
                    f"  Gross Margin:    [Improved X]% (scale efficiencies)\n"
                    f"  Net Position:    First profitable year target\n\n"
                    f"Year 3:\n"
                    f"  Revenue:         $[3–4x Year 1 target]\n"
                    f"  EBITDA Margin:   [X]%\n"
                    f"  Valuation basis: [Revenue multiple or comparable company analysis]\n\n"
                    f"Key assumptions: [Customer acquisition cost, churn rate, growth rate for {topic.lower()}]"
                ),
            },
            {
                "heading": "Team & Operations",
                "content": (
                    f"Team Structure for {topic}:\n\n"
                    f"Founding Team:\n"
                    f"  • CEO / Co-founder: [Background in {kw_str.split(',')[0].strip() if keywords else topic.lower()}]\n"
                    f"  • CTO / Co-founder: [Technical background]\n"
                    f"  • [Other key role]: [Background and contribution]\n\n"
                    f"Key Hires (Year 1):\n"
                    f"  • Head of Sales: To lead customer acquisition\n"
                    f"  • [Domain expert]: To strengthen credibility in {kw_str}\n\n"
                    f"Advisory Board:\n"
                    f"  • [Advisor 1]: Industry expert in {topic.lower()}\n"
                    f"  • [Advisor 2]: Investor / go-to-market specialist\n\n"
                    f"Operations:\n"
                    f"  • HQ: [Location]\n"
                    f"  • Legal structure: [Company type, jurisdiction]\n"
                    f"  • Tech stack: [Core platform / tools for delivering {topic.lower()}]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _investor_pitch(self, topic, keywords, kw_str) -> dict:
        title = f"Investor Pitch: {topic}"
        sections = [
            {
                "heading": "The Hook",
                "content": (
                    f"[Opening with a compelling fact or question about {topic.lower()}]\n\n"
                    f"Every year, [X] people/businesses struggle with {kw_str.split(',')[0].strip() if keywords else topic.lower()}. "
                    f"Current solutions are broken. {topic} fixes this."
                ),
            },
            {
                "heading": "Problem & Solution",
                "content": (
                    f"THE PROBLEM:\n"
                    f"{kw_str.split(',')[0].strip().title() if keywords else topic} is a multi-billion-dollar problem. "
                    f"Existing solutions are:\n"
                    f"  • Too expensive for SMEs\n  • Too complex to use\n  • Not built for [target customer]\n\n"
                    f"OUR SOLUTION: {topic}\n"
                    f"  [One-line value proposition]. Customers get [benefit] in [timeframe] "
                    f"without [key pain point]."
                ),
            },
            {
                "heading": "Traction & Market",
                "content": (
                    f"Market size: $[X]B total addressable market\n"
                    f"Our target segment: $[X]M serviceable market\n\n"
                    f"Traction so far:\n"
                    f"  • [X] paying customers / signed LOIs\n"
                    f"  • $[X] ARR / MRR\n"
                    f"  • [X]% month-on-month growth\n"
                    f"  • [Notable customer / partner name if any]"
                ),
            },
            {
                "heading": "Business Model & Ask",
                "content": (
                    f"Revenue model: [SaaS / transaction / licence / service]\n"
                    f"Average deal size: $[X]\n"
                    f"CAC: $[X] | LTV: $[X] | LTV:CAC ratio: [X]:1\n\n"
                    f"THE ASK:\n"
                    f"We are raising $[amount] at a $[valuation] valuation.\n"
                    f"Use of funds: [X]% product, [X]% sales/marketing, [X]% operations\n"
                    f"Runway: [X] months to [key milestone — e.g. profitability / Series A]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _marketing_strategy(self, topic, keywords, kw_str) -> dict:
        title = f"Marketing Strategy: {topic}"
        sections = [
            {
                "heading": "Target Audience",
                "content": (
                    f"Primary audience for {topic}:\n\n"
                    f"  Demographics: [Age, location, profession, income level]\n"
                    f"  Psychographics: [Goals, values, pain points related to {kw_str}]\n"
                    f"  Behaviour: [How they currently solve this problem; where they spend time online]\n\n"
                    f"Customer personas:\n"
                    f"  Persona 1: [Name] — [Brief profile, their need for {topic.lower()}]\n"
                    f"  Persona 2: [Name] — [Brief profile, different use case]"
                ),
            },
            {
                "heading": "Marketing Channels & Tactics",
                "content": (
                    f"Channels for {topic}:\n\n"
                    f"Content Marketing:\n"
                    f"  • Blog posts on {kw_str} — target SEO keywords\n"
                    f"  • Case studies showing customer results\n"
                    f"  • How-to guides and templates\n\n"
                    f"Social Media:\n"
                    f"  • LinkedIn: Professional content for B2B audiences\n"
                    f"  • [Platform 2]: [Content type for the {kw_str.split(',')[0].strip() if keywords else 'target'} audience]\n\n"
                    f"Paid Acquisition:\n"
                    f"  • Google Ads targeting '{kw_str}' search queries\n"
                    f"  • Retargeting campaigns for website visitors\n\n"
                    f"Community & Referral:\n"
                    f"  • Referral programme: [Incentive for existing customers]\n"
                    f"  • Partner with [relevant communities/platforms]"
                ),
            },
            {
                "heading": "Campaign Plan & KPIs",
                "content": (
                    f"Campaign: Launch of {topic}\n\n"
                    f"Phase 1 – Awareness (Month 1–2):\n"
                    f"  Goal: [X] impressions / [X] website visitors\n"
                    f"  Tactic: Launch content series on {kw_str.split(',')[0].strip() if keywords else topic.lower()}\n\n"
                    f"Phase 2 – Consideration (Month 3–4):\n"
                    f"  Goal: [X] email sign-ups / [X] demo requests\n"
                    f"  Tactic: Webinar, comparison guides, free trial offer\n\n"
                    f"Phase 3 – Conversion (Month 5–6):\n"
                    f"  Goal: [X] paying customers\n"
                    f"  Tactic: Limited offer, case studies, sales follow-up\n\n"
                    f"KPIs:\n"
                    f"  • Cost per acquisition (CPA): Target $[X]\n"
                    f"  • Conversion rate: Target [X]%\n"
                    f"  • Return on ad spend (ROAS): Target [X]:1\n"
                    f"  • Brand awareness lift: [Survey measurement]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _financial_model(self, topic, keywords, kw_str) -> dict:
        title = f"Financial Model: {topic}"
        sections = [
            {
                "heading": "Revenue Forecast",
                "content": (
                    f"Revenue projections for {topic}:\n\n"
                    f"Month     | Customers | ARPU ($) | MRR ($)  | ARR ($)\n"
                    f"----------|-----------|----------|----------|----------\n"
                    f"Month 1   |     5     |    200   |   1,000  |   12,000\n"
                    f"Month 3   |    15     |    200   |   3,000  |   36,000\n"
                    f"Month 6   |    40     |    220   |   8,800  |  105,600\n"
                    f"Month 12  |   100     |    250   |  25,000  |  300,000\n"
                    f"Year 2    |   250     |    280   |  70,000  |  840,000\n"
                    f"Year 3    |   500     |    300   | 150,000  | 1,800,000\n\n"
                    f"ARPU = Average Revenue Per User | MRR = Monthly Recurring Revenue"
                ),
            },
            {
                "heading": "Cost Structure",
                "content": (
                    f"Annual Cost Model for {topic}:\n\n"
                    f"Cost Category          | Year 1  | Year 2  | Year 3\n"
                    f"-----------------------|---------|---------|-------\n"
                    f"Personnel              | $180K   | $350K   | $600K\n"
                    f"Technology/Hosting     | $24K    | $48K    | $80K\n"
                    f"Sales & Marketing      | $60K    | $120K   | $200K\n"
                    f"Operations & Legal     | $30K    | $50K    | $80K\n"
                    f"G&A                    | $20K    | $35K    | $55K\n"
                    f"TOTAL OPEX             | $314K   | $603K   | $1,015K\n\n"
                    f"Gross Margin target: 65–75% by Year 2"
                ),
            },
            {
                "heading": "Unit Economics & Break-Even",
                "content": (
                    f"Unit Economics for {topic}:\n\n"
                    f"  Customer Acquisition Cost (CAC):  $[X]\n"
                    f"  Average Revenue Per User (ARPU):  $[X]/month\n"
                    f"  Average Contract Length:          [X] months\n"
                    f"  Lifetime Value (LTV):             $[X]\n"
                    f"  LTV:CAC Ratio:                    [X]:1 (target ≥3:1)\n"
                    f"  Payback period:                   [X] months\n"
                    f"  Monthly churn:                    [X]%\n\n"
                    f"Break-even analysis:\n"
                    f"  Fixed monthly costs: $[X]\n"
                    f"  Revenue needed to break even: $[X]\n"
                    f"  Customers needed: [X] at $[ARPU]\n"
                    f"  Projected break-even month: Month [X]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _strategic_analysis(self, topic, keywords, kw_str) -> dict:
        title = f"Strategic Analysis: {topic}"
        sections = [
            {
                "heading": "SWOT Analysis",
                "content": (
                    f"SWOT Analysis: {topic}\n\n"
                    f"STRENGTHS:\n"
                    f"  • Strong capability in {kw_str.split(',')[0].strip() if keywords else topic.lower()}\n"
                    f"  • Established [customer base / technology / IP]\n"
                    f"  • Experienced team with domain knowledge in {kw_str}\n"
                    f"  • [Unique competitive advantage]\n\n"
                    f"WEAKNESSES:\n"
                    f"  • Limited [resource / market reach / brand awareness] currently\n"
                    f"  • Dependence on [key person / technology / supplier]\n"
                    f"  • [Internal process or capability gap]\n\n"
                    f"OPPORTUNITIES:\n"
                    f"  • Growing demand for {topic.lower()} in [target market]\n"
                    f"  • Regulatory or technology changes favouring our position\n"
                    f"  • Partnership potential with [complementary organisations]\n\n"
                    f"THREATS:\n"
                    f"  • Established competitors in {kw_str.split(',')[-1].strip() if keywords else topic.lower()}\n"
                    f"  • Potential regulatory changes impacting the business model\n"
                    f"  • Economic conditions affecting customer spending"
                ),
            },
            {
                "heading": "Competitive Landscape",
                "content": (
                    f"Competitor Analysis: {topic}\n\n"
                    f"Competitor   | Strengths               | Weaknesses              | Our Advantage\n"
                    f"-------------|-------------------------|-------------------------|---------------\n"
                    f"[Competitor 1] | [Strong brand, scale]  | [High cost, slow]       | Faster, cheaper\n"
                    f"[Competitor 2] | [Feature-rich product] | [Poor UX, no support]   | Better experience\n"
                    f"[Competitor 3] | [Niche expertise]      | [Limited reach]         | Broader market\n\n"
                    f"Our positioning: {topic} wins on [key differentiator — e.g. price, speed, quality, UX]."
                ),
            },
            {
                "heading": "Strategic Recommendations",
                "content": (
                    f"Based on the SWOT for {topic}:\n\n"
                    f"SO Strategies (use Strengths to capture Opportunities):\n"
                    f"  1. Leverage {kw_str.split(',')[0].strip() if keywords else 'core strength'} to capture the growing {kw_str.split(',')[-1].strip() if keywords else 'opportunity'} market\n\n"
                    f"WO Strategies (overcome Weaknesses by pursuing Opportunities):\n"
                    f"  2. Address [key weakness] through investment in [capability/partnership]\n\n"
                    f"ST Strategies (use Strengths to counter Threats):\n"
                    f"  3. Use [competitive advantage] to defend against [threat]\n\n"
                    f"WT Strategies (minimise Weaknesses, avoid Threats):\n"
                    f"  4. [Risk mitigation plan for most critical weakness × threat combination]"
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
