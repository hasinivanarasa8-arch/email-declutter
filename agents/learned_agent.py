from typing import Any, Dict

from transformers import pipeline

from agents.base_agent import BaseAgent
from agents.constants import LABELS


class LearnedAgent(BaseAgent):
    """
    Zero-shot semantic classification agent.
    """

    name = "learned_agent"

    def __init__(self, model_name: str = "facebook/bart-large-mnli"):
        self.labels = LABELS
        self.last_result = None
        self.classifier = pipeline(
            "zero-shot-classification",
            model=model_name
        )

    def _get_text(self, state: Dict[str, Any]) -> str:
        subject = str(state.get("subject", ""))
        body = str(state.get("email_text", ""))
        sender = str(state.get("sender", ""))
        return f"Sender: {sender}\nSubject: {subject}\nBody: {body}".strip()

    def act(self, state: Dict[str, Any]) -> str:
        text = self._get_text(state)
        result = self.classifier(text, self.labels)
        self.last_result = result
        return result["labels"][0]
