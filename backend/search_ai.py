"""Global AI Search — keyword + TF-IDF semantic search across all documents."""

from __future__ import annotations

import math
import re
from collections import Counter


class SearchAI:
    """In-memory full-text + TF-IDF search engine for documents."""

    def __init__(self) -> None:
        self._docs: list[dict] = []   # list of {id, title, module, prompt, body, sections, user_id, ...}
        self._idf_cache: dict[str, float] = {}

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def add_document(self, doc: dict) -> None:
        """Index a generated document."""
        full_text = " ".join([
            doc.get("title", ""),
            doc.get("prompt", ""),
            doc.get("body", ""),
        ]).lower()
        doc["_full_text"] = full_text
        doc["_tokens"]    = self._tokenise(full_text)
        self._docs.append(doc)
        self._idf_cache = {}   # invalidate cache

    def search(self, query: str, user_id: str | None = None,
               module: str | None = None, limit: int = 20) -> list[dict]:
        """Search indexed documents. Returns ranked list of result dicts."""
        if not query.strip():
            return []

        # Filter by user and module
        pool = [
            d for d in self._docs
            if (not user_id or d.get("user_id") == user_id) and
               (not module  or d.get("module") == module)
        ]
        if not pool:
            return []

        q_tokens = self._tokenise(query.lower())
        if not q_tokens:
            return []

        idf = self._compute_idf(pool)
        results = []
        for doc in pool:
            score = self._tfidf_score(doc["_tokens"], q_tokens, idf)
            if score > 0:
                results.append((score, doc))

        results.sort(key=lambda x: x[0], reverse=True)
        return [
            {
                "id":        d.get("id", ""),
                "title":     d.get("title", ""),
                "module":    d.get("module", ""),
                "prompt":    (d.get("prompt") or "")[:150],
                "preview":   (d.get("body") or "")[:200],
                "score":     round(sc, 4),
                "pdf_url":   d.get("pdf_url"),
                "docx_url":  d.get("docx_url"),
                "pptx_url":  d.get("pptx_url"),
                "xlsx_url":  d.get("xlsx_url"),
                "created_at": d.get("created_at"),
            }
            for sc, d in results[:limit]
        ]

    def suggestions(self, prefix: str, limit: int = 8) -> list[str]:
        """Return autocomplete suggestions from indexed document titles."""
        prefix = prefix.strip().lower()
        if len(prefix) < 2:
            return []
        seen: set[str] = set()
        out: list[str] = []
        for doc in reversed(self._docs):
            title = doc.get("title", "")
            if prefix in title.lower() and title not in seen:
                seen.add(title)
                out.append(title)
                if len(out) >= limit:
                    break
        return out

    def size(self) -> int:
        return len(self._docs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    _STOP = {
        "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "from", "as", "is", "it", "its", "that", "this",
        "are", "was", "were", "be", "been", "have", "has", "had", "do", "does",
        "did", "will", "would", "could", "should", "may", "might", "shall",
        "not", "no", "nor", "so", "yet", "both", "either", "neither",
    }

    def _tokenise(self, text: str) -> list[str]:
        words = re.findall(r"[a-z]+", text.lower())
        return [w for w in words if w not in self._STOP and len(w) > 2]

    def _compute_idf(self, pool: list[dict]) -> dict[str, float]:
        """Compute inverse document frequency for current pool."""
        N = len(pool)
        if not N:
            return {}
        df: Counter = Counter()
        for doc in pool:
            df.update(set(doc["_tokens"]))
        return {term: math.log(N / (cnt + 1)) + 1.0 for term, cnt in df.items()}

    def _tfidf_score(self, doc_tokens: list[str], q_tokens: list[str],
                     idf: dict[str, float]) -> float:
        if not doc_tokens:
            return 0.0
        tf_doc: Counter = Counter(doc_tokens)
        score = 0.0
        for qt in q_tokens:
            tf  = tf_doc.get(qt, 0) / len(doc_tokens)
            _idf = idf.get(qt, 0.0)
            score += tf * _idf
        return score


# Module-level singleton — shared across the whole server process
_global_search = SearchAI()


def get_search_engine() -> SearchAI:
    return _global_search
