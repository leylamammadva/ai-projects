# 🤖 AI Projects

Small AI projects built with Python, LangChain and the Gemini API.

## 🔍 AI Log Analyzer
Security-aware log triage with structured output, redaction of IPs and e-mails, prompt-injection defences, tests and a model comparison. See [log-analyzer/README.md](log-analyzer/README.md) for details.

## 😊 AI Sentiment Analyzer
NLP sentiment analysis with Google Gemini. Returns sentiment, key emotions and reasoning. The confidence score is reported by the model itself and is not a measured accuracy.

**Tech:** Python, LangChain, Gemini API, Streamlit

### Setup
```bash
git clone https://github.com/leylamammadva/ai-projects.git
cd ai-projects
pip install -r requirements.txt
```
Create a `.env` file with `GOOGLE_API_KEY=your_api_key_here` (never commit it), then run:
```bash
streamlit run sentiment-analyzer/app.py
```