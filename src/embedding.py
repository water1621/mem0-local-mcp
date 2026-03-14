"""Embedding client for SiliconFlow API."""
import httpx
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class EmbeddingResult:
    """Embedding result."""
    embedding: List[float]
    tokens: int


class EmbeddingClient:
    """Client for SiliconFlow Embedding API."""
    
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.siliconflow.cn/v1",
        model: str = "BAAI/bge-m3",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.AsyncClient(timeout=60.0)
    
    async def embed(self, text: str) -> EmbeddingResult:
        """Embed a single text."""
        results = await self.embed_batch([text])
        return results[0]
    
    async def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Embed multiple texts."""
        url = f"{self.base_url}/embeddings"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "input": texts,
            "encoding_format": "float",
        }
        
        response = await self._client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        
        results = []
        for item in data["data"]:
            results.append(EmbeddingResult(
                embedding=item["embedding"],
                tokens=data.get("usage", {}).get("total_tokens", 0) // len(texts),
            ))
        
        return results
    
    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()