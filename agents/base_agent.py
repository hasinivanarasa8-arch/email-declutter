# agents/base_agent.py

class BaseAgent:
    def act(self, state):
        raise NotImplementedError("Subclasses must implement this method")