# agents/random_agent.py

import random
from agents.base_agent import BaseAgent

LABELS = ["important", "spam", "promotion", "social", "later"]

class RandomAgent(BaseAgent):
    def act(self, state):
        return random.choice(LABELS)