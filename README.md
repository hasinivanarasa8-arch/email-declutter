# 🚀 AI Inbox Intelligence

### Agentic Email Triage under Uncertainty

---

## 🔍 Overview

Modern inboxes are chaotic. Important emails get buried, spam slips through, and users waste time manually sorting everything.

This project models **email management as a sequential decision-making problem**, where AI agents must intelligently triage emails under uncertainty.

Instead of building a simple classifier, we created a **simulation environment** where multiple agents interact with an inbox and learn to make decisions based on rewards.

---

## 🧠 Key Idea

We treat inbox decluttering as an **agentic problem**:

* Each email is a **state**
* The agent selects an **action (label)**
* The environment returns a **reward**
* The process repeats over time

This transforms email filtering into a **reinforcement-style decision system**, not just static classification.

---

## ⚙️ System Architecture

```mermaid
flowchart TD
    A[User Interface] --> B[Flask Backend]
    B --> C[Agent (Random / Rule / Learned)]
    C --> D[Inbox Environment]
    D --> E[Reward Function]
    D --> F[Email Generator]
    E --> C
    F --> D
```

---

## 🤖 Agents Implemented

### 1. Random Agent

* Selects labels randomly
* Acts as a baseline
* Helps measure minimum performance

### 2. Rule-Based Agent

* Uses keyword heuristics
* Mimics traditional filtering systems
* Fast and interpretable

### 3. Learned Agent (Zero-Shot NLP)

* Uses HuggingFace transformers
* Understands semantic meaning of emails
* Generalizes beyond fixed rules

---

## 📦 Environment Design

### State

Each email contains:

* subject
* sender
* email_text
* hidden true_label

### Action Space

```text
important | spam | promotion | social | later
```

### Reward Function

* ✅ Correct classification → positive reward
* ❌ Incorrect classification → penalty
* 🚨 Missing important emails → higher penalty
* 🛑 Catching spam → bonus reward

This encourages **safe and intelligent decision-making**.

---

## 📊 Evaluation Metrics

* Accuracy
* Total Reward
* Label-wise Accuracy
* Processed Emails
* Correct Predictions

---

## 🖥️ Demo Features

* Interactive inbox simulation
* Switch between agents (Random / Rule / Learned)
* Real-time predictions
* Live metrics:

  * accuracy
  * total reward
  * spam caught
  * important emails handled
* Continuous stream of emails

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
python demo/app.py
```

Open in browser:

```text
http://127.0.0.1:5000
```

---

## 🐳 Docker Run

Build and run with Docker:

```bash
docker build -t email-declutter .
docker run -p 5000:5000 email-declutter
```

Or use Docker Compose:

```bash
docker compose up --build
```

Then open:

```text
http://127.0.0.1:5000
```

---

## 🎯 Why This Matters

Most email systems rely on static filtering rules.

This project demonstrates:

* **Adaptive decision-making**
* **Agent-based intelligence**
* **Reward-driven optimization**
* **Handling noisy and ambiguous inputs**

It reflects real-world challenges in:

* email clients
* notification systems
* task prioritization
* AI assistants

---

## ⚠️ Limitations

* Synthetic email dataset
* Simple reward function
* No long-term memory across sessions
* Learned agent depends on external model loading

---

## 🚀 Future Improvements

* Reinforcement learning (policy optimization)
* Memory-based agents (context awareness)
* Multi-step decision strategies (archive, reply, defer)
* Real email dataset integration
* Confidence-based routing (human-in-loop)

---

## 🧩 Hackathon Alignment

This project strongly aligns with:

* ✅ Agentic AI systems
* ✅ Environment-based learning
* ✅ Decision-making under uncertainty
* ✅ Multiple competing agent strategies
* ✅ Reward-driven evaluation

---

## 🏁 Final Note

This is not just an email classifier.

It is a **simulation framework for intelligent inbox management**, where agents learn to balance priorities, reduce clutter, and act under imperfect information.

---

## 🔗 Tech Stack

* Python
* Flask
* Transformers (HuggingFace)
* HTML / CSS / JS
* Custom Simulation Environment
