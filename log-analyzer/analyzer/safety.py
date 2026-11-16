"""Input handling for untrusted log files."""
import re

MAX_CHARS = 60_000  # cost and abuse limit for one analysis

_INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(the\s+)?(previous|prior|above)\s+(instructions|prompts?)", re.I),
    re.compile(r"disregard\s+(all\s+)?(the\s+)?(previous|prior|above)", re.I),
    re.compile(r"you\s+are\s+now\b", re.I),
    re.compile(r"system\s+prompt", re.I),
    re.compile(r"report\s+that\s+.{0,40}\b(secure|safe|normal)\b", re.I),
]


def prepare_log(raw: bytes) -> tuple[str, bool]:
    """Decode bytes safely and cap the size. Returns (text, was_truncated)."""
    text = raw.decode("utf-8", errors="replace")
    if len(text) > MAX_CHARS:
        return text[:MAX_CHARS], True
    return text, False


def neutralize_tags(text: str) -> str:
    """Stop a log from closing the <log> data block early and escaping it."""
    return re.sub(r"</?\s*log\s*>", "[log-tag removed]", text, flags=re.I)


def detect_injection_attempt(text: str) -> list[str]:
    """Heuristic only: returns log lines that look like instructions to an AI model.
    It can miss cleverly worded attacks and can flag harmless lines."""
    hits = []
    for line in text.splitlines():
        if any(p.search(line) for p in _INJECTION_PATTERNS):
            hits.append(line.strip()[:200])
    return hits
