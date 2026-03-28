# agents/rule_agent.py

from agents.base_agent import BaseAgent

class RuleAgent(BaseAgent):
    def act(self, state):
        text = state["email_text"].lower()

        if "win" in text or "free" in text or "offer" in text:
            return "spam"

        if "meeting" in text or "project" in text or "interview" in text:
            return "important"

        if "discount" in text or "sale" in text:
            return "promotion"

        if "friend" in text or "liked" in text:
            return "social"

        return "later"