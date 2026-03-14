"""Mem0 core memory management logic."""
import uuid
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from .embedding import EmbeddingClient, EmbeddingResult
from .llm import LLMClient
from .vector_store import VectorStore, Memory


@dataclass
class SearchResult:
    """Search result."""
    memory: Memory
    score: float


class Mem0Local:
    """Local Mem0 implementation."""
    
    def __init__(
        self,
        embedding_client: EmbeddingClient,
        llm_client: LLMClient,
        vector_store: VectorStore,
    ):
        self.embedding = embedding_client
        self.llm = llm_client
        self.store = vector_store
    
    async def add(
        self,
        content: str,
        user_id: str,
        metadata: Optional[Dict] = None,
    ) -> List[Memory]:
        """Add a new memory from content."""
        # Extract memories using LLM
        extracted = await self.llm.extract_memories(content, user_id)
        
        if not extracted:
            extracted = [content]
        
        memories = []
        for text in extracted:
            # Generate embedding
            embedding_result = await self.embedding.embed(text)
            
            # Create memory
            memory = Memory(
                id=str(uuid.uuid4()),
                content=text,
                embedding=embedding_result.embedding,
                user_id=user_id,
                metadata=metadata or {},
            )
            
            # Store
            self.store.add(memory)
            memories.append(memory)
        
        return memories
    
    async def search(
        self,
        query: str,
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[SearchResult]:
        """Search memories by query."""
        # Embed query
        query_embedding = await self.embedding.embed(query)
        
        # Search vector store
        results = self.store.search(
            query_embedding.embedding,
            user_id=user_id,
            limit=limit,
        )
        
        return [
            SearchResult(memory=memory, score=score)
            for memory, score in results
        ]
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID."""
        return self.store.get(memory_id)
    
    def get_all(self, user_id: Optional[str] = None) -> List[Memory]:
        """Get all memories."""
        return self.store.get_all(user_id)
    
    def update(
        self,
        memory_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Optional[Memory]:
        """Update a memory."""
        memory = self.store.get(memory_id)
        if not memory:
            return None
        
        if content:
            memory.content = content
        if metadata:
            memory.metadata.update(metadata)
        
        from datetime import datetime
        memory.updated_at = datetime.now().isoformat()
        
        self.store.add(memory)
        return memory
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory."""
        return self.store.delete(memory_id)
    
    def delete_all(self, user_id: Optional[str] = None) -> int:
        """Delete all memories."""
        return self.store.delete_all(user_id)
    
    def count(self, user_id: Optional[str] = None) -> int:
        """Count memories."""
        return self.store.count(user_id)