"""Streamlit interface for the Assignment 1 Student Support Agent."""

from __future__ import annotations

from html import escape

import streamlit as st

from student_support_agent.agent import AgentRunError, StudentSupportAgent
from student_support_agent.config import (
    ConfigurationError,
    load_settings,
    project_data_directory,
)


st.set_page_config(
    page_title="Student Support Agent",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .block-container {max-width: 1180px; padding-top: 2.25rem; padding-bottom: 3rem;}
      .hero {background: linear-gradient(120deg, #0d47a1 0%, #1565c0 48%, #00a6a6 100%);
             border-radius: 24px; color: white; padding: 2.25rem 2.5rem; margin-bottom: 1.5rem;
             box-shadow: 0 18px 36px rgba(13, 71, 161, 0.20);}
      .hero-kicker {font-size: 0.82rem; font-weight: 700; letter-spacing: 0.13em; text-transform: uppercase;
                    opacity: 0.82; margin-bottom: 0.45rem;}
      .hero h1 {font-size: 2.4rem; margin: 0; line-height: 1.15;}
      .hero p {font-size: 1.05rem; margin: 0.75rem 0 0; max-width: 680px; opacity: 0.92;}
      .feature-card {background: white; border: 1px solid #e5eaf2; border-radius: 18px; min-height: 124px;
                     padding: 1.1rem 1.2rem; box-shadow: 0 6px 18px rgba(26, 55, 88, 0.06);}
      .feature-icon {font-size: 1.45rem; margin-bottom: 0.38rem;}
      .feature-title {font-weight: 700; color: #102a43; margin-bottom: 0.2rem;}
      .feature-copy {color: #52616b; font-size: 0.9rem; line-height: 1.4;}
      .section-label {font-size: 0.82rem; letter-spacing: 0.1em; text-transform: uppercase; font-weight: 700;
                      color: #1565c0; margin: 1.8rem 0 0.45rem;}
      .answer-card {background: #f7fbff; border: 1px solid #cfe6ff; border-left: 5px solid #1565c0;
                    border-radius: 14px; padding: 1.2rem 1.35rem; margin-top: 0.5rem;}
      .tool-pill {display: inline-block; margin: 0.18rem 0.3rem 0.18rem 0; padding: 0.32rem 0.62rem;
                  border-radius: 999px; background: #e6f7f5; color: #006b66; font-size: 0.84rem; font-weight: 600;}
      div[data-testid="stForm"] {background: white; border: 1px solid #e5eaf2; border-radius: 20px;
                                  padding: 1.35rem 1.45rem 0.8rem; box-shadow: 0 10px 24px rgba(26, 55, 88, 0.07);}
      div[data-testid="stMetric"] {background: white; border: 1px solid #e5eaf2; border-radius: 14px; padding: 0.75rem;}
      .stButton > button, .stFormSubmitButton > button {border-radius: 10px; font-weight: 700;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

with st.sidebar:
    st.markdown("## 🎓 Student Support")
    st.caption("Assignment 1 · Local tool-calling agent")
    st.divider()
    st.markdown("### Privacy first")
    st.write(
        "Use only non-sensitive policy questions. Never enter student IDs, grades, fee "
        "balances, passwords, or other private information."
    )
    st.markdown("### What this app can do")
    st.write(
        "Search approved project policies and store explicitly requested non-sensitive "
        "response preferences."
    )
    if st.button("Clear displayed response", use_container_width=True):
        st.session_state.last_result = None
        st.rerun()

st.markdown(
    """
    <section class="hero">
      <div class="hero-kicker">Academic project · privacy-aware support</div>
      <h1>Find clear answers to policy questions.</h1>
      <p>Ask about the approved fictional policy pack and see the agent’s answer, tool activity, and runtime metrics in one place.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

feature_one, feature_two, feature_three = st.columns(3)
with feature_one:
    st.markdown(
        "<div class='feature-card'><div class='feature-icon'>🔎</div>"
        "<div class='feature-title'>Grounded policy search</div>"
        "<div class='feature-copy'>Answers are based on the project’s approved policy documents.</div></div>",
        unsafe_allow_html=True,
    )
with feature_two:
    st.markdown(
        "<div class='feature-card'><div class='feature-icon'>🛡️</div>"
        "<div class='feature-title'>Privacy by design</div>"
        "<div class='feature-copy'>The app avoids private student records and never exposes API credentials.</div></div>",
        unsafe_allow_html=True,
    )
with feature_three:
    st.markdown(
        "<div class='feature-card'><div class='feature-icon'>⚡</div>"
        "<div class='feature-title'>Visible execution</div>"
        "<div class='feature-copy'>Review latency, token use, and local tools selected for each request.</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("<div class='section-label'>Ask the agent</div>", unsafe_allow_html=True)
with st.form("support_question", clear_on_submit=False):
    question = st.text_area(
        "Ask a non-sensitive policy question",
        placeholder="Enter a question about an approved policy.",
        max_chars=2_000,
        height=130,
        label_visibility="collapsed",
    )
    submitted = st.form_submit_button("Ask the agent", type="primary", use_container_width=True)

if submitted:
    if not question.strip():
        st.warning("Enter a non-sensitive policy question first.")
    else:
        try:
            with st.spinner("Checking approved policy information..."):
                settings = load_settings()
                st.session_state.last_result = StudentSupportAgent(
                    settings,
                    project_data_directory(),
                ).respond(question)
        except ConfigurationError as error:
            st.error(f"Configuration error: {error}")
        except AgentRunError as error:
            st.error(f"Agent error: {error}")

result = st.session_state.last_result
if result is not None:
    st.markdown("<div class='section-label'>Response</div>", unsafe_allow_html=True)
    st.markdown("<div class='answer-card'>", unsafe_allow_html=True)
    st.write(result.answer)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='section-label'>Run metrics</div>", unsafe_allow_html=True)
    latency, prompt_tokens, completion_tokens, tool_count = st.columns(4)
    latency.metric("Latency", f"{result.metrics.latency_ms} ms")
    prompt_tokens.metric("Prompt tokens", result.metrics.prompt_tokens or "N/A")
    completion_tokens.metric(
        "Completion tokens",
        result.metrics.completion_tokens or "N/A",
    )
    tool_count.metric("Tools used", len(result.metrics.tool_calls))

    st.markdown("<div class='section-label'>Tool activity</div>", unsafe_allow_html=True)
    if result.metrics.tool_calls:
        tool_pills = "".join(
            f"<span class='tool-pill'>{escape(tool_call.name)} · {escape(tool_call.status)}</span>"
            for tool_call in result.metrics.tool_calls
        )
        st.markdown(tool_pills, unsafe_allow_html=True)
    else:
        st.info("No tools were required for this request.")
