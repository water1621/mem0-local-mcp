# Mem0 Local MCP Server

[![MCP](https://img.shields.io/badge/MCP-Compatible-blue)](https://modelcontextprotocol.io/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-green)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

🧠 **AI 记忆层 MCP 服务器** - 让你的 AI 助手拥有长期记忆能力。

自托管、完全本地控制、支持多种 LLM 和 Embedding 提供商。

---

## ✨ 特性

- 🧠 **智能记忆管理** - 自动从对话中提取重要信息
- 🔍 **语义搜索** - 基于向量相似度的智能检索
- 💾 **本地存储** - 数据完全本地化，隐私可控
- 🔧 **灵活配置** - 支持 YAML 配置文件，易于分享
- 🔄 **多提供商支持** - OpenAI、阿里云、硅基流动等

---

## 📦 安装

### 方式一：直接使用

```bash
# 克隆或下载项目
git clone <repository-url>
cd mem0-local-mcp

# 安装依赖
pip install -r requirements.txt

# 复制配置模板
cp config.example.yaml config.yaml

# 编辑配置文件，填入你的 API Key
# Windows: notepad config.yaml
# macOS/Linux: nano config.yaml
```

### 方式二：pip 安装（即将支持）

```bash
pip install mem0-local-mcp
```

---

## ⚙️ 配置

### 配置文件结构 (`config.yaml`)

```yaml
# LLM 配置 - 用于从对话中提取记忆
llm:
  api_key: "YOUR_LLM_API_KEY"
  base_url: "https://api.openai.com/v1"
  model: "gpt-4o-mini"

# Embedding 配置 - 用于向量化记忆
embedding:
  api_key: "YOUR_EMBEDDING_API_KEY"
  base_url: "https://api.openai.com/v1"
  model: "text-embedding-3-small"

# 向量存储配置
vector_store:
  provider: "sqlite"  # 或 "memory"
  persist_path: "./data/memories.db"
```

### 支持的提供商

#### LLM 提供商

| 提供商 | base_url | 推荐模型 |
|--------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | gpt-4o-mini, gpt-4o |
| 阿里云 | `https://coding.dashscope.aliyuncs.com/apps/anthropic/v1` | qwen3-coder-plus |
| 硅基流动 | `https://api.siliconflow.cn/v1` | Qwen/Qwen3-8B |

#### Embedding 提供商

| 提供商 | base_url | 推荐模型 |
|--------|----------|----------|
| OpenAI | `https://api.openai.com/v1` | text-embedding-3-small |
| 硅基流动 | `https://api.siliconflow.cn/v1` | BAAI/bge-m3 |
| 阿里云 | `https://dashscope.aliyuncs.com/compatible-mode/v1` | text-embedding-v3 |

### 配置优先级

1. **环境变量**（最高优先级）
2. **YAML 配置文件**
3. **默认值**

支持的环境变量：

```bash
# LLM
LLM_API_KEY=xxx
LLM_BASE_URL=xxx
LLM_MODEL=xxx

# Embedding
EMBEDDING_API_KEY=xxx
EMBEDDING_BASE_URL=xxx
EMBEDDING_MODEL=xxx

# Vector Store
VECTOR_STORE_PROVIDER=sqlite
VECTOR_STORE_PATH=./data/memories.db
```

---

## 🚀 使用

### 本地测试

```bash
python server.py
```

### 配置 OpenCode

编辑 `~/.config/opencode/opencode.json`：

```json
{
  "mcp": {
    "mem0-local": {
      "type": "local",
      "command": ["python", "/path/to/mem0-local-mcp/server.py"],
      "enabled": true
    }
  }
}
```

或使用环境变量：

```json
{
  "mcp": {
    "mem0-local": {
      "type": "local",
      "command": ["python", "/path/to/mem0-local-mcp/server.py"],
      "environment": {
        "LLM_API_KEY": "your-key",
        "LLM_MODEL": "gpt-4o-mini",
        "EMBEDDING_API_KEY": "your-key",
        "EMBEDDING_MODEL": "text-embedding-3-small"
      },
      "enabled": true
    }
  }
}
```

### 配置 Claude Desktop

编辑 `~/Library/Application Support/Claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "mem0-local": {
      "command": "python",
      "args": ["/path/to/mem0-local-mcp/server.py"]
    }
  }
}
```

---

## 🛠️ MCP 工具

| 工具 | 描述 | 示例用法 |
|------|------|----------|
| `add_memory` | 添加新记忆 | "记住我喜欢用 TypeScript" |
| `search_memories` | 语义搜索记忆 | "搜索我之前的数据库偏好" |
| `get_memories` | 获取所有记忆 | 查看已存储的所有记忆 |
| `get_memory` | 获取指定记忆 | 按 ID 获取记忆详情 |
| `delete_memory` | 删除指定记忆 | 删除某条记忆 |
| `delete_all_memories` | 删除所有记忆 | 清空记忆库 |
| `count_memories` | 统计记忆数量 | 查看已存储多少条记忆 |

---

## 📁 项目结构

```
mem0-local-mcp/
├── server.py              # MCP 服务器入口
├── config.py              # 配置管理
├── config.example.yaml    # 配置模板
├── requirements.txt       # Python 依赖
├── README.md              # 文档
├── src/
│   ├── __init__.py
│   ├── embedding.py       # Embedding 客户端
│   ├── llm.py             # LLM 客户端
│   ├── memory.py          # 记忆管理核心
│   └── vector_store.py    # 向量存储
└── data/
    └── memories.db        # SQLite 数据库（自动创建）
```

---

## 🔐 安全建议

1. **不要提交 `config.yaml`** - 已在 `.gitignore` 中
2. **使用环境变量** - 更安全的配置方式
3. **定期备份** - `data/memories.db` 包含所有记忆
4. **API Key 保护** - 不要在代码中硬编码

---

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📮 联系方式

如有问题，请提交 GitHub Issue。