from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """
    Base class for all email triage agents.

    Each agent receives a state dictionary and returns
    a single label string representing its decision.
    """

    name = "base_agent"

    @abstractmethod
    def act(self, state: Dict[str, Any]) -> str:
        """
        Predict a label for the given email state.
        """
        raise NotImplementedError
