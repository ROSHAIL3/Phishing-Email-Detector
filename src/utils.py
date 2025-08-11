import json
import os
import re
from pathlib import Path
from datetime import datetime

# ---------- Paths ----------
def project_root() -> Path:
    # src/utils.py -> project root is two levels up from this file
    return Path(__file__).resolve().parents[1]

def data_path(*parts) -> Path:
    return project_root() / "data" / Path(*parts)

def assets_path(*parts) -> Path:
    return project_root() / "assets" / Path(*parts)

# ---------- Keyword loading ----------
def load_keywords(filepath: str | Path) -> list[str]:
    p = Path(filepath)
    if not p.is_absolute():
        p = data_path(filepath)
    if not p.exists():
        return []
    with p.open("r", encoding="utf-8") as f:
        return [line.strip().lower() for line in f if line.strip()]

# ---------- URL extraction ----------
_URL_REGEX = re.compile(r"""
    \b
    (?:
      https?://
    )
    [^\s<>'"(){}]+
""", re.IGNORECASE | re.VERBOSE)

def extract_urls(text: str) -> list[str]:
    return _URL_REGEX.findall(text or "")

# ---------- Simple heuristics ----------
_WORD_REGEX = re.compile(r"[A-Za-z]+")

def count_all_caps_words(text: str) -> int:
    words = _WORD_REGEX.findall(text)
    return sum(1 for w in words if len(w) > 2 and w.isupper())

def count_exclamations(text: str) -> int:
    return text.count("!")

def find_suspicious_phrases(text: str, phrases: list[str]) -> list[str]:
    t = (text or "").lower()
    found = []
    for p in phrases:
        if p and p in t:
            found.append(p)
    return list(dict.fromkeys(found))  # de-duplicate preserve order

# ---------- NLTK setup and safe sentence split ----------
def safe_sentence_split(text: str) -> list[str]:
    """
    Try NLTK sentence tokenizer; if unavailable, fall back to a simple regex split.
    """
    try:
        import nltk  # local import
        try:
            # Try using punkt; download quietly if missing
            from nltk.tokenize import sent_tokenize  # noqa
            # A quick smoke test; if it raises, download
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            nltk.download("punkt", quiet=True)
        from nltk.tokenize import sent_tokenize
        return sent_tokenize(text or "")
    except Exception:
        # Fallback: split on ., !, ? keeping basic sentence ends
        return re.split(r"(?<=[.!?])\s+", text or "")

# ---------- History persistence ----------
def append_history(entry: dict) -> None:
    """
    Append a scan entry to data/history.json. Creates the file if needed.
    """
    hp = data_path("history.json")
    hp.parent.mkdir(parents=True, exist_ok=True)
    history = []
    if hp.exists():
        try:
            history = json.loads(hp.read_text(encoding="utf-8"))
        except Exception:
            history = []
    entry_with_time = {"timestamp": datetime.now().isoformat(timespec="seconds"), **entry}
    history.append(entry_with_time)
    hp.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

# ---------- Utility ----------
def clamp(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, val))
