"""Analytics AI – data analysis reports, dashboards, KPI reports, insights."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class AnalyticsAI:
    """Generates data analysis reports, KPI dashboards, and insights documents."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_kpi      = any(w in lower for w in ["kpi", "metric", "performance", "scorecard", "dashboard"])
        is_report   = any(w in lower for w in ["report", "analysis", "insights", "findings"])
        is_forecast = any(w in lower for w in ["forecast", "predict", "projection", "trend"])

        title = f"Analytics Report: {topic}"
        sections = [
            {
                "heading": "Executive Summary",
                "content": (
                    f"Analytics report: {topic}\n"
                    f"Domain: {domain.title()}\n"
                    f"Key metrics: {kw_str}\n\n"
                    f"This report analyses the performance and data landscape for {topic.lower()}. "
                    f"Key findings, trends, and actionable recommendations are provided based on "
                    f"the available data related to {kw_str}."
                ),
            },
            {
                "heading": "KPI Dashboard",
                "content": (
                    f"Key Performance Indicators — {topic}\n\n"
                    f"Metric                        | Current  | Target   | Variance | Trend\n"
                    f"------------------------------|----------|----------|----------|-------\n"
                    + "\n".join(
                        f"{kw.title()[:30]:<30}| {self._mock_val()}    | {self._mock_target()} | {self._mock_var()}  | {self._trend()}"
                        for kw in keywords[:5]
                    )
                    + f"\nOverall Performance Score     | 74%      | 90%      | -16%     | ↑\n\n"
                    f"Status: AMBER — 3 of {len(keywords) or 5} metrics below target. Immediate action required on "
                    f"{kw_str.split(',')[0].strip() if keywords else 'primary metric'}."
                ),
            },
            {
                "heading": "Trend Analysis",
                "content": (
                    f"Trend Analysis: {topic} — Last 6 Periods\n\n"
                    f"Period    | {(kw_str.split(',')[0].strip() if keywords else 'Metric A')[:12]:<14} | "
                    f"{(kw_str.split(',')[1].strip() if len(keywords)>1 else 'Metric B')[:12]:<14} | "
                    f"Overall\n"
                    f"----------|{'-'*16}|{'-'*16}|--------\n"
                    f"Period 1  | 58%            | 61%            | 60%\n"
                    f"Period 2  | 63%            | 65%            | 64%\n"
                    f"Period 3  | 68%            | 66%            | 67%\n"
                    f"Period 4  | 72%            | 70%            | 71%\n"
                    f"Period 5  | 74%            | 73%            | 74%\n"
                    f"Period 6  | 74%            | 76%            | 75%\n\n"
                    f"Trend: {topic.split()[0] if topic.split() else 'Performance'} is on an upward trajectory (+15pp over 6 periods). "
                    f"{kw_str.split(',')[-1].strip().title() if keywords else 'The second metric'} shows slight deceleration — monitor closely."
                ),
            },
            {
                "heading": "Root Cause Analysis",
                "content": (
                    f"Why are metrics for {topic} performing below target?\n\n"
                    f"Contributing factors (in order of impact):\n\n"
                    f"1. {kw_str.split(',')[0].strip().title() if keywords else 'Primary factor'} (HIGH IMPACT)\n"
                    f"   • Current state: Underperforming vs. benchmark by [X]%\n"
                    f"   • Root cause: [Specific operational or strategic issue]\n"
                    f"   • Evidence: [Data point supporting this finding]\n\n"
                    f"2. {kw_str.split(',')[1].strip().title() if len(keywords)>1 else 'Secondary factor'} (MEDIUM IMPACT)\n"
                    f"   • Current state: Variable performance across [segments/regions]\n"
                    f"   • Root cause: [Process inconsistency / resource constraint]\n"
                    f"   • Evidence: [Variance data]\n\n"
                    f"3. External factors (LOW-MEDIUM IMPACT)\n"
                    f"   • Market conditions affecting {topic.lower()}\n"
                    f"   • Seasonal patterns or one-time events"
                ),
            },
            {
                "heading": "Data Insights & Patterns",
                "content": (
                    f"Key Insights from {topic} data:\n\n"
                    f"Insight 1: Correlation found\n"
                    f"  Strong positive correlation (r = 0.78) between {kw_str.split(',')[0].strip() if keywords else 'Variable A'} "
                    f"  and {kw_str.split(',')[-1].strip() if len(keywords)>1 else 'outcome'}. "
                    f"  When {kw_str.split(',')[0].strip() if keywords else 'Variable A'} increases by 10%, "
                    f"  {kw_str.split(',')[-1].strip() if len(keywords)>1 else 'outcome'} increases by ~7.8%.\n\n"
                    f"Insight 2: Segmentation effect\n"
                    f"  The top-performing segment outperforms the bottom by 2.4x on {topic.lower()} metrics. "
                    f"  The gap has widened over the past 3 periods, suggesting structural differences.\n\n"
                    f"Insight 3: Anomaly detected\n"
                    f"  An unusual spike in {kw_str.split(',')[1].strip() if len(keywords)>1 else 'metric'} "
                    f"  during Period 3 warrants investigation. "
                    f"  Possible causes: [data quality issue / genuine outlier / process change]."
                ),
            },
            {
                "heading": "Recommendations & Next Steps",
                "content": (
                    f"To improve {topic} performance:\n\n"
                    f"Immediate Actions (This Week):\n"
                    f"  1. Investigate the {kw_str.split(',')[0].strip() if keywords else 'primary'} metric shortfall — "
                    f"     assign root-cause task force\n"
                    f"  2. Review data quality for anomalies identified in Period 3\n\n"
                    f"Short-Term (Month 1–3):\n"
                    f"  3. Implement targeted improvement plan for bottom-performing segment\n"
                    f"  4. Set weekly KPI review cadence with accountable owners\n"
                    f"  5. Align {kw_str.split(',')[-1].strip() if keywords else 'secondary'} targets "
                    f"     with revised business objectives\n\n"
                    f"Monitoring:\n"
                    f"  • Weekly: KPI scorecard review\n"
                    f"  • Monthly: Full analytics report on {topic.lower()}\n"
                    f"  • Quarterly: Strategic review against [annual targets]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    @staticmethod
    def _mock_val() -> str:
        import random; random.seed(42); return f"{random.randint(60,85)}%"
    @staticmethod
    def _mock_target() -> str:
        import random; random.seed(7); return f"{random.randint(85,95)}%"
    @staticmethod
    def _mock_var() -> str:
        import random; random.seed(13); return f"-{random.randint(5,20)}%"
    @staticmethod
    def _trend() -> str:
        import random; random.seed(99); return random.choice(["↑", "↓", "→"])


def _sections_to_text(title: str, sections: list[dict]) -> str:
    lines = [title, "=" * len(title), ""]
    for sec in sections:
        lines.append(sec["heading"])
        lines.append("-" * len(sec["heading"]))
        lines.append(sec["content"])
        lines.append("")
    return "\n".join(lines)
