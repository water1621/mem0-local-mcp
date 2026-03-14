"""Configuration management for Mem0 Local MCP Server."""
import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class EmbeddingConfig:
    """Embedding service configuration."""
    api_key: str
    base_url: str
    model: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "EmbeddingConfig":
        return cls(
            api_key=data.get("api_key", os.getenv("EMBEDDING_API_KEY", "")),
            base_url=data.get("base_url", os.getenv("EMBEDDING_BASE_URL", "https://api.openai.com/v1")),
            model=data.get("model", os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")),
        )


@dataclass
class LLMConfig:
    """LLM service configuration."""
    api_key: str
    base_url: str
    model: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "LLMConfig":
        return cls(
            api_key=data.get("api_key", os.getenv("LLM_API_KEY", "")),
            base_url=data.get("base_url", os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")),
            model=data.get("model", os.getenv("LLM_MODEL", "gpt-4o-mini")),
        )


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    provider: str
    persist_path: str
    
    @classmethod
    def from_dict(cls, data: dict) -> "VectorStoreConfig":
        return cls(
            provider=data.get("provider", os.getenv("VECTOR_STORE_PROVIDER", "sqlite")),
            persist_path=data.get("persist_path", os.getenv("VECTOR_STORE_PATH", "./data/memories.db")),
        )


@dataclass
class ServerConfig:
    """Server configuration."""
    log_level: str = "info"
    
    @classmethod
    def from_dict(cls, data: dict) -> "ServerConfig":
        return cls(
            log_level=data.get("log_level", "info"),
        )


@dataclass
class Config:
    """Main configuration."""
    llm: LLMConfig
    embedding: EmbeddingConfig
    vector_store: VectorStoreConfig
    server: ServerConfig = field(default_factory=ServerConfig)
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> "Config":
        """Load configuration from YAML file.
        
        Precedence:
        1. Environment variables (highest priority)
        2. YAML config file
        3. Default values
        """
        if config_path is None:
            # Try default paths
            default_paths = [
                Path.cwd() / "config.yaml",
                Path(__file__).parent / "config.yaml",
                Path.home() / ".mem0-local" / "config.yaml",
            ]
            for path in default_paths:
                if path.exists():
                    config_path = str(path)
                    break
        
        config_data = {}
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config_data = yaml.safe_load(f) or {}
        
        return cls(
            llm=LLMConfig.from_dict(config_data.get("llm", {})),
            embedding=EmbeddingConfig.from_dict(config_data.get("embedding", {})),
            vector_store=VectorStoreConfig.from_dict(config_data.get("vector_store", {})),
            server=ServerConfig.from_dict(config_data.get("server", {})),
        )
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables only (backward compatible)."""
        return cls(
            llm=LLMConfig.from_dict({}),
            embedding=EmbeddingConfig.from_dict({}),
            vector_store=VectorStoreConfig.from_dict({}),
            server=ServerConfig.from_dict({}),
        )
    
    def validate(self) -> list[str]:
        """Validate configuration and return list of errors."""
        errors = []
        
        if not self.llm.api_key or self.llm.api_key == "YOUR_LLM_API_KEY_HERE":
            errors.append("LLM API key is not configured")
        
        if not self.embedding.api_key or self.embedding.api_key == "YOUR_EMBEDDING_API_KEY_HERE":
            errors.append("Embedding API key is not configured")
        
        if self.vector_store.provider not in ("memory", "sqlite"):
            errors.append(f"Invalid vector store provider: {self.vector_store.provider}")
        
        return errors
    
    @classmethod
    def get_config_path(cls) -> Optional[Path]:
        """Get the path to the config file that would be used."""
        default_paths = [
            Path.cwd() / "config.yaml",
            Path(__file__).parent / "config.yaml",
            Path.home() / ".mem0-local" / "config.yaml",
        ]
        for path in default_paths:
            if path.exists():
                return path
        return None