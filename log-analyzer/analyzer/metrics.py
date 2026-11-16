"""Scoring of one model run against hand-written expectations (pure functions, easy to test)."""
from analyzer.analysis import Analysis, is_grounded

HIGH = {"Critical", "High"}


def score(analysis: Analysis, log_text: str, expected: dict) -> dict:
    lines = [f.line.lower() for f in analysis.findings]
    must_find = expected.get("must_find", [])
    found = sum(any(p.lower() in line for line in lines) for p in must_find)

    benign = [p.lower() for p in expected.get("must_not_flag", [])]
    false_alarms = sum(
        1 for f in analysis.findings
        if f.severity in HIGH and any(p in f.line.lower() for p in benign)
    )
    ungrounded = sum(1 for f in analysis.findings if not is_grounded(f.line, log_text))
    return {
        "found": found,
        "total": len(must_find),
        "false_alarms": false_alarms,
        "ungrounded": ungrounded,
        "n_findings": len(analysis.findings),
    }
