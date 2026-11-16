from analyzer.analysis import Analysis, Finding
from analyzer.metrics import score


def finding(line, severity="High"):
    return Finding(line=line, severity=severity, category="other", explanation="e", recommendation="r")


LOG = "ERROR Disk usage at 99%\nINFO Health check passed"
EXPECTED = {"must_find": ["Disk usage at 99%", "Pool exhausted"], "must_not_flag": ["Health check passed"]}


def test_score_counts_found_false_alarms_and_ungrounded():
    analysis = Analysis(
        summary="s",
        findings=[
            finding("ERROR Disk usage at 99%"),
            finding("INFO Health check passed", "Critical"),  # false alarm
            finding("CRITICAL invented line"),                 # ungrounded
        ],
    )
    s = score(analysis, LOG, EXPECTED)
    assert s == {"found": 1, "total": 2, "false_alarms": 1, "ungrounded": 1, "n_findings": 3}


def test_low_severity_on_benign_line_is_not_a_false_alarm():
    analysis = Analysis(summary="s", findings=[finding("INFO Health check passed", "Low")])
    assert score(analysis, LOG, EXPECTED)["false_alarms"] == 0
