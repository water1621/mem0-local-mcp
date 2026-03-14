"""LLM client for Alibaba Cloud Coding Plan API."""
import httpx
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class Message:
    """Chat message."""
    role: str
    content: str


class LLMClient:
    """Client for LLM API (Alibaba Cloud Coding Plan)."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://coding.dashscope.aliyuncs.com/apps/anthropic/v1",
        model: str = "qwen3-coder-plus",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=120.0)
    
    async def chat(
        self,
        messages: List[Message],
        system: Optional[str] = None,
        max_tokens: int = 1024,
    ) -> str:
        """Send a chat completion request."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        
        for msg in messages:
            formatted_messages.append({"role": msg.role, "content": msg.content})
        
        payload = {
            "model": self.model,
            "messages": formatted_messages,
            "max_tokens": max_tokens,
        }
        
        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]["content"]
    
    async def extract_memories(self, text: str, user_id: str) -> List[str]:
        """Extract memories from text using LLM."""
        system_prompt = """You are a memory extraction assistant. Your task is to extract important facts, preferences, and information from the user's messages that should be remembered for future conversations.

Extract concise, factual statements that would be useful to remember. Each memory should be a single, clear statement.

Return the memories as a JSON array of strings. If no important information is found, return an empty array.

Example:
Input: "I'm working on a React project and I prefer using TypeScript over JavaScript"
Output: ["User is working on a React project", "User prefers TypeScript over JavaScript"]"""

        try:
            result = await self.chat(
                messages=[Message(role="user", content=f"Extract memories from: {text}")],
                system=system_prompt,
                max_tokens=512,
            )
            
            # Parse JSON array from response
            import json
            # Try to find JSON array in response
            start = result.find("[")
            end = result.rfind("]") + 1
            if start != -1 and end > start:
                memories = json.loads(result[start:end])
                return memories if isinstance(memories, list) else []
            return []
        except Exception:
            return [text]  # Fallback: store the original text
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()