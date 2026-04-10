"""Content AI – blog posts, social media, email campaigns, copywriting."""

from __future__ import annotations

from prompt_parser import extract_topic, extract_keywords, detect_domain


class ContentAI:
    """Generates blog posts, social media content, email campaigns, and copy."""

    def generate(self, prompt: str) -> dict:
        topic = extract_topic(prompt)
        domain = detect_domain(prompt)
        keywords = extract_keywords(prompt, max_kw=6)
        kw_str = ", ".join(keywords) if keywords else topic.lower()
        lower = prompt.lower()

        is_blog   = any(w in lower for w in ["blog", "article", "post", "write up"])
        is_social = any(w in lower for w in ["social media", "linkedin", "twitter", "instagram", "facebook", "tweet"])
        is_email  = any(w in lower for w in ["email", "newsletter", "campaign", "subject line"])
        is_copy   = any(w in lower for w in ["ad copy", "advertisement", "landing page", "headline", "tagline"])
        is_press  = any(w in lower for w in ["press release", "announcement", "news release"])

        title = f"Content: {topic}"

        if is_blog:
            return self._blog_post(topic, domain, keywords, kw_str)
        if is_social:
            return self._social_media_pack(topic, domain, keywords, kw_str)
        if is_email:
            return self._email_campaign(topic, domain, keywords, kw_str)
        if is_copy:
            return self._ad_copy(topic, domain, keywords, kw_str)
        if is_press:
            return self._press_release(topic, domain, keywords, kw_str)
        return self._full_content_pack(topic, domain, keywords, kw_str)

    def _full_content_pack(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Content Package: {topic}"
        sections = [
            {
                "heading": "Content Strategy",
                "content": (
                    f"Topic: {topic}\n"
                    f"Domain: {domain.title()}\n"
                    f"Core themes: {kw_str}\n\n"
                    f"Target audience: [Define primary reader/viewer/customer]\n"
                    f"Content goal: [Awareness / Lead generation / Engagement / Conversion]\n"
                    f"Tone of voice: [Professional / Conversational / Authoritative / Friendly]\n\n"
                    f"Key message: [One clear statement that every piece of content about {topic.lower()} should reinforce]\n\n"
                    f"Content mix:\n"
                    f"  • Long-form article (1,500–2,500 words) on {topic.lower()}\n"
                    f"  • 3× social media posts (LinkedIn, Twitter/X, Instagram)\n"
                    f"  • 1× email newsletter\n"
                    f"  • 3× headline variants for A/B testing"
                ),
            },
            {
                "heading": "Blog Article",
                "content": (
                    f"TITLE: {topic}: Everything You Need to Know in 2024\n\n"
                    f"INTRO:\n"
                    f"If you've been wondering about {topic.lower()}, you're not alone. "
                    f"[Compelling statistic or surprising fact about {kw_str.split(',')[0].strip() if keywords else topic.lower()}]. "
                    f"In this article, we break down exactly what {topic.lower()} means, "
                    f"why it matters, and what you can do about it today.\n\n"
                    f"SECTION 1: What is {topic}?\n"
                    f"  [{topic} defined in plain language for your target audience. "
                    f"  Avoid jargon. Use an analogy if helpful.]\n\n"
                    f"SECTION 2: Why {kw_str.split(',')[0].strip().title() if keywords else topic} Matters\n"
                    f"  [3–5 key reasons your audience should care about {topic.lower()}. "
                    f"  Include one data point or case study per reason.]\n\n"
                    f"SECTION 3: How to Get Started with {topic}\n"
                    f"  Step 1: [Actionable first step]\n"
                    f"  Step 2: [Build on step 1]\n"
                    f"  Step 3: [Move to intermediate level]\n\n"
                    f"SECTION 4: Common Mistakes to Avoid\n"
                    f"  [3 pitfalls people encounter with {topic.lower()} and how to avoid them]\n\n"
                    f"CONCLUSION:\n"
                    f"  {topic} doesn't have to be complicated. Start with [simple first action] "
                    f"  and build from there. [Call to action — subscribe / download / contact / try free]\n\n"
                    f"SEO Keywords to include: {kw_str}"
                ),
            },
            {
                "heading": "Social Media Posts",
                "content": (
                    f"LinkedIn Post:\n"
                    f"  {topic} is changing the way [industry/field] works.\n\n"
                    f"  Here are 3 things most people don't know about {kw_str.split(',')[0].strip() if keywords else topic.lower()}:\n\n"
                    f"  1️⃣ [Insight 1 — surprising or counterintuitive]\n"
                    f"  2️⃣ [Insight 2 — practical and actionable]\n"
                    f"  3️⃣ [Insight 3 — forward-looking]\n\n"
                    f"  Which one surprised you most? Comment below 👇\n\n"
                    f"  #{topic.replace(' ','')} #{kw_str.split(',')[0].strip().replace(' ','') if keywords else 'AI'} "
                    f"  #{''.join(w.title() for w in kw_str.split(',')[1].strip().split()) if len(keywords)>1 else 'Innovation'}\n\n"
                    f"Twitter/X Post:\n"
                    f"  🔥 {topic} in 60 seconds:\n\n"
                    f"  • What it is: [one sentence]\n"
                    f"  • Why it matters: [one sentence]\n"
                    f"  • What to do: [one actionable step]\n\n"
                    f"  Save this for later 🔖\n\n"
                    f"Instagram Caption:\n"
                    f"  ✨ Did you know that {topic.lower()} can [key benefit]?\n\n"
                    f"  Swipe through to learn how [kw_str.split(',')[0] if keywords else topic.lower()] "
                    f"  can transform how you [relevant activity].\n\n"
                    f"  Double tap if this helped! ❤️\n"
                    f"  {'#' + ' #'.join(kw.replace(' ','') for kw in keywords[:5]) if keywords else '#EasyAI #Content'}"
                ),
            },
            {
                "heading": "Email Campaign",
                "content": (
                    f"Subject Line Options (A/B test these):\n"
                    f"  Option A: 'The truth about {topic.lower()} (most people get this wrong)'\n"
                    f"  Option B: 'How to [key benefit from {topic.lower()}] in [timeframe]'\n"
                    f"  Option C: '[Number] ways {topic.lower()} can [specific outcome] for you'\n\n"
                    f"EMAIL BODY:\n"
                    f"Hi [First Name],\n\n"
                    f"Quick question: have you been struggling with {topic.lower()}?\n\n"
                    f"You're not alone. [Relatable pain point about {kw_str.split(',')[0].strip() if keywords else topic.lower()}].\n\n"
                    f"That's exactly why we [created / built / wrote] [offer/content].\n\n"
                    f"Here's what you'll [learn / get / achieve]:\n"
                    f"  ✅ [Benefit 1 related to {topic.lower()}]\n"
                    f"  ✅ [Benefit 2]\n"
                    f"  ✅ [Benefit 3]\n\n"
                    f"[CTA BUTTON: 'Get Started Free' / 'Read the Guide' / 'Watch Now']\n\n"
                    f"Talk soon,\n"
                    f"[Your Name]\n"
                    f"[Unsubscribe link]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _blog_post(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Blog Post: {topic}"
        sections = [
            {
                "heading": "Headline & Meta",
                "content": (
                    f"Headline: {topic}: The Complete Guide for {domain.title()} Professionals\n\n"
                    f"Meta description (155 chars): Learn everything about {topic.lower()} — "
                    f"key principles, practical steps, and expert insights on {kw_str[:60]}...\n\n"
                    f"Target keyword: {kw_str.split(',')[0].strip() if keywords else topic.lower()}\n"
                    f"Secondary keywords: {kw_str}\n"
                    f"Estimated word count: 1,800–2,200 words\n"
                    f"Reading time: ~8 minutes"
                ),
            },
            {
                "heading": "Article Body",
                "content": (
                    f"INTRODUCTION\n"
                    f"[Hook: Start with a startling statistic, bold claim, or relatable scenario about {topic.lower()}]\n\n"
                    f"By the end of this guide, you will understand:\n"
                    f"  • What {topic.lower()} really means (beyond the buzzword)\n"
                    f"  • Why {kw_str.split(',')[0].strip() if keywords else topic.lower()} is critical right now\n"
                    f"  • Exactly how to apply it in your {domain} work\n\n"
                    f"SECTION 1: Defining {topic}\n"
                    f"  [Clear, jargon-free definition. Use an analogy. Cite one authoritative source.]\n\n"
                    f"SECTION 2: The Current State of {topic} in {domain.title()}\n"
                    f"  [3 data points or trends. Keep it current. Show the 'why now'.]\n\n"
                    f"SECTION 3: Step-by-Step Guide to {topic}\n"
                    f"  Step 1: [First action — specific and doable]\n"
                    f"  Step 2: [Build on step 1]\n"
                    f"  Step 3: [Intermediate action]\n"
                    f"  Step 4: [More advanced — for those ready to go deeper]\n\n"
                    f"SECTION 4: Real Examples of {topic} in Practice\n"
                    f"  [2–3 case studies or examples. Be specific. Show results.]\n\n"
                    f"SECTION 5: Common Mistakes & How to Avoid Them\n"
                    f"  Mistake 1: [Describe and correct]\n"
                    f"  Mistake 2: [Describe and correct]\n"
                    f"  Mistake 3: [Describe and correct]\n\n"
                    f"CONCLUSION + CTA\n"
                    f"  [Summarise key points. Restate the value. Invite action.]\n"
                    f"  Call to action: [Subscribe / Download / Try free / Contact us]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _social_media_pack(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Social Media Pack: {topic}"
        hashtags = " ".join(f"#{kw.replace(' ','')}" for kw in keywords[:5]) if keywords else f"#{topic.replace(' ','')} #AI"
        sections = [
            {
                "heading": "LinkedIn (5 posts)",
                "content": "\n\n---\n\n".join([
                    f"POST 1 – Thought Leadership\n{topic} is transforming {domain.title()}.\n\nHere's what most people miss:\n[3 insights]\n\nWhat's your experience? 💬\n{hashtags}",
                    f"POST 2 – How-to\nHow to [key benefit from {topic.lower()}] in 5 steps:\n\n1. [Step]\n2. [Step]\n3. [Step]\n4. [Step]\n5. [Step]\n\nSave this. 🔖\n{hashtags}",
                    f"POST 3 – Story\nI used to struggle with {topic.lower()}.\n\nThen I discovered [key insight about {kw_str.split(',')[0].strip() if keywords else topic.lower()}].\n\nHere's what changed:\n[Short story → outcome]\n{hashtags}",
                ]),
            },
            {
                "heading": "Twitter / X (5 posts)",
                "content": "\n\n---\n\n".join([
                    f"🧵 {topic} explained in 5 tweets:\n\n1/ What it is: [one sentence definition]\n2/ Why it matters: [key stat or impact]\n3/ How to start: [actionable tip]\n4/ Common mistake: [what to avoid]\n5/ Bottom line: [takeaway]\n\nFollow for more on {kw_str.split(',')[0].strip() if keywords else topic.lower()}",
                    f"Hot take: Most people approach {topic.lower()} completely wrong.\n\nThe fix? [Simple, counterintuitive insight]\n\nAgree or disagree? 👇",
                    f"Quick tip on {topic.lower()}:\n\n✅ Do: [Good practice]\n❌ Don't: [Common mistake]\n\nSave this tweet. 📌",
                ]),
            },
            {
                "heading": "Instagram Captions",
                "content": (
                    f"Caption 1 (Educational):\n"
                    f"  Did you know {topic.lower()} can [key benefit]? 🤯\n\n"
                    f"  Here's how it works → [brief explanation]\n\n"
                    f"  Follow us for more insights on {kw_str.split(',')[0].strip() if keywords else topic.lower()} 🎯\n"
                    f"  {hashtags}\n\n"
                    f"Caption 2 (Engagement):\n"
                    f"  Agree or disagree? 👇\n\n"
                    f"  '{topic} will be the most important skill in {domain.title()} by 2026.'\n\n"
                    f"  Comment YES or NO below! {hashtags}"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _email_campaign(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Email Campaign: {topic}"
        sections = [
            {
                "heading": "Campaign Overview",
                "content": (
                    f"Campaign: {topic}\n"
                    f"Goal: [Awareness / Nurture / Convert / Re-engage]\n"
                    f"Audience: [Segment description]\n"
                    f"Sequence: 3-email drip campaign\n"
                    f"Timing: Email 1 → Day 0 | Email 2 → Day 3 | Email 3 → Day 7"
                ),
            },
            {
                "heading": "Email 1 – Welcome / Hook",
                "content": (
                    f"Subject: The one thing you need to know about {topic.lower()}\n"
                    f"Preview: Most people get this completely wrong...\n\n"
                    f"Hi [First Name],\n\n"
                    f"Welcome. I'm going to be direct:\n\n"
                    f"{topic} is something that [audience segment] can no longer afford to ignore.\n\n"
                    f"Here's why: [1–2 sentence compelling reason related to {kw_str}]\n\n"
                    f"In the next few days, I'm going to share [3 things] that will change "
                    f"how you think about {topic.lower()}.\n\n"
                    f"Watch for my next email on [Day + Topic preview].\n\n[Sign-off]"
                ),
            },
            {
                "heading": "Email 2 – Value / Education",
                "content": (
                    f"Subject: How [target audience] are using {topic.lower()} to [key benefit]\n\n"
                    f"Hi [First Name],\n\n"
                    f"As promised, here's the insight on {topic.lower()}:\n\n"
                    f"[MAIN CONTENT — teach one specific thing about {kw_str}. Be generous. Provide real value.]\n\n"
                    f"Key takeaway: [One actionable thing they can do today]\n\n"
                    f"Tomorrow I'll share [preview of Email 3 topic].\n\n[Sign-off]"
                ),
            },
            {
                "heading": "Email 3 – CTA / Offer",
                "content": (
                    f"Subject: Ready to take {topic.lower()} to the next level?\n\n"
                    f"Hi [First Name],\n\n"
                    f"Over the past few days, we've covered [quick recap of topics 1 and 2].\n\n"
                    f"Now it's time to take action.\n\n"
                    f"[OFFER / CTA: What do you want them to do? Be specific.]\n\n"
                    f"🔗 [Button: 'Get Started' / 'Book a Call' / 'Download Now' / 'Try Free']\n\n"
                    f"[Urgency or social proof element]\n\n"
                    f"Any questions? Just reply to this email.\n\n[Sign-off]"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _ad_copy(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Ad Copy & Headlines: {topic}"
        sections = [
            {
                "heading": "Headlines (A/B Test These)",
                "content": (
                    f"Headline variants for {topic}:\n\n"
                    f"1. '{topic}: Finally, a Solution That Actually Works'\n"
                    f"2. 'How to [key benefit from {kw_str.split(',')[0].strip() if keywords else topic.lower()}] Without [pain point]'\n"
                    f"3. '[Number] Reasons {domain.title()} Professionals Are Switching to {topic}'\n"
                    f"4. 'Stop [wrong approach]. Start [correct approach] with {topic}'\n"
                    f"5. 'The {topic} Secret That [competitors/others] Don't Want You to Know'"
                ),
            },
            {
                "heading": "Ad Copy Variants",
                "content": (
                    f"Version A (Problem-Solution):\n"
                    f"  HEADLINE: Struggling with {topic.lower()}?\n"
                    f"  BODY: Most {domain} professionals waste [time/money] on [old approach]. "
                    f"  {topic} changes everything. [Key benefit]. [Social proof]. Try free today.\n"
                    f"  CTA: Start Free Trial\n\n"
                    f"Version B (Benefit-led):\n"
                    f"  HEADLINE: [Specific outcome] in [timeframe] with {topic}\n"
                    f"  BODY: Join [X] {domain} professionals already using {topic} to "
                    f"  [achieve specific result]. No [barrier]. No [friction]. Just results.\n"
                    f"  CTA: See How It Works\n\n"
                    f"Version C (Social proof):\n"
                    f"  HEADLINE: '{topic} saved me [X hours / $X / Y headache]' — [Persona]\n"
                    f"  BODY: [Short testimonial] ★★★★★\n"
                    f"  CTA: Read More Stories"
                ),
            },
        ]
        body = _sections_to_text(title, sections)
        return {"title": title, "sections": sections, "body": body}

    def _press_release(self, topic, domain, keywords, kw_str) -> dict:
        title = f"Press Release: {topic}"
        sections = [
            {
                "heading": "Press Release",
                "content": (
                    f"FOR IMMEDIATE RELEASE\n\n"
                    f"[ORGANISATION NAME] ANNOUNCES {topic.upper()}\n\n"
                    f"[City, Date] — [Organisation Name], a leading provider of [products/services] "
                    f"in the {domain.title()} space, today announced {topic.lower()}.\n\n"
                    f"[LEAD PARAGRAPH: Who, What, When, Where, Why in 2–3 sentences about {topic}]\n\n"
                    f"\"[Quote from CEO/spokesperson about {topic.lower()} and why it matters — "
                    f"mention {kw_str.split(',')[0].strip() if keywords else 'the key benefit'}],\" said "
                    f"[Name], [Title] of [Organisation Name]. "
                    f"\"[Second sentence expanding on the significance for the {domain.title()} industry.]\"\n\n"
                    f"KEY FACTS:\n"
                    f"  • {kw_str.split(',')[0].strip().title() if keywords else 'Key point 1'}: [Specific detail]\n"
                    f"  • {kw_str.split(',')[1].strip().title() if len(keywords)>1 else 'Key point 2'}: [Specific detail]\n"
                    f"  • Availability: [Date, geography, pricing if applicable]\n\n"
                    f"ABOUT [ORGANISATION NAME]:\n"
                    f"  [2–3 sentence boilerplate describing the organisation and its mission in {domain.title()}]\n\n"
                    f"MEDIA CONTACT:\n"
                    f"  [Name] | [Email] | [Phone]\n"
                    f"  ###"
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
