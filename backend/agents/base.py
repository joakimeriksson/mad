"""
Base agent class for MAD agents.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class Agent(ABC):
    """Base class for all agents in the Multi-Agent Dungeon."""

    def __init__(self, agent_id: str, name: str):
        self.agent_id = agent_id
        self.name = name
        self.conversation_history: list[Dict[str, str]] = []

    @abstractmethod
    async def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Generate a response to a user message.

        Args:
            message: The user's message
            context: Optional context dictionary (e.g., poster_id, tags)

        Returns:
            The agent's response
        """
        pass

    def add_to_history(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """Clear the conversation history."""
        self.conversation_history = []

    def get_history(self) -> list[Dict[str, str]]:
        """Get the conversation history."""
        return self.conversation_history
