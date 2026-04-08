const API_BASE = "http://127.0.0.1:5000";

function getSelectedAgent() {
    return document.getElementById("agent-select").value;
}

function updateEmail(state) {
    document.getElementById("subject").textContent = state.subject || "No Subject";
    document.getElementById("sender").textContent = state.sender || "Unknown Sender";
    document.getElementById("email-text").textContent = state.email_text || "";
}

function updateMetrics(stats) {
    document.getElementById("processed").textContent = stats.processed ?? 0;
    document.getElementById("accuracy").textContent = `${((stats.accuracy ?? 0) * 100).toFixed(1)}%`;
    document.getElementById("total-reward").textContent = stats.total_reward ?? 0;
    document.getElementById("spam-caught").textContent = stats.spam_caught ?? 0;
    document.getElementById("important-caught").textContent = stats.important_caught ?? 0;
}

function clearResult() {
    document.getElementById("prediction").textContent = "---";
    document.getElementById("true-label").textContent = "---";
    document.getElementById("reward").textContent = "0";
    document.getElementById("status").textContent = "---";
}

async function resetDemo() {
    const agent = getSelectedAgent();

    const response = await fetch(`${API_BASE}/reset?agent=${agent}`);
    const data = await response.json();

    updateEmail(data.state);
    updateMetrics(data.stats);
    clearResult();
}

async function loadNextEmail() {
    const response = await fetch(`${API_BASE}/next`);
    const data = await response.json();

    updateEmail(data.state);
    updateMetrics(data.stats);
    clearResult();
}

async function runAgent() {
    const agent = getSelectedAgent();

    const response = await fetch(`${API_BASE}/act`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ agent })
    });

    const data = await response.json();

    document.getElementById("prediction").textContent = data.prediction;
    document.getElementById("true-label").textContent = data.true_label;
    document.getElementById("reward").textContent = data.reward;
    document.getElementById("status").textContent = data.status;

    updateMetrics(data.stats);
    updateEmail(data.next_state);
}

window.onload = resetDemo;
