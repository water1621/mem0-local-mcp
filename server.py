"""Mem0 Local MCP Server - Entry point."""
import asyncio
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from config import Config
from src.embedding import EmbeddingClient
from src.llm import LLMClient
from src.vector_store import VectorStore
from src.memory import Mem0Local

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("mem0-local")

# Create MCP server
server = Server("mem0-local")

# Global instances
mem0: Optional[Mem0Local] = None


def get_tools() -> list[Tool]:
    """Define available MCP tools."""
    return [
        Tool(
            name="add_memory",
            description="Add a new memory. The content will be processed to extract and store important information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content to remember",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'default')",
                        "default": "default",
                    },
                    "metadata": {
                        "type": "object",
                        "description": "Optional metadata to attach to the memory",
                    },
                },
                "required": ["content"],
            },
        ),
        Tool(
            name="search_memories",
            description="Search memories using semantic search. Returns relevant memories with similarity scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query",
                    },
                    "user_id": {
                        "type": "string",
                        "description": "User identifier to filter memories (optional)",
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10,
                    },
                },
                "required": ["query"],
            },
        ),
        Tool(
            name="get_memories",
            description="Get all memories for a user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (default: 'default')",
                        "default": "default",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="get_memory",
            description="Get a specific memory by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "The memory ID",
                    },
                },
                "required": ["memory_id"],
            },
        ),
        Tool(
            name="delete_memory",
            description="Delete a specific memory by ID.",
            inputSchema={
                "type": "object",
                "properties": {
                    "memory_id": {
                        "type": "string",
                        "description": "The memory ID to delete",
                    },
                },
                "required": ["memory_id"],
            },
        ),
        Tool(
            name="delete_all_memories",
            description="Delete all memories for a user.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (deletes all if not specified)",
                    },
                },
                "required": [],
            },
        ),
        Tool(
            name="count_memories",
            description="Count the number of stored memories.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {
                        "type": "string",
                        "description": "User identifier (counts all if not specified)",
                    },
                },
                "required": [],
            },
        ),
    ]


@server.list_tools()
async def list_tools() -> list[Tool]:
    """Return available tools."""
    return get_tools()


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """Handle tool calls."""
    global mem0
    
    if mem0 is None:
        return [TextContent(type="text", text=json.dumps({"error": "Server not initialized"}, indent=2))]
    
    try:
        if name == "add_memory":
            content = arguments["content"]
            user_id = arguments.get("user_id", "default")
            metadata = arguments.get("metadata")
            
            memories = await mem0.add(content, user_id, metadata)
            
            result = {
                "success": True,
                "added_count": len(memories),
                "memories": [
                    {
                        "id": m.id,
                        "content": m.content,
                        "created_at": m.created_at,
                    }
                    for m in memories
                ],
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "search_memories":
            query = arguments["query"]
            user_id = arguments.get("user_id")
            limit = arguments.get("limit", 10)
            
            results = await mem0.search(query, user_id, limit)
            
            result = {
                "success": True,
                "count": len(results),
                "results": [
                    {
                        "id": r.memory.id,
                        "content": r.memory.content,
                        "score": round(r.score, 4),
                        "created_at": r.memory.created_at,
                    }
                    for r in results
                ],
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "get_memories":
            user_id = arguments.get("user_id", "default")
            
            memories = mem0.get_all(user_id)
            
            result = {
                "success": True,
                "count": len(memories),
                "memories": [
                    {
                        "id": m.id,
                        "content": m.content,
                        "created_at": m.created_at,
                        "metadata": m.metadata,
                    }
                    for m in memories
                ],
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "get_memory":
            memory_id = arguments["memory_id"]
            
            memory = mem0.get(memory_id)
            
            if memory:
                result = {
                    "success": True,
                    "memory": {
                        "id": memory.id,
                        "content": memory.content,
                        "user_id": memory.user_id,
                        "created_at": memory.created_at,
                        "updated_at": memory.updated_at,
                        "metadata": memory.metadata,
                    },
                }
            else:
                result = {
                    "success": False,
                    "error": f"Memory not found: {memory_id}",
                }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "delete_memory":
            memory_id = arguments["memory_id"]
            
            deleted = mem0.delete(memory_id)
            
            result = {
                "success": deleted,
                "message": f"Memory {memory_id} deleted" if deleted else f"Memory not found: {memory_id}",
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "delete_all_memories":
            user_id = arguments.get("user_id")
            
            count = mem0.delete_all(user_id)
            
            result = {
                "success": True,
                "deleted_count": count,
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        elif name == "count_memories":
            user_id = arguments.get("user_id")
            
            count = mem0.count(user_id)
            
            result = {
                "success": True,
                "count": count,
            }
            return [TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
        
        else:
            return [TextContent(type="text", text=json.dumps({"error": f"Unknown tool: {name}"}, indent=2))]
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {e}")
        return [TextContent(type="text", text=json.dumps({"error": str(e)}, indent=2))]


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from YAML file or environment variables."""
    # Try YAML first, fall back to env vars
    config = Config.from_yaml(config_path)
    
    # Validate
    errors = config.validate()
    if errors:
        config_file = Config.get_config_path()
        if config_file:
            logger.warning(f"Configuration issues in {config_file}:")
        else:
            logger.warning("Configuration issues (no config.yaml found):")
        for error in errors:
            logger.warning(f"  - {error}")
        logger.warning("Using environment variables as fallback...")
        
        # Fall back to environment variables
        config = Config.from_env()
        errors = config.validate()
        if errors:
            logger.error("Configuration is incomplete:")
            for error in errors:
                logger.error(f"  - {error}")
            logger.error("Please set up config.yaml or environment variables.")
            sys.exit(1)
    
    return config


async def main():
    """Main entry point."""
    global mem0
    
    # Get config path from command line or environment
    config_path = None
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    elif "MEM0_CONFIG_PATH" in os.environ:
        config_path = os.environ["MEM0_CONFIG_PATH"]
    
    # Load configuration
    config = load_config(config_path)
    
    # Set log level
    logging.getLogger("mem0-local").setLevel(getattr(logging, config.server.log_level.upper()))
    
    logger.info(f"Initializing Mem0 Local MCP Server...")
    logger.info(f"LLM: {config.llm.model} @ {config.llm.base_url}")
    logger.info(f"Embedding: {config.embedding.model} @ {config.embedding.base_url}")
    logger.info(f"Vector Store: {config.vector_store.provider}")
    
    # Initialize clients
    embedding_client = EmbeddingClient(
        api_key=config.embedding.api_key,
        base_url=config.embedding.base_url,
        model=config.embedding.model,
    )
    
    llm_client = LLMClient(
        api_key=config.llm.api_key,
        base_url=config.llm.base_url,
        model=config.llm.model,
    )
    
    vector_store = VectorStore(
        persist_path=config.vector_store.persist_path,
    )
    
    # Initialize Mem0
    mem0 = Mem0Local(
        embedding_client=embedding_client,
        llm_client=llm_client,
        vector_store=vector_store,
    )
    
    logger.info("Server initialized successfully")
    
    # Run MCP server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())