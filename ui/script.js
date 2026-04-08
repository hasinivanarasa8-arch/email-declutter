const API_BASE = "http://127.0.0.1:5000";

function getSelectedAgent() {
    return document.getElementById("agent-select").value;
}

function normalizeClassName(value) {
    return String(value || "")
        .toLowerCase()
        .trim()
        .replace(/\s+/g, "-")
        .replace(/[^a-z0-9-_]/g, "");
}

function setBadge(elementId, value, prefix) {
    const el = document.getElementById(elementId);
    const normalized = normalizeClassName(value);

    el.textContent = value || "---";
    el.className = `${prefix ? prefix + "-" + normalized : "neutral"} ${prefix ? "" : "badge"}`.trim();

    if (elementId === "prediction" || elementId === "true-label") {
        el.className = `badge ${value ? "label-" + normalized : "neutral"}`;
    }

    if (!value || value === "---") {
        el.className = "badge neutral";
    }
}

function setReward(value) {
    const el = document.getElementById("reward");
    const num = Number(value ?? 0);

    el.textContent = Number.isNaN(num) ? value : num;

    if (num > 0) {
        el.className = "reward-pill reward-positive";
    } else if (num < 0) {
        el.className = "reward-pill reward-negative";
    } else {
        el.className = "reward-pill reward-zero";
    }
}

function setStatus(value) {
    const el = document.getElementById("status");
    const normalized = normalizeClassName(value);

    el.textContent = value || "---";

    if (!value || value === "---") {
        el.className = "status-pill neutral";
        return;
    }

    el.className = `status-pill status-${normalized}`;
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
    document.getElementById("prediction").className = "badge neutral";

    document.getElementById("true-label").textContent = "---";
    document.getElementById("true-label").className = "badge neutral";

    document.getElementById("reward").textContent = "0";
    document.getElementById("reward").className = "reward-pill reward-zero";

    document.getElementById("status").textContent = "---";
    document.getElementById("status").className = "status-pill neutral";
}

async function resetDemo() {
    try {
        const agent = getSelectedAgent();
        const response = await fetch(`${API_BASE}/reset?agent=${agent}`);
        const data = await response.json();

        updateEmail(data.state);
        updateMetrics(data.stats);
        clearResult();
    } catch (error) {
        console.error("Reset failed:", error);
    }
}

async function loadNextEmail() {
    try {
        const response = await fetch(`${API_BASE}/next`);
        const data = await response.json();

        updateEmail(data.state);
        updateMetrics(data.stats);
        clearResult();
    } catch (error) {
        console.error("Loading next email failed:", error);
    }
}

async function runAgent() {
    try {
        const agent = getSelectedAgent();

        const response = await fetch(`${API_BASE}/act`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ agent })
        });

        const data = await response.json();

        setBadge("prediction", data.prediction);
        setBadge("true-label", data.true_label);
        setReward(data.reward);
        setStatus(data.status);

        updateMetrics(data.stats);
        updateEmail(data.next_state);
    } catch (error) {
        console.error("Run agent failed:", error);
    }
}

window.onload = resetDemo;