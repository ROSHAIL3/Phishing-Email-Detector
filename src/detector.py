from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from src.utils import (
    load_keywords,
    extract_urls,
    find_suspicious_phrases,
    count_all_caps_words,
    count_exclamations,
    safe_sentence_split,
    clamp,
)

@dataclass
class DetectionResult:
    flagged_keywords: List[str]
    suspicious_urls: List[str]
    suspicious_sentences: List[str]
    score: int                 # 0–100
    risk_level: str            # Low / Medium / High
    details: Dict[str, Any]    # extra metrics
    is_phishing: bool

def _score_to_level(score: int) -> str:
    if score >= 70:
        return "High"
    if score >= 40:
        return "Medium"
    return "Low"

def detect_phishing(email_text: str) -> DetectionResult:
    # Load keywords
    keywords = load_keywords("suspicious_keywords.txt")
    email_lower = (email_text or "").lower()

    # Keyword matches across full email
    flagged_keywords = find_suspicious_phrases(email_lower, keywords)

    # URLs and URL suspicion
    urls = extract_urls(email_text or "")
    suspicious_urls = []
    for url in urls:
        u_low = url.lower()
        # Heuristics: keyword in URL, hyphenated brand-like domains, ip-like, punycode
        if any(kw in u_low for kw in keywords) or "xn--" in u_low or "@" in u_low:
            suspicious_urls.append(url)
        elif "-" in u_low and ("login" in u_low or "verify" in u_low or "secure" in u_low):
            suspicious_urls.append(url)

    # Sentence-level suspicion
    suspicious_sentences = []
    for s in safe_sentence_split(email_text or ""):
        s_low = s.lower()
        if any(kw in s_low for kw in keywords):
            suspicious_sentences.append(s.strip())

    # Extra heuristics
    caps_count = count_all_caps_words(email_text or "")
    excls = count_exclamations(email_text or "")

    # Score calculation (heuristic, bounded 0–100)
    score = 0.0
    score += len(flagged_keywords) * 8.0          # keywords weight
    score += len(suspicious_urls) * 18.0          # URLs are strong indicators
    score += len(suspicious_sentences) * 6.0
    score += min(caps_count, 10) * 2.0            # shouting
    score += min(excls, 10) * 1.5                 # urgency/pressure

    score = int(round(clamp(score, 0, 100)))
    risk_level = _score_to_level(score)
    is_phishing = score >= 40 or len(suspicious_urls) > 0

    return DetectionResult(
        flagged_keywords=flagged_keywords,
        suspicious_urls=suspicious_urls,
        suspicious_sentences=suspicious_sentences,
        score=score,
        risk_level=risk_level,
        details={
            "all_caps_words": caps_count,
            "exclamation_marks": excls,
            "url_count": len(urls),
            "keyword_count": len(flagged_keywords),
            "sentence_hits": len(suspicious_sentences),
        },
        is_phishing=is_phishing,
    )
