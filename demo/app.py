import os
import sys

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from env.inbox_env import InboxEnv
from agents.random_agent import RandomAgent
from agents.rule_agent import RuleAgent
from agents.learned_agent import LearnedAgent

app = Flask(
    __name__,
    static_folder="../ui",
    static_url_path=""
)
CORS(app)

env = InboxEnv()

agents = {
    "random": RandomAgent(),
    "rule": RuleAgent(),
    "learned": LearnedAgent(),
}

current_state = None
current_agent_name = "rule"

stats = {
    "processed": 0,
    "correct": 0,
    "total_reward": 0,
    "spam_caught": 0,
    "important_caught": 0,
}


def safe_state_payload(state):
    if not state:
        return {
            "email_text": "",
            "subject": "No Subject",
            "sender": "Unknown Sender",
        }

    return {
        "email_text": state.get("email_text", ""),
        "subject": state.get("subject", "No Subject"),
        "sender": state.get("sender", "Unknown Sender"),
    }


def reset_demo(agent_name="rule"):
    global current_state, current_agent_name, stats

    current_agent_name = agent_name if agent_name in agents else "rule"
    current_state = env.reset()

    stats = {
        "processed": 0,
        "correct": 0,
        "total_reward": 0,
        "spam_caught": 0,
        "important_caught": 0,
    }

    return current_state


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/agents", methods=["GET"])
def list_agents():
    return jsonify({
        "agents": list(agents.keys()),
        "default": current_agent_name,
    })


@app.route("/reset", methods=["GET", "POST"])
def reset():
    global current_state

    agent_name = "rule"

    if request.method == "GET":
        agent_name = request.args.get("agent", "rule").lower()
    else:
        payload = request.get_json(silent=True) or {}
        agent_name = payload.get("agent", "rule").lower()

    current_state = reset_demo(agent_name)

    return jsonify({
        "message": "Demo reset successful",
        "agent": current_agent_name,
        "state": safe_state_payload(current_state),
        "stats": {
            **stats,
            "accuracy": 0.0,
        },
    })


@app.route("/next", methods=["GET"])
def next_email():
    global current_state

    if current_state is None:
        current_state = env.reset()

    accuracy = stats["correct"] / stats["processed"] if stats["processed"] else 0.0

    return jsonify({
        "agent": current_agent_name,
        "state": safe_state_payload(current_state),
        "stats": {
            **stats,
            "accuracy": round(accuracy, 4),
        },
    })


@app.route("/act", methods=["POST"])
def act():
    global current_state, current_agent_name, stats

    if current_state is None:
        current_state = env.reset()

    payload = request.get_json(silent=True) or {}
    agent_name = payload.get("agent", current_agent_name).lower()

    if agent_name not in agents:
        return jsonify({"error": f"Unknown agent: {agent_name}"}), 400

    current_agent_name = agent_name
    agent = agents[agent_name]

    email_before_action = current_state
    prediction = agent.act(current_state)

    next_state, reward, done, info = env.step(prediction)

    true_label = info.get("true_label", "unknown")
    correct = prediction == true_label

    stats["processed"] += 1
    stats["total_reward"] += reward

    if correct:
        stats["correct"] += 1

    if prediction == "spam" and true_label == "spam":
        stats["spam_caught"] += 1

    if prediction == "important" and true_label == "important":
        stats["important_caught"] += 1

    accuracy = stats["correct"] / stats["processed"] if stats["processed"] else 0.0

    current_state = next_state

    return jsonify({
        "agent": current_agent_name,
        "email": safe_state_payload(email_before_action),
        "prediction": prediction,
        "true_label": true_label,
        "reward": reward,
        "correct": correct,
        "done": done,
        "status": "Correct prediction" if correct else "Incorrect prediction",
        "next_state": safe_state_payload(current_state),
        "stats": {
            **stats,
            "accuracy": round(accuracy, 4),
        },
    })


if __name__ == "__main__":
    reset_demo("rule")
    app.run(host="0.0.0.0", port=5000, debug=True)
