"""Compare models on the same sample logs.

Run from the log-analyzer folder:   python -m analyzer.compare
Set COMPARE_MODELS (comma separated) in .env, for example:
COMPARE_MODELS=gemini-2.5-flash,gemini-2.5-flash-lite
Use model names that exist for your API key.
"""
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

from analyzer.analysis import analyze
from analyzer.metrics import score
from analyzer.redact import redact

load_dotenv()


def main() -> None:
    from langchain_google_genai import ChatGoogleGenerativeAI

    models = [m.strip() for m in os.getenv("COMPARE_MODELS", "gemini-2.5-flash").split(",") if m.strip()]
    delay = float(os.getenv("COMPARE_DELAY", "3"))
    expected = json.loads(Path("data/expected.json").read_text(encoding="utf-8"))

    rows = []
    for model in models:
        llm = ChatGoogleGenerativeAI(model=model, google_api_key=os.getenv("GOOGLE_API_KEY"), temperature=0)
        agg = {"found": 0, "total": 0, "false_alarms": 0, "ungrounded": 0, "n_findings": 0, "errors": 0, "secs": []}
        for name, exp in expected.items():
            text, _ = redact(Path("sample_logs", name).read_text(encoding="utf-8"))
            start = time.time()
            try:
                result = analyze(text, llm)
                s = score(result, text, exp)
                for k in ("found", "total", "false_alarms", "ungrounded", "n_findings"):
                    agg[k] += s[k]
            except Exception as exc:  # rate limit, invalid output, network
                agg["errors"] += 1
                agg["total"] += len(exp.get("must_find", []))
                print(f"{model} / {name}: {type(exc).__name__}: {exc}")
            agg["secs"].append(time.time() - start)
            time.sleep(delay)
        mean = sum(agg["secs"]) / len(agg["secs"])
        rows.append((model, agg, mean))

    lines = [
        "# Model comparison",
        "",
        f"{len(expected)} sample logs, temperature 0, logs redacted before sending.",
        "",
        "| Model | Key events found | False alarms | Ungrounded findings | Errors | Mean time per log (s) |",
        "|---|---|---|---|---|---|",
    ]
    for model, a, mean in rows:
        lines.append(
            f"| {model} | {a['found']}/{a['total']} | {a['false_alarms']} | "
            f"{a['ungrounded']} of {a['n_findings']} | {a['errors']} | {mean:.1f} |"
        )
    lines += [
        "",
        "Key events found: expected phrases that appear in at least one finding's quoted line.",
        "False alarms: High or Critical findings that quote a line which is routine and harmless.",
        "Ungrounded: findings whose quoted line does not exist in the log (possible hallucination).",
        "Small sample: indicative only, not statistically significant.",
        "",
    ]
    Path("results").mkdir(exist_ok=True)
    Path("results/model_comparison.md").write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
