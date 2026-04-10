"""Administrative AI – reminders, scheduling, submission tracking."""

from __future__ import annotations


class AdminAI:
    """Generates administrative documents: schedules, reminders, trackers."""

    def generate(self, prompt: str) -> dict:
        title = f"Administrative Plan: {prompt[:65]}"
        sections = [
            {
                "heading": "Request Summary",
                "content": (
                    f"Administrative task: {prompt}\n\n"
                    "The following plan addresses the organisational and scheduling "
                    "requirements outlined in the request."
                ),
            },
            {
                "heading": "Assignment Reminders",
                "content": (
                    "Reminder Schedule:\n"
                    "• 2 weeks before due date: Initial reminder – confirm understanding "
                    "of requirements and check progress.\n"
                    "• 1 week before due date: Progress check – ensure draft or outline "
                    "is complete.\n"
                    "• 3 days before due date: Final reminder – address any remaining "
                    "questions, confirm submission format.\n"
                    "• Day of submission: Confirmation – verify successful upload / delivery."
                ),
            },
            {
                "heading": "Class / Event Schedule",
                "content": (
                    "Weekly Schedule Template:\n"
                    "Monday    09:00–10:30  Lecture – Core Topic A  [Room TBC]\n"
                    "Monday    14:00–15:00  Office Hours            [Room TBC]\n"
                    "Wednesday 09:00–10:30  Seminar – Applied Topic [Room TBC]\n"
                    "Thursday  13:00–14:00  Tutorial / Workshop     [Room TBC]\n"
                    "Friday    10:00–11:00  Review Session          [Online / Room TBC]"
                ),
            },
            {
                "heading": "Office Hours Schedule",
                "content": (
                    "Office Hours:\n"
                    "• Monday 14:00–15:00 (in person, Room [TBC])\n"
                    "• Wednesday 15:00–16:00 (virtual, Zoom link [TBC])\n"
                    "• By appointment: email [instructor@institution.edu] at least "
                    "48 hours in advance.\n\n"
                    "Students are encouraged to prepare specific questions in advance "
                    "to make the most of office hour sessions."
                ),
            },
            {
                "heading": "Submission Tracker",
                "content": (
                    "Assignment Tracker:\n\n"
                    "Assignment          | Due Date   | Status     | Notes\n"
                    "--------------------|------------|------------|------------------\n"
                    "Assignment 1        | [Date]     | Pending    | \n"
                    "Midterm Essay       | [Date]     | Pending    | \n"
                    "Group Project       | [Date]     | In Progress| Group formed ✓\n"
                    "Final Examination   | [Date]     | Scheduled  | Room [TBC]\n"
                    "Portfolio Submission| [Date]     | Pending    | \n\n"
                    "Update this tracker after each submission is confirmed."
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
