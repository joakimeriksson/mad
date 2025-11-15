"""
Guide Agent - Helps visitors navigate the open house and find posters.
"""

from typing import Optional, Dict, Any, List
from .base import Agent
from .ollama_service import OllamaService
import os


class GuideAgent(Agent):
    """Agent that helps visitors navigate and find interesting posters."""

    def __init__(
        self,
        agent_id: str,
        name: str,
        all_posters: List[Dict[str, Any]],
        ollama_service: Optional[OllamaService] = None,
    ):
        super().__init__(agent_id, name)
        self.all_posters = all_posters
        self.ollama_service = ollama_service
        self.agent_mode = os.getenv("AGENT_MODE", "simple")

    def _build_system_prompt(self) -> str:
        """Build the system prompt with information about all posters."""
        poster_summaries = "\n\n".join([
            f"Poster {i+1}: {poster['title']}\n"
            f"  Authors: {', '.join(poster['authors'])}\n"
            f"  Location: {poster.get('room', 'unknown')} - {poster.get('booth_id', 'unknown')}\n"
            f"  Topics: {', '.join(poster['tags'])}\n"
            f"  Summary: {poster['abstract'][:150]}..."
            for i, poster in enumerate(self.all_posters)
        ])

        return f"""You are a friendly guide at the RISE Computer Science open house.

Your role:
- Help visitors find posters and demos based on their interests
- Provide directions to specific rooms and booths
- Recommend posters based on topics the visitor is interested in
- Give a warm, welcoming experience

Available Posters:
{poster_summaries}

Room Layout:
- Corridor: Main hallway with booths
- Room 1: First exhibition room
- Room 2: Second exhibition room

Remember: Be concise and helpful. When recommending posters, mention the location (room and booth number).
"""

    def _find_posters_by_tag(self, query: str) -> List[Dict[str, Any]]:
        """Find posters matching tags in the query."""
        query_lower = query.lower()
        matching_posters = []

        for poster in self.all_posters:
            # Check if any tag matches words in the query
            for tag in poster['tags']:
                if tag.lower() in query_lower or any(
                    word in tag.lower() for word in query_lower.split()
                ):
                    matching_posters.append(poster)
                    break

        return matching_posters

    def _simple_response(self, message: str) -> str:
        """Generate a simple template-based response (fallback mode)."""
        message_lower = message.lower()

        # Greeting
        if any(word in message_lower for word in ["hello", "hi", "hey"]):
            return "Welcome to the RISE Computer Science open house! I'm your guide. I can help you find posters based on your interests or give you directions. What topics interest you?"

        # List all posters
        if any(phrase in message_lower for phrase in ["what posters", "show me all", "list posters", "what do you have"]):
            poster_list = "\n".join([
                f"- {poster['title']} ({poster.get('room', 'unknown')}, {poster.get('booth_id', 'unknown')})"
                for poster in self.all_posters
            ])
            return f"We have these posters:\n{poster_list}\n\nWould you like to know more about any specific topic?"

        # Find posters by topic
        matching = self._find_posters_by_tag(message)
        if matching:
            if len(matching) == 1:
                poster = matching[0]
                return f"For {', '.join(poster['tags'])}, I recommend '{poster['title']}' by {', '.join(poster['authors'])}. You'll find it in {poster.get('room', 'the building')} at {poster.get('booth_id', 'a booth')}. {poster['abstract'][:100]}..."
            else:
                recommendations = "\n".join([
                    f"- {p['title']} ({p.get('room', 'unknown')}, {p.get('booth_id', 'unknown')})"
                    for p in matching[:3]
                ])
                return f"I found {len(matching)} posters related to your interest:\n{recommendations}\n\nWould you like details about any of these?"

        # Directions
        if any(word in message_lower for word in ["where", "location", "find", "direction"]):
            return "The exhibition has three areas: the main corridor with several booths, and two side rooms (Room 1 and Room 2). Which topic are you looking for?"

        # Default
        return "I can help you find posters on topics like AI, robotics, security, healthcare, and sustainability. What interests you?"

    async def respond(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a response to help the visitor navigate."""
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
