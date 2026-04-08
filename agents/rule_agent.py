# agents/rule_agent.py

from typing import Any, Dict, List

from agents.base_agent import BaseAgent


class RuleAgent(BaseAgent):
    """
    Keyword-based heuristic agent for simple email triage.
    """

    name = "rule_agent"

    SPAM_KEYWORDS: List[str] = [
        "win",
        "winner",
        "free",
        "offer",
        "claim now",
        "lottery",
        "prize",
        "click here",
    ]

    IMPORTANT_KEYWORDS: List[str] = [
        "meeting",
        "project",
        "deadline",
        "interview",
        "assignment",
        "submission",
        "client",
        "urgent",
        "review",
    ]

    PROMOTION_KEYWORDS: List[str] = [
        "discount",
        "sale",
        "deal",
        "coupon",
        "limited time",
        "flat off",
        "promo",
        "shop now",
    ]

    SOCIAL_KEYWORDS: List[str] = [
        "friend",
        "liked",
        "commented",
        "tagged",
        "mentioned",
        "follow",
        "request",
        "reaction",
    ]

    def _get_text(self, state: Dict[str, Any]) -> str:
        subject = str(state.get("subject", ""))
        body = str(state.get("email_text", ""))
        return f"{subject} {body}".lower().strip()

    def _contains_any(self, text: str, keywords: List[str]) -> bool:
        return any(keyword in text for keyword in keywords)

    def act(self, state: Dict[str, Any]) -> str:
        text = self._get_text(state)

        if self._contains_any(text, self.SPAM_KEYWORDS):
            return "spam"

        if self._contains_any(text, self.IMPORTANT_KEYWORDS):
            return "important"

        if self._contains_any(text, self.PROMOTION_KEYWORDS):
            return "promotion"

        if self._contains_any(text, self.SOCIAL_KEYWORDS):
            return "social"

        return "later"
