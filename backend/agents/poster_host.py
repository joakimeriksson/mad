"""
Poster Host Agent - Expert on a specific research poster.
"""

from typing import Optional, Dict, Any
from .base import Agent
from .ollama_service import OllamaService
import os


class PosterHostAgent(Agent):
    """Agent that acts as an expert on a specific research poster."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        poster_data: Dict[str, Any],
        ollama_service: Optional[OllamaService] = None,
    ):
        super().__init__(agent_id, name)
        self.poster_data = poster_data
        self.ollama_service = ollama_service
        self.agent_mode = os.getenv("AGENT_MODE", "simple")

    def _build_system_prompt(self) -> str:
        """Build the system prompt with poster information."""
        faq_text = ""
        if "faq" in self.poster_data and self.poster_data["faq"]:
            faq_text = "\n\nFrequently Asked Questions:\n"
            for item in self.poster_data["faq"]:
                faq_text += f"Q: {item['question']}\nA: {item['answer']}\n\n"

        return f"""You are a friendly research assistant presenting the poster titled "{self.poster_data['title']}".

Your role:
- You are knowledgeable about this specific research project
- Answer questions clearly and concisely
- Stay focused on this poster's topic
- If asked about other topics, politely redirect to this poster or suggest asking the guide

Poster Information:
Title: {self.poster_data['title']}
Authors: {', '.join(self.poster_data['authors'])}
Tags: {', '.join(self.poster_data['tags'])}

Abstract:
{self.poster_data['abstract']}
{faq_text}

Remember: Be enthusiastic about the research but concise. Keep responses under 3-4 sentences unless more detail is specifically requested.
"""

    def _simple_response(self, message: str) -> str:
        """Generate a simple template-based response (fallback mode)."""
        message_lower = message.lower()

        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return f"Hello! I'm here to tell you about our research on {self.poster_data['title']}. What would you like to know?"

        # About/summary
        if any(word in message_lower for word in ["about", "summary", "what is this", "tell me"]):
            return f"{self.poster_data['abstract'][:200]}... Would you like to know more about a specific aspect?"

        # Authors
        if "author" in message_lower or "who" in message_lower:
            return f"This research was conducted by {', '.join(self.poster_data['authors'])}."

        # Tags/topics
        if any(word in message_lower for word in ["topic", "tag", "area", "field"]):
            return f"This poster covers: {', '.join(self.poster_data['tags'])}."

        # FAQ lookup
        if "faq" in self.poster_data:
            for faq_item in self.poster_data["faq"]:
                if any(word in message_lower for word in faq_item["question"].lower().split()):
                    return faq_item["answer"]

        # Default
        return f"That's an interesting question about {self.poster_data['title']}. Our research focuses on {self.poster_data['abstract'][:150]}..."

    async def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response about the poster."""
        self.add_to_history("user", message)

        # Use Ollama if available and mode is set
        if self.agent_mode == "ollama" and self.ollama_service:
            try:
                system_prompt = self._build_system_prompt()

                # Build conversation messages
                messages = [{"role": "system", "content": system_prompt}]
                messages.extend(self.conversation_history)

                response = await self.ollama_service.chat(messages, temperature=0.7)

                if response and "trouble connecting" not in response:
                    self.add_to_history("assistant", response)
                    return response
                else:
                    # Fallback to simple mode if Ollama fails
                    print("Falling back to simple mode due to Ollama error")
            except Exception as e:
                print(f"Error in Ollama response: {e}")

        # Simple template-based response
        response = self._simple_response(message)
        self.add_to_history("assistant", response)
        return response
