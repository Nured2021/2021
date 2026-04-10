"""Administrative AI – reminders, scheduling, submission tracking."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class AdminAI:
    """Generates schedules, trackers, reminders, and admin documents."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=5)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_schedule  = any(w in lower for w in ["schedule", "timetable", "calendar", "class schedule"])
        is_tracker   = any(w in lower for w in ["tracker", "tracking", "submission", "assignment"])
        is_timeline  = any(w in lower for w in ["timeline", "project plan", "roadmap", "gantt"])
        is_reminder  = any(w in lower for w in ["reminder", "deadline", "alert", "notification"])

        title = f"Administrative Plan: {topic}"
        sections = [
            {
                "heading": "Overview",
                "content": (
                    f"Administrative plan for: {topic}\n"
                    f"Domain: {domain.title()}\n"
                    f"Key areas: {kw_str}\n\n"
                    f"This administrative document provides a structured approach to managing "
                    f"{topic.lower()}, including schedules, deadlines, task assignments, "
                    f"and tracking mechanisms."
                ),
            },
            {
                "heading": "Deadline & Reminder Schedule",
                "content": (
                    f"Reminder Schedule for {topic}:\n\n"
                    f"  4 weeks before:  Initial planning — define scope, assign responsibilities for {topic.lower()}\n"
                    f"  3 weeks before:  First progress check — confirm plans are on track\n"
                    f"  2 weeks before:  Mid-point review — address blockers, adjust timeline if needed\n"
                    f"  1 week before:   Final push — all materials should be near completion\n"
                    f"  3 days before:   Quality check — review, proofread, confirm submission format\n"
                    f"  1 day before:    Final confirmation — everything ready, contingency checked\n"
                    f"  Due date:        Submit / deliver and confirm receipt\n"
                    f"  1 week after:    Review outcomes, document lessons learned for {topic.lower()}"
                ),
            },
            {
                "heading": "Event / Class Schedule",
                "content": (
                    f"Weekly Schedule: {topic}\n\n"
                    f"Monday    09:00–10:30  Session 1 – {kw_str.split(',')[0].strip().title() if keywords else 'Core Topic A'}          [Location TBC]\n"
                    f"Monday    14:00–15:00  Office Hours / Q&A                                [Room / Virtual]\n"
                    f"Tuesday   10:00–11:30  Workshop – Applied {kw_str.split(',')[1].strip().title() if len(keywords)>1 else 'Practice'} [Location TBC]\n"
                    f"Wednesday 09:00–10:30  Session 2 – {kw_str.split(',')[2].strip().title() if len(keywords)>2 else 'Core Topic B'}       [Location TBC]\n"
                    f"Thursday  13:00–14:00  Tutorial / Group Work                            [Location TBC]\n"
                    f"Friday    10:00–11:00  Review & Catch-Up Session                        [Online / Room]\n\n"
                    f"Note: Schedule subject to change. Updated versions will be posted 48 hours in advance."
                ),
            },
            {
                "heading": "Task Assignment Tracker",
                "content": (
                    f"Task Tracker: {topic}\n\n"
                    f"Task                              | Assigned To | Due Date   | Status       | Notes\n"
                    f"----------------------------------|-------------|------------|--------------|------------------\n"
                    + "\n".join(
                        f"{kw.title()[:30]:<34}| [Name]      | [Date]     | Pending      | In queue"
                        for kw in keywords[:5]
                    ) + "\n"
                    f"Final Report / Submission         | [Name]      | [Date]     | Not Started  | \n"
                    f"Post-Event Review                 | [Name]      | [Date]     | Not Started  | \n\n"
                    f"Status Key: Pending | In Progress | Complete | Blocked | On Hold"
                ),
            },
            {
                "heading": "Office Hours & Communications",
                "content": (
                    f"Office Hours for {topic} Team:\n\n"
                    f"  In-person:  [Day] [Time] — [Location]\n"
                    f"  Virtual:    [Day] [Time] — [Video platform link]\n"
                    f"  By appointment: Email [coordinator@organisation.com] 48h in advance\n\n"
                    f"Communication channels:\n"
                    f"  • Primary: Email with subject line '[{topic[:30]}] — [Your Query]'\n"
                    f"  • Urgent matters: [Phone / messaging platform]\n"
                    f"  • Documentation: Shared folder at [link/location]\n\n"
                    f"Response time SLA:\n"
                    f"  • Routine queries: 24 hours on business days\n"
                    f"  • Urgent requests (deadline <48h): 4 hours during business hours"
                ),
            },
            {
                "heading": "File Organisation Guide",
                "content": (
                    f"Recommended Folder Structure for {topic}:\n\n"
                    f"  📁 {topic}/\n"
                    f"  ├── 📁 01_Planning/\n"
                    f"  │   ├── project_plan.docx\n"
                    f"  │   └── stakeholder_list.xlsx\n"
                    f"  ├── 📁 02_Documents/\n"
                    f"  │   ├── {kw_str.split(',')[0].strip().replace(' ','_') if keywords else 'main_document'}.docx\n"
                    f"  │   └── supporting_materials/\n"
                    f"  ├── 📁 03_Data/\n"
                    f"  │   └── tracker.xlsx\n"
                    f"  ├── 📁 04_Correspondence/\n"
                    f"  │   └── emails_and_letters/\n"
                    f"  └── 📁 05_Archive/\n"
                    f"      └── completed_versions/\n\n"
                    f"Naming convention: [YYYY-MM-DD]_[topic]_[version].ext\n"
                    f"Example: 2024-09-01_{topic.lower().replace(' ','_')[:20]}_v1.docx"
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
