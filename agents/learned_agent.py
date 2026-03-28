# agents/learned_agent.py

from transformers import pipeline
from agents.base_agent import BaseAgent

class LearnedAgent(BaseAgent):
    def __init__(self):
        self.classifier = pipeline("zero-shot-classification")
        self.labels = ["important", "spam", "promotion", "social", "later"]

    def act(self, state):
        result = self.classifier(
            state["email_text"],
            self.labels
        )
        return result["labels"][0]