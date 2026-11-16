import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

from analyzer.analysis import SEVERITY_ORDER, analyze, is_grounded
from analyzer.redact import redact, restore
from analyzer.safety import MAX_CHARS, detect_injection_attempt, prepare_log

load_dotenv()

st.set_page_config(page_title="AI Log Analyzer", page_icon="🔍")
st.title("🔍 AI Log Analyzer")
st.write("Upload a log file and get an AI-assisted analysis. Always verify the findings yourself.")

redact_on = st.checkbox("Redact IP addresses and e-mails before sending to the AI (recommended)", value=True)
st.caption(
    "The log is sent to a third-party API. Usernames, hostnames and secrets in free text are not "
    "detected by redaction, so do not upload logs you are not allowed to share."
)

uploaded_file = st.file_uploader("Upload Log File", type=["log", "txt"])

if uploaded_file:
    log_text, truncated = prepare_log(uploaded_file.read())
    if truncated:
        st.warning(f"The file is larger than {MAX_CHARS:,} characters. Only the first part will be analyzed.")

    st.subheader("📄 Log Content")
    st.text_area("Log content", log_text, height=200, label_visibility="collapsed")

    suspicious = detect_injection_attempt(log_text)
    if suspicious:
        st.warning(
            "This log contains text that looks like instructions to an AI model (possible prompt injection). "
            "The analysis treats the log as data, but review these lines manually:"
        )
        st.code("\n".join(suspicious), wrap_lines=True)

    if st.button("🤖 Analyze with AI"):
        if redact_on:
            send_text, mapping = redact(log_text)
        else:
            send_text, mapping = log_text, {}

        with st.expander("Text sent to the AI", expanded=True):
            st.code(send_text, language=None, wrap_lines=True)

        llm = ChatGoogleGenerativeAI(
            model=os.getenv("MODEL_NAME", "gemini-2.5-flash"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
            temperature=0,
        )
        with st.spinner("AI is analyzing your logs..."):
            try:
                analysis = analyze(send_text, llm)
            except Exception as exc:
                st.error(f"The analysis failed ({type(exc).__name__}). Check your API key, model name and quota.")
                st.stop()

        def show(text: str) -> str:
            return restore(text, mapping) if mapping else text

        st.subheader("📊 AI Analysis")
        st.markdown(f"**Summary.** {show(analysis.summary)}")

        findings = sorted(analysis.findings, key=lambda f: SEVERITY_ORDER[f.severity])
        if not findings:
            st.info("No findings reported.")
        for f in findings:
            st.markdown(f"**[{f.severity}] {f.category}**")
            st.code(show(f.line), language=None, wrap_lines=True)
            if not is_grounded(f.line, send_text):
                st.warning("This quoted line was not found in the log. The finding may be invented.")
            st.markdown(f"{show(f.explanation)}\n\n*Recommendation:* {show(f.recommendation)}")
            st.divider()
