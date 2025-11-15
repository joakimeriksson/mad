"""
Ollama service wrapper for LLM interactions.
"""

import os
from typing import Optional, List, Dict
import httpx


class OllamaService:
    """Service for interacting with Ollama LLM."""

    def __init__(
        self,
        host: Optional[str] = None,
        model: Optional[str] = None,
    ):
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama2")
        self.timeout = 60.0

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using Ollama.

        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt to set context
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            The generated response
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }

                if system_prompt:
                    payload["system"] = system_prompt

                response = await client.post(
                    f"{self.host}/api/generate",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")

        except httpx.HTTPError as e:
            print(f"Error connecting to Ollama: {e}")
            return "I'm having trouble connecting to my knowledge base right now. Please try again later."
        except Exception as e:
            print(f"Unexpected error in Ollama service: {e}")
            return "I encountered an unexpected error. Please try again."

    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        """
        Generate a response using chat format.

        Args:
            messages: List of message dictionaries with 'role' and 'content'
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            The generated response
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": temperature,
                    }
                }

                response = await client.post(
                    f"{self.host}/api/chat",
                    json=payload
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")

        except httpx.HTTPError as e:
            print(f"Error connecting to Ollama: {e}")
            return "I'm having trouble connecting to my knowledge base right now. Please try again later."
        except Exception as e:
            print(f"Unexpected error in Ollama service: {e}")
            return "I encountered an unexpected error. Please try again."

    async def check_connection(self) -> bool:
        """Check if Ollama is available."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                return response.status_code == 200
        except Exception:
            return False
