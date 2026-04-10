"""Style Applier – adds writing-style and tone instructions to prompts."""

from typing import Optional


class StyleApplier:
    """Converts style + tone selections into AI-prompt instructions."""

    STYLE_INSTRUCTIONS: dict[str, str] = {
        "professional": (
            "Write in a polished, business-appropriate style. "
            "Use precise, industry-standard language. Be concise and direct. "
            "Avoid slang, overly casual phrasing, and unnecessary filler."
        ),
        "casual": (
            "Write in a friendly, conversational tone. "
            "Use everyday language and contractions naturally. "
            "Make it feel warm, approachable, and easy to read."
        ),
        "academic": (
            "Write in a formal academic style with sophisticated vocabulary. "
            "Use evidence-based reasoning and scholarly structure. "
            "Cite ideas properly and avoid first-person pronouns where possible."
        ),
        "legal": (
            "Write in precise, unambiguous legal language. "
            "Define key terms on first use and reference them consistently. "
            "Use standard legal drafting conventions: 'shall', 'hereby', 'pursuant to', "
            "'notwithstanding', and numbered clause structure."
        ),
        "creative": (
            "Write in an engaging, imaginative style. "
            "Use vivid imagery, compelling narrative, and varied sentence rhythm. "
            "Be original and make the writing feel alive and distinctive."
        ),
        "persuasive": (
            "Write persuasively to move the reader to action or agreement. "
            "Use strong arguments, emotional appeals, and social proof. "
            "Lead with benefits, address objections, and close with a clear call to action."
        ),
    }

    TONE_INSTRUCTIONS: dict[str, str] = {
        "formal":      "Maintain a formal, respectful register throughout. Address the reader with appropriate deference.",
        "friendly":    "Keep the tone warm and personable. Make the reader feel welcome and at ease.",
        "persuasive":  "Use compelling, benefit-driven language designed to convince and motivate the reader.",
        "informative": "Prioritise clarity and accuracy. Be thorough, factual, and educational.",
        "humorous":    "Use light wit and a playful tone. Keep it professional but let personality shine through.",
    }

    def build_style_block(self, style: str, tone: str) -> str:
        """Return the style + tone instruction block to prepend to an AI prompt."""
        style_instr = self.STYLE_INSTRUCTIONS.get(style, self.STYLE_INSTRUCTIONS["professional"])
        tone_instr  = self.TONE_INSTRUCTIONS.get(tone, self.TONE_INSTRUCTIONS["informative"])
        return (
            f"WRITING STYLE: {style_instr}\n"
            f"TONE: {tone_instr}"
        )

    def apply_to_prompt(self, base_prompt: str, style: str, tone: str) -> str:
        """Inject style/tone instructions into a generation prompt."""
        block = self.build_style_block(style, tone)
        return f"{block}\n\n{base_prompt}"
