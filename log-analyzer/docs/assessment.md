# Applicability assessment: AI-assisted log triage for a financial services SOC

Status: draft based on a small prototype and four synthetic logs.

## Use case
A security operations team receives large volumes of logs (authentication, web, system). An LLM can give analysts a first-pass summary and a prioritized list of events with quoted evidence, so analysts spend less time reading routine lines.

## Expected benefits
- Faster first read of an incident log.
- Consistent structure (severity, category, evidence line, next step).
- Evidence quoting makes each finding checkable against the source.

## What the prototype showed
- Model comparison on 4 synthetic logs (final prompt, one run per log): `gemini-2.5-flash` matched 7 of 11 expected key events and `gemini-3.5-flash-lite` 8 of 11, both with no false alarms and no ungrounded findings. An earlier run gave 8 of 11 for `gemini-2.5-flash`, so the difference between the models is within run-to-run variation. Indicative only.
- Manual runs with `gemini-2.5-flash` on four synthetic logs showed no false alarm on the operational log, but in one web-attack case the model quoted a less informative line, and severity ratings varied between runs.
- On the log with an embedded instruction, the model did not follow it and reported it as a suspicious event in my test runs (single runs; the main defence is the code-level controls, not the model).

## Risks
| Risk | Why it matters | Control in the prototype | Remaining gap |
|---|---|---|---|
| Data leakage | Logs contain IPs, e-mails and possibly secrets and are sent to a third-party API | IP and e-mail pseudonymization before sending | Usernames, hostnames and free-text secrets are not detected; contract and data-processing terms (GDPR) must be checked |
| Prompt injection | Attackers can write text into logs that tries to steer the model | Log wrapped in data tags, rule to treat it as data, tag-escape neutralization, heuristic warning | Heuristic detection can miss attacks; no guarantee against injection |
| Hallucination | The model may report events that are not in the log | Each finding must quote a log line; lines not found in the log are flagged | A real quoted line can still be misinterpreted |
| Missed events | A threat that the model overlooks gives false reassurance | Analyst review remains required | Not yet measured reliably; evaluation on a larger labelled set is pending |
| Cost and abuse | Very large uploads cost money | Size limit per analysis | No per-user rate limit |

## Recommendation
Suitable as an analyst assistant for triage of non-sensitive or redacted logs, not as an automated decision maker. Severity ratings varied between runs, so every finding needs analyst review. Next step: pilot on historical redacted logs with analyst feedback before any production use.

## Next steps
1. Evaluate on a larger, analyst-labelled set of logs.
2. Add detection of usernames and hostnames to redaction, or run a model inside the organization's own environment.
3. Add tool use, for example a lookup of an IP's earlier failed logins, to move from a single prompt to an agent workflow.
4. Add monitoring of model output quality over time.