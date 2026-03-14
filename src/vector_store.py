"""Vector store implementation for Mem0."""
import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import os


@dataclass
class Memory:
    """A stored memory."""
    id: str
    content: str
    embedding: List[float]
    user_id: str
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())


class VectorStore:
    """In-memory vector store with optional persistence."""
    
    def __init__(self, persist_path: Optional[str] = None):
        self.memories: Dict[str, Memory] = {}
        self.persist_path = persist_path
        self._load()
    
    def _load(self):
        """Load memories from disk."""
        if self.persist_path and os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        memory = Memory(**item)
                        self.memories[memory.id] = memory
            except Exception:
                pass
    
    def _save(self):
        """Save memories to disk."""
        if self.persist_path:
            os.makedirs(os.path.dirname(self.persist_path), exist_ok=True)
            try:
                data = [
                    {
                        "id": m.id,
                        "content": m.content,
                        "embedding": m.embedding,
                        "user_id": m.user_id,
                        "metadata": m.metadata,
                        "created_at": m.created_at,
                        "updated_at": m.updated_at,
                    }
                    for m in self.memories.values()
                ]
                with open(self.persist_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
    
    def add(self, memory: Memory) -> Memory:
        """Add a memory to the store."""
        self.memories[memory.id] = memory
        self._save()
        return memory
    
    def get(self, memory_id: str) -> Optional[Memory]:
        """Get a memory by ID."""
        return self.memories.get(memory_id)
    
    def get_all(self, user_id: Optional[str] = None) -> List[Memory]:
        """Get all memories, optionally filtered by user."""
        if user_id:
            return [m for m in self.memories.values() if m.user_id == user_id]
        return list(self.memories.values())
    
    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        if memory_id in self.memories:
            del self.memories[memory_id]
            self._save()
            return True
        return False
    
    def delete_all(self, user_id: Optional[str] = None) -> int:
        """Delete all memories, optionally filtered by user."""
        if user_id:
            to_delete = [m_id for m_id, m in self.memories.items() if m.user_id == user_id]
            for m_id in to_delete:
                del self.memories[m_id]
            self._save()
            return len(to_delete)
        else:
            count = len(self.memories)
            self.memories.clear()
            self._save()
            return count
    
    def search(
        self,
        query_embedding: List[float],
        user_id: Optional[str] = None,
        limit: int = 10,
    ) -> List[Tuple[Memory, float]]:
        """Search for similar memories using cosine similarity."""
        query_vec = np.array(query_embedding)
        query_norm = np.linalg.norm(query_vec)
        
        if query_norm == 0:
            return []
        
        memories = self.get_all(user_id)
        similarities = []
        
        for memory in memories:
            mem_vec = np.array(memory.embedding)
            mem_norm = np.linalg.norm(mem_vec)
            
            if mem_norm == 0:
                continue
            
            similarity = np.dot(query_vec, mem_vec) / (query_norm * mem_norm)
            similarities.append((memory, float(similarity)))
        
        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:limit]
    
    def count(self, user_id: Optional[str] = None) -> int:
        """Count memories."""
        if user_id:
            return len([m for m in self.memories.values() if m.user_id == user_id])
        return len(self.memories)