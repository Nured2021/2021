"""
Master AI Brain — Intent Detection + Context Mapping + Mode Selection
Routes user prompts to the correct generation engine.
"""
import re

INTENTS = {
    "document": ["document", "report", "essay", "paper", "article", "letter", "memo", "brief", "contract", "proposal", "write", "draft", "docx", "word"],
    "spreadsheet": ["spreadsheet", "excel", "xlsx", "budget", "financial", "accounting", "invoice", "ledger", "balance sheet", "income statement", "table", "data"],
    "presentation": ["presentation", "slides", "pptx", "powerpoint", "pitch", "deck", "slideshow"],
    "education": ["teach", "learn", "course", "professor", "lecture", "exam", "quiz", "syllabus", "curriculum", "study", "semester", "class", "education", "tutor", "explain"],
    "pdf": ["pdf", "export pdf"],
}

MODES = {
    "formal": ["formal", "professional", "business", "corporate", "official"],
    "academic": ["academic", "scholarly", "research", "thesis", "dissertation"],
    "creative": ["creative", "story", "narrative", "fiction", "poetry"],
    "legal": ["legal", "law", "court", "contract", "litigation", "statute"],
    "medical": ["medical", "clinical", "diagnosis", "anatomy", "pathology"],
    "technical": ["technical", "engineering", "code", "algorithm", "system"],
}

PROFESSORS = [
    "math", "physics", "law", "medical", "cs", "engineering", "economics",
    "data_science", "chemistry", "biology", "history", "philosophy",
    "psychology", "literature", "art", "music", "business", "political_science",
    "sociology", "environmental_science",
]


def detect_intent(prompt: str) -> str:
    lower = prompt.lower()
    scores = {}
    for intent, keywords in INTENTS.items():
        scores[intent] = sum(1 for kw in keywords if kw in lower)
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return "document"
    return best


def detect_mode(prompt: str) -> str:
    lower = prompt.lower()
    for mode, keywords in MODES.items():
        if any(kw in lower for kw in keywords):
            return mode
    return "formal"


def detect_professor(prompt: str) -> str:
    lower = prompt.lower()
    professor_keywords = {
        "math": ["math", "calculus", "algebra", "geometry", "statistics", "equation"],
        "physics": ["physics", "mechanics", "quantum", "thermodynamics", "optics"],
        "law": ["law", "legal", "court", "contract", "rights", "litigation"],
        "medical": ["medical", "anatomy", "physiology", "pathology", "clinical"],
        "cs": ["computer science", "programming", "algorithm", "software", "code", "python", "javascript"],
        "engineering": ["engineering", "structural", "mechanical", "civil", "electrical"],
        "economics": ["economics", "macro", "micro", "market", "gdp", "inflation"],
        "data_science": ["data science", "machine learning", "ml", "ai", "neural", "deep learning"],
        "chemistry": ["chemistry", "chemical", "molecule", "reaction", "organic"],
        "biology": ["biology", "cell", "dna", "genetics", "evolution", "ecology"],
        "history": ["history", "historical", "civilization", "war", "empire", "century"],
        "philosophy": ["philosophy", "ethics", "logic", "metaphysics", "epistemology"],
        "psychology": ["psychology", "cognitive", "behavior", "mental", "therapy"],
        "literature": ["literature", "novel", "poetry", "shakespeare", "literary"],
        "art": ["art", "painting", "sculpture", "renaissance", "artistic"],
        "music": ["music", "composition", "symphony", "melody", "harmony"],
        "business": ["business", "management", "strategy", "marketing", "entrepreneurship"],
        "political_science": ["political", "politics", "government", "democracy", "policy"],
        "sociology": ["sociology", "society", "culture", "social", "community"],
        "environmental_science": ["environment", "climate", "ecology", "sustainability", "pollution"],
    }
    best_prof = "cs"
    best_score = 0
    for prof, keywords in professor_keywords.items():
        score = sum(1 for kw in keywords if kw in lower)
        if score > best_score:
            best_score = score
            best_prof = prof
    return best_prof


def detect_file_types(intent: str, prompt: str) -> list:
    lower = prompt.lower()
    types = []
    if intent == "document" or "docx" in lower or "word" in lower:
        types.append("docx")
    if intent == "spreadsheet" or "excel" in lower or "xlsx" in lower:
        types.append("xlsx")
    if intent == "presentation" or "pptx" in lower or "slides" in lower:
        types.append("pptx")
    if "pdf" in lower or intent == "pdf":
        types.append("pdf")
    if not types:
        types = ["pdf", "docx"]
    return types


def route(prompt: str) -> dict:
    intent = detect_intent(prompt)
    mode = detect_mode(prompt)
    file_types = detect_file_types(intent, prompt)
    professor = detect_professor(prompt) if intent == "education" else None

    return {
        "intent": intent,
        "mode": mode,
        "file_types": file_types,
        "professor": professor,
        "prompt": prompt,
    }
