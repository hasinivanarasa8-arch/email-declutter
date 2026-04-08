import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from env.inbox_env import InboxEnv
from agents.random_agent import RandomAgent
from agents.rule_agent import RuleAgent

# Optional learned agent loading
try:
    from agents.learned_agent import LearnedAgent
    LEARNED_AGENT_AVAILABLE = True
except Exception:
    LEARNED_AGENT_AVAILABLE = False


def build_agents():
    agents = {
        "random": RandomAgent(),
        "rule": RuleAgent(),
    }

    if LEARNED_AGENT_AVAILABLE:
        try:
            agents["learned"] = LearnedAgent()
        except Exception:
            pass

    return agents


def reset_environment():
    st.session_state.env = InboxEnv()
    st.session_state.current_state = st.session_state.env.reset()
    st.session_state.done = False
    st.session_state.stats = {
        "processed": 0,
        "correct": 0,
        "total_reward": 0,
        "spam_caught": 0,
        "important_caught": 0,
    }


# Initialize session state safely
if "agents" not in st.session_state:
    st.session_state.agents = build_agents()

if "env" not in st.session_state:
    reset_environment()

if "current_state" not in st.session_state:
    reset_environment()

if "stats" not in st.session_state:
    reset_environment()

if "done" not in st.session_state:
    st.session_state.done = False


# UI Title
st.title("📧 Inbox Triage AI Agent")
st.caption("Agentic email triage demo with reward-driven evaluation")

# Agent selection
available_agents = list(st.session_state.agents.keys())
agent_name = st.selectbox("Choose Agent", available_agents)
agent = st.session_state.agents[agent_name]

# Reset button
if st.button("🔄 Reset Environment"):
    reset_environment()
    st.success("Environment reset successfully.")

state = st.session_state.current_state

# Display email
st.subheader("📩 Current Email")

if state:
    st.write(f"**Subject:** {state.get('subject', 'No Subject')}")
    st.write(f"**Sender:** {state.get('sender', 'Unknown Sender')}")
    st.write(f"**Content:** {state.get('email_text', '')}")
else:
    st.info("No email available.")

# Action button
if st.button("🤖 Classify Email"):
    if st.session_state.done:
        st.warning("Episode already completed. Please reset the environment.")
    elif state is None:
        st.warning("No email to classify. Please reset the environment.")
    else:
        prediction = agent.act(state)

        next_state, reward, done, info = st.session_state.env.step(prediction)

        true_label = info.get("true_label", "unknown")
        correct = prediction == true_label

        # Update stats
        st.session_state.stats["processed"] += 1
        st.session_state.stats["total_reward"] += reward

        if correct:
            st.session_state.stats["correct"] += 1

        if prediction == "spam" and true_label == "spam":
            st.session_state.stats["spam_caught"] += 1

        if prediction == "important" and true_label == "important":
            st.session_state.stats["important_caught"] += 1

        processed = st.session_state.stats["processed"]
        accuracy = (
            st.session_state.stats["correct"] / processed if processed else 0.0
        )

        # Show result
        st.subheader("🤖 Prediction Result")
        st.write(f"**Prediction:** {prediction}")
        st.write(f"**True Label:** {true_label}")
        st.write(f"**Reward:** {reward}")
        st.write(f"**Status:** {'✅ Correct' if correct else '❌ Incorrect'}")

        # Move to next email
        st.session_state.current_state = next_state
        st.session_state.done = done

        if done:
            st.success("🎉 Episode completed. Please reset to start again.")

# Stats
st.subheader("📊 Performance Stats")

processed = st.session_state.stats["processed"]
accuracy = st.session_state.stats["correct"] / processed if processed else 0.0

st.write({
    **st.session_state.stats,
    "accuracy": round(accuracy, 4),
})
