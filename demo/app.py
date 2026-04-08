import os
import sys
import time
import html
import pandas as pd
import streamlit as st

print("RUNNING STREAMLIT DEMO APP")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agents.random_agent import RandomAgent
from agents.rule_agent import RuleAgent
from agents.learned_agent import LearnedAgent
from evaluation.evaluator import evaluate_agent


st.set_page_config(
    page_title="Inbox Triage AI Agent",
    page_icon="📩",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def inject_css():
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(180deg, #0b1120 0%, #111827 100%);
        color: #e5eefc;
    }
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    header[data-testid="stHeader"] {
        background: transparent;
    }
    #MainMenu, footer {
        visibility: hidden;
    }
    .hero {
        background: linear-gradient(135deg, rgba(79,140,255,0.18), rgba(168,85,247,0.14));
        border: 1px solid rgba(148,163,184,0.18);
        border-radius: 24px;
        padding: 28px 30px;
        margin-bottom: 22px;
        box-shadow: 0 18px 45px rgba(2,8,23,0.28);
    }
    .hero-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(148,163,184,0.12);
        color: #cbd5e1;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-bottom: 14px;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.05;
        color: #f8fbff;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #a9b7cf;
        line-height: 1.6;
        max-width: 900px;
    }
    .panel {
        background: rgba(15,23,42,0.84);
        border: 1px solid rgba(148,163,184,0.16);
        border-radius: 22px;
        padding: 22px;
        box-shadow: 0 12px 32px rgba(2,8,23,0.22);
        margin-bottom: 18px;
    }
    .panel-title {
        font-size: 1.4rem;
        font-weight: 800;
        color: #f8fbff;
        margin-bottom: 4px;
    }
    .panel-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
        margin-bottom: 18px;
    }
    .email-box {
        background: rgba(30, 41, 59, 0.55);
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 18px;
        padding: 18px;
        margin-top: 14px;
    }
    .email-field {
        margin-bottom: 12px;
    }
    .email-label {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 4px;
    }
    .email-value {
        color: #f8fbff;
        font-size: 1rem;
        line-height: 1.6;
        word-break: break-word;
    }
    div[data-testid="stSelectbox"] label,
    div[data-testid="stNumberInput"] label {
        color: #dce8fb !important;
        font-weight: 700 !important;
    }
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stNumberInput"] > div {
        background-color: rgba(15,23,42,0.84);
        border-radius: 14px;
    }
    .stButton > button {
        width: 100%;
        border-radius: 14px;
        padding: 0.72rem 1rem;
        font-weight: 800;
        border: 1px solid rgba(148,163,184,0.16);
        background: linear-gradient(135deg, #4f8cff, #2563eb);
        color: white;
        box-shadow: 0 10px 24px rgba(37,99,235,0.24);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #5c97ff, #2f6df0);
        color: white;
    }
    div[data-testid="metric-container"] {
        background: rgba(15,23,42,0.84);
        border: 1px solid rgba(148,163,184,0.14);
        padding: 16px;
        border-radius: 18px;
        box-shadow: 0 10px 24px rgba(2,8,23,0.18);
    }
    div[data-testid="metric-container"] label {
        color: #94a3b8 !important;
        font-weight: 700 !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #f8fbff;
        font-weight: 800;
    }
    .notes-box {
        background: rgba(15,23,42,0.84);
        border: 1px solid rgba(148,163,184,0.14);
        border-radius: 18px;
        padding: 18px 20px;
        margin-top: 18px;
    }
    </style>
    """, unsafe_allow_html=True)


inject_css()


@st.cache_resource
def get_agents():
    return {
        "Random": RandomAgent(),
        "Rule": RuleAgent(),
        "Learned (HF)": LearnedAgent()
    }


def run_single_agent(agent_name: str, steps: int):
    agents = get_agents()
    agent = agents[agent_name]
    start = time.time()
    result = evaluate_agent(agent, steps=steps)
    elapsed = time.time() - start
    result["runtime_sec"] = round(elapsed, 2)
    return result


def run_all_agents(steps: int):
    outputs = []
    agents = get_agents()
    for name, agent in agents.items():
        start = time.time()
        result = evaluate_agent(agent, steps=steps)
        elapsed = time.time() - start
        outputs.append({
            "Agent": name,
            "Accuracy": round(float(result.get("accuracy", 0)) * 100, 2),
            "Total Reward": result.get("total_reward", 0),
            "Runtime (s)": round(elapsed, 2),
            "Label Stats": result.get("label_stats", {})
        })
    return outputs


def label_stats_to_df(label_stats):
    if not label_stats:
        return pd.DataFrame(columns=["Label", "Accuracy"])

    rows = []
    for label, value in label_stats.items():
        if isinstance(value, dict):
            if "accuracy" in value:
                acc = value["accuracy"]
            elif "correct" in value and "total" in value and value["total"]:
                acc = value["correct"] / value["total"]
            else:
                acc = 0
        else:
            acc = value

        rows.append({
            "Label": str(label),
            "Accuracy": round(float(acc) * 100, 2)
        })

    return pd.DataFrame(rows)


st.markdown("""
<div class="hero">
    <div class="hero-badge">Hackathon Demo Dashboard</div>
    <div class="hero-title">Inbox Triage AI Agent</div>
    <div class="hero-subtitle">
        Compare rule-based, random, and learned agents for inbox triage using reward-driven evaluation.
        This dashboard highlights accuracy, total reward, runtime, and label-wise performance in one clean view.
    </div>
</div>
""", unsafe_allow_html=True)

control_col1, control_col2, control_col3, control_col4, control_col5 = st.columns([2.0, 1.1, 1, 1, 1])

with control_col1:
    selected_agent = st.selectbox(
        "Choose agent",
        ["Random", "Rule", "Learned (HF)"],
        index=2
    )

with control_col2:
    steps = st.number_input("Evaluation steps", min_value=10, max_value=500, value=50, step=10)

with control_col3:
    run_one = st.button("Run Selected Agent")

with control_col4:
    run_all = st.button("Run Full Comparison")

with control_col5:
    reset_env = st.button("Reset Environment")

if "single_result" not in st.session_state:
    st.session_state.single_result = None

if "all_results" not in st.session_state:
    st.session_state.all_results = None

if reset_env:
    st.session_state.single_result = None
    st.session_state.all_results = None
    st.success("Environment reset successfully")

if run_one:
    with st.spinner(f"Evaluating {selected_agent} agent..."):
        st.session_state.single_result = (selected_agent, run_single_agent(selected_agent, int(steps)))

if run_all:
    with st.spinner("Running full agent comparison..."):
        st.session_state.all_results = run_all_agents(int(steps))

left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Selected Agent Evaluation</div>
        <div class="panel-subtitle">Focused view for one agent with summary metrics and label-wise breakdown.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.single_result is None:
        st.info("Run a selected agent to view detailed results.")
    else:
        agent_name, result = st.session_state.single_result

        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Agent", agent_name)
        with m2:
            st.metric("Accuracy", f"{float(result.get('accuracy', 0)) * 100:.2f}%")
        with m3:
            st.metric("Total Reward", result.get("total_reward", 0))
        with m4:
            st.metric("Runtime", f"{result.get('runtime_sec', 0)}s")

        state = result.get("final_state") or {}
        preview_email = state.get("current_email") or {}

        subject = html.escape(str(preview_email.get("subject", "N/A")))
        sender = html.escape(str(preview_email.get("sender", "N/A")))
        body = html.escape(str(preview_email.get("body", "N/A")))

        st.markdown("""
        <div class="panel">
            <div class="panel-title">Sample Email for Verification</div>
            <div class="panel-subtitle">This is the initial email from the episode, shown so judges can verify what the environment is processing.</div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="email-box">
            <div class="email-field">
                <div class="email-label">Subject</div>
                <div class="email-value">{subject}</div>
            </div>
            <div class="email-field">
                <div class="email-label">Sender</div>
                <div class="email-value">{sender}</div>
            </div>
            <div class="email-field">
                <div class="email-label">Body / Snippet</div>
                <div class="email-value">{body}</div>
            </div>
        </div>
        </div>
        """, unsafe_allow_html=True)

        label_df = label_stats_to_df(result.get("label_stats", {}))

        st.markdown("""
        <div class="panel">
            <div class="panel-title">Label-wise Accuracy</div>
            <div class="panel-subtitle">How well the selected agent performed on each email category.</div>
        </div>
        """, unsafe_allow_html=True)

        if not label_df.empty:
            st.dataframe(label_df, use_container_width=True, hide_index=True)
            st.bar_chart(label_df.set_index("Label"))
        else:
            st.warning("No label statistics were returned by the evaluator.")

with right:
    st.markdown("""
    <div class="panel">
        <div class="panel-title">Leaderboard Comparison</div>
        <div class="panel-subtitle">Compare all agents side by side on overall accuracy, reward, and runtime.</div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.all_results is None:
        st.info("Run full comparison to generate the leaderboard.")
    else:
        leaderboard_rows = []
        for item in st.session_state.all_results:
            leaderboard_rows.append({
                "Agent": item["Agent"],
                "Accuracy (%)": item["Accuracy"],
                "Total Reward": item["Total Reward"],
                "Runtime (s)": item["Runtime (s)"]
            })

        leaderboard_df = pd.DataFrame(leaderboard_rows).sort_values(
            by=["Accuracy (%)", "Total Reward"],
            ascending=[False, False]
        )

        st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)

        chart_df = leaderboard_df.set_index("Agent")[["Accuracy (%)", "Total Reward"]]
        st.bar_chart(chart_df)

        top_agent = leaderboard_df.iloc[0]["Agent"]
        st.success(f"Top performer: {top_agent}")

st.markdown("""
<div class="notes-box">
    <h3 style="margin-top:0; color:#f8fbff;">Evaluation Notes</h3>
    <ul style="color:#cbd5e1; line-height:1.8; margin-bottom:0;">
        <li><strong>Random Agent</strong> provides a baseline for comparison.</li>
        <li><strong>Rule Agent</strong> reflects heuristic decision-making.</li>
        <li><strong>Learned (HF) Agent</strong> demonstrates model-driven triage behavior.</li>
        <li><strong>Accuracy</strong> shows classification quality, while <strong>Total Reward</strong> reflects task-specific decision value.</li>
    </ul>
</div>
""", unsafe_allow_html=True)