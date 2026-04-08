from __future__ import annotations

from typing import Any, Dict, Optional

from env.inbox_env import InboxEnv, ActionType, ReplyTemplate, EmailLabel


def evaluate_agent(
    agent: Any,
    steps: int = 50,
    seed: int = 42,
    env: Optional[InboxEnv] = None,
) -> Dict[str, Any]:
    env = env or InboxEnv(seed=seed, max_steps=steps)

    # Initial state before episode starts
    initial_observation = env.reset(seed=seed)
    initial_state = env.state()

    preview_email = {}
    if isinstance(initial_state, dict):
        preview_email = initial_state.get("current_email") or {}

    obs = initial_observation
    total_reward = 0.0
    done = False
    actual_steps = 0

    while not done and actual_steps < steps:
        action = _get_agent_action(agent, obs)
        obs, reward, done, _info = env.step(action)
        total_reward += reward
        actual_steps += 1

    final_state = env.state()
    grade = env.grade_episode()

    return {
        "accuracy": grade.get("accuracy", 0.0),
        "total_reward": total_reward,
        "label_stats": grade.get("label_stats", {}),
        "steps_taken": actual_steps,
        "final_score": grade.get("final_score", total_reward),
        "breakdown": grade.get("breakdown", {}),
        "preview_email": preview_email,      # use this in UI
        "initial_observation": initial_observation,
        "initial_state": initial_state,
        "final_state": final_state,
    }


def _get_agent_action(agent: Any, observation: Dict[str, Any]) -> Dict[str, Any]:
    raw_action = None

    candidates = [
        ("act", lambda: agent.act(observation)),
        ("predict", lambda: agent.predict(observation)),
        ("select_action", lambda: agent.select_action(observation)),
        ("__call__", lambda: agent(observation)),
    ]

    for name, fn in candidates:
        if name != "__call__" and not hasattr(agent, name):
            continue
        try:
            raw_action = fn()
            break
        except Exception:
            continue

    if raw_action is None:
        return _fallback_policy(observation)

    return _normalize_agent_output(raw_action, observation)


def _normalize_agent_output(raw_action: Any, observation: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(raw_action, dict):
        action_type = str(raw_action.get("type", "")).lower().strip()
        template = str(raw_action.get("template", ReplyTemplate.NONE.value)).lower().strip()

        if action_type in {a.value for a in ActionType}:
            if template not in {t.value for t in ReplyTemplate}:
                template = ReplyTemplate.NONE.value
            return {"type": action_type, "template": template}

        label_like = raw_action.get("label", raw_action.get("prediction"))
        if label_like is not None:
            return _label_to_action(str(label_like), observation)

    if isinstance(raw_action, str):
        text = raw_action.lower().strip()

        if text in {a.value for a in ActionType}:
            return {"type": text, "template": ReplyTemplate.NONE.value}

        if text in {t.value for t in ReplyTemplate}:
            return {"type": ActionType.REPLY.value, "template": text}

        return _label_to_action(text, observation)

    return _fallback_policy(observation)


def _label_to_action(label_text: str, observation: Dict[str, Any]) -> Dict[str, Any]:
    text = label_text.lower().strip()

    if text in {"important", "urgent", EmailLabel.URGENT.value}:
        return {"type": ActionType.FLAG.value, "template": ReplyTemplate.NONE.value}

    if text in {"spam", EmailLabel.SPAM.value}:
        return {"type": ActionType.DELETE.value, "template": ReplyTemplate.NONE.value}

    if text in {"promotion", "promotions", EmailLabel.PROMOTION.value}:
        return {"type": ActionType.ARCHIVE.value, "template": ReplyTemplate.NONE.value}

    if text in {"normal", EmailLabel.NORMAL.value}:
        if "schedule" in observation.get("snippet", "").lower():
            return {"type": ActionType.REPLY.value, "template": ReplyTemplate.SCHEDULE.value}
        return {"type": ActionType.ARCHIVE.value, "template": ReplyTemplate.NONE.value}

    return _fallback_policy(observation)


def _fallback_policy(observation: Dict[str, Any]) -> Dict[str, Any]:
    subject = observation.get("subject", "").lower()
    snippet = observation.get("snippet", "").lower()
    sender = observation.get("sender", "").lower()
    urgency_hint = observation.get("urgency_hint", "").lower()

    text = " ".join([subject, snippet, sender])

    if urgency_hint == "high" or any(k in text for k in ["outage", "urgent", "approval", "deadline", "vip"]):
        return {"type": ActionType.FLAG.value, "template": ReplyTemplate.NONE.value}

    if any(k in text for k in ["suspended", "free vacation", "verify your account", "suspicious", "phishing"]):
        return {"type": ActionType.DELETE.value, "template": ReplyTemplate.NONE.value}

    if "reschedule" in text or "alternative slots" in text:
        return {"type": ActionType.REPLY.value, "template": ReplyTemplate.SCHEDULE.value}

    if any(k in text for k in ["brochure", "discount", "pricing", "newsletter", "promotion"]):
        return {"type": ActionType.ARCHIVE.value, "template": ReplyTemplate.NONE.value}

    return {"type": ActionType.ARCHIVE.value, "template": ReplyTemplate.NONE.value}