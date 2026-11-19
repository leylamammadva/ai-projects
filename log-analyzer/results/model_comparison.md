# Model comparison

4 sample logs, temperature 0, logs redacted before sending.

| Model | Key events found | False alarms | Ungrounded findings | Errors | Mean time per log (s) |
|---|---|---|---|---|---|
| gemini-2.5-flash | 7/11 | 0 | 0 of 10 | 0 | 10.5 |
| gemini-3.5-flash-lite | 8/11 | 0 | 0 of 8 | 0 | 9.6 |

Key events found: expected phrases that appear in at least one finding's quoted line.
False alarms: High or Critical findings that quote a line which is routine and harmless.
Ungrounded: findings whose quoted line does not exist in the log (possible hallucination).
Small sample: indicative only, not statistically significant.
