# Release Notes

## v1.0.0 - Initial Release

### ✨ Features

- **智能记忆管理**: 自动从对话中提取重要信息并存储
- **语义搜索**: 基于向量相似度的智能记忆检索
- **本地存储**: 支持 SQLite 持久化存储，数据完全本地化
- **多提供商支持**: 
  - LLM: OpenAI、阿里云、硅基流动等
  - Embedding: OpenAI、硅基流动、阿里云等
- **灵活配置**: YAML 配置文件 + 环境变量双重支持
- **MCP 协议兼容**: 支持 Claude Desktop、OpenCode 等 MCP 客户端

### 🛠️ MCP Tools

| Tool | Description |
|------|-------------|
| `add_memory` | Add a new memory |
| `search_memories` | Semantic search memories |
| `get_memories` | Get all memories |
| `get_memory` | Get memory by ID |
| `delete_memory` | Delete a memory |
| `delete_all_memories` | Delete all memories |
| `count_memories` | Count stored memories |

### 📦 Installation

```bash
git clone <repo-url>
cd mem0-local-mcp
pip install -r requirements.txt
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys
python server.py
```

### 🔧 Configuration

See `config.example.yaml` for configuration template.

---

## Upcoming Features

- [ ] Qdrant/Chroma vector store support
- [ ] Memory expiration and cleanup
- [ ] Memory categories and tags
- [ ] Web UI for memory management
- [ ] Export/Import memories
- [ ] Memory deduplication