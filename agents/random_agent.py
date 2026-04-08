import random
from typing import Any, Dict

from agents.base_agent import BaseAgent
from agents.constants import LABELS


class RandomAgent(BaseAgent):
    """
    Random baseline agent.
    Useful as a lower-bound benchmark.
    """

    name = "random_agent"

    def act(self, state: Dict[str, Any]) -> str:
        return random.choice(LABELS)
