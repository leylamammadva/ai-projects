# AI Log Analyzer

![tests](https://github.com/leylamammadva/ai-projects/actions/workflows/log-analyzer-tests.yml/badge.svg)

A Streamlit app that uses Google Gemini through LangChain to analyze log files and return a structured, evidence-based triage: a summary plus findings with severity, category, the exact log line, an explanation and a recommendation.

**Tech:** Python, LangChain, Gemini API, Streamlit, Pydantic, pytest, GitHub Actions

## Demo

**Brute-force SSH log:** repeated failed logins from one IP are grouped into a single finding, while the successful root login and the creation of the `backdoor` user are reported separately as Critical.

![Brute-force SSH analysis](../screenshots/demo4.png)

**Prompt injection test:** a log line that tries to instruct the model ("IGNORE ALL PREVIOUS INSTRUCTIONS...") is reported as a suspicious event instead of being followed.

![Prompt injection test](../screenshots/demo1.png)

The app also shows the exact text that is sent to the AI after redaction, so the user can check what leaves the machine.

## What makes it security-aware
- **Privacy:** IP addresses and e-mails are pseudonymized before the log is sent to the API (`PRIVATE_IP_1`, `PUBLIC_IP_1`, `EMAIL_1`). Tokens are restored locally for display only. An expander in the UI shows the redacted text that was sent.
- **Prompt injection:** the log is untrusted input. It is wrapped in `<log>` tags, the system prompt says to treat it as data, tag-escape attempts are neutralized, and lines that look like instructions to an AI model trigger a warning.
- **Hallucination check:** every finding must quote a log line. Lines that do not exist in the log are flagged in the UI.
- **Structured output:** the model must return a typed object (Pydantic schema), not free text.
- **Less noise:** the prompt asks the model to report repeated identical events (for example many failed logins from one IP) as one finding with the count and time range, and to keep different kinds of events separate.
- **Limits:** file size cap and safe decoding of invalid bytes.

## Results
Manual runs with `gemini-2.5-flash` (temperature 0) on the synthetic sample logs. Each log was run once, so these results are indicative, not statistically significant.

| Log | Observation |
|-----|-------------|
| `brute_force_ssh.log` | 5 failed logins (02:11:03 to 02:11:12) were grouped into one finding. The successful root login and the creation of the `backdoor` user were reported separately as Critical. |
| `injection.log` | The embedded instruction was not followed. The model reported it as a High suspicious event and still reported the real Critical unauthorized access attempt. |

Observed weaknesses:
- Before the grouping rule was added to the prompt, the same failed logins produced four near-identical Medium findings.
- Severity is not stable between runs: the failed SSH logins were rated Medium in one run and High in another.
- A single failed login (`invalid credentials`) was rated Medium, which may be too high.
- Resistance to prompt injection rests mainly on code-level controls (`<log>` delimiting, tag neutralization, heuristic detection). The model's behavior is an additional layer, not a guarantee.

## Model comparison
Run `python -m analyzer.compare` to test models on the sample logs against hand-written expectations (`data/expected.json`).

<!-- PASTE THE REAL TABLE FROM results/model_comparison.md HERE AFTER YOU RUN IT -->

## Limitations
- Redaction does not detect usernames, hostnames or secrets in free text.
- The injection warning is a heuristic and can miss cleverly worded attacks.
- Four synthetic sample logs only: results are indicative, not statistically significant.
- LLM output can vary between runs, including severity ratings. Findings must be verified by an analyst.
- Not for production use.

See [docs/assessment.md](docs/assessment.md) for a short applicability assessment for a financial services SOC.

## Setup
```bash
git clone https://github.com/leylamammadva/ai-projects.git
cd ai-projects/log-analyzer
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # add your own key, never commit .env
streamlit run app.py
```

## Tests
```bash
pip install -r requirements-dev.txt
pytest -q
```
The tests run offline: the LLM is replaced by a fake, so no API key is needed.

## Structure
```
log-analyzer/
  app.py               Streamlit UI
  analyzer/
    analysis.py        prompt, structured output, grounding check
    redact.py          pseudonymization before sending
    safety.py          size limit, tag neutralization, injection heuristic
    metrics.py         scoring against expectations
    compare.py         model comparison script
  sample_logs/         synthetic logs
  data/expected.json   hand-written expectations
  tests/               offline unit tests
  docs/assessment.md   applicability assessment
```