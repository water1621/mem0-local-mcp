"""Session memory utilities for Mem0 Local MCP."""
import json
from datetime import datetime
from typing import List, Dict, Optional


def create_session_summary(
    project_name: str,
    key_decisions: List[str],
    code_patterns: List[str],
    pending_tasks: List[str],
    next_steps: str,
    context_files: Optional[List[str]] = None,
) -> str:
    """
    Create a structured session summary for memory storage.
    
    Usage:
        summary = create_session_summary(
            project_name="My App",
            key_decisions=["Use PostgreSQL", "React + TypeScript"],
            code_patterns=["Repository pattern", "Error boundary"],
            pending_tasks=["Add auth", "Write tests"],
            next_steps="Continue with auth implementation",
        )
        # Then store via Mem0: add_memory(summary)
    """
    summary = {
        "type": "session_summary",
        "project": project_name,
        "timestamp": datetime.now().isoformat(),
        "key_decisions": key_decisions,
        "code_patterns": code_patterns,
        "pending_tasks": pending_tasks,
        "next_steps": next_steps,
        "context_files": context_files or [],
    }
    
    return json.dumps(summary, ensure_ascii=False, indent=2)


def format_for_mem0(
    project_name: str,
    key_decisions: List[str],
    code_patterns: List[str],
    pending_tasks: List[str],
    next_steps: str,
) -> str:
    """
    Format session summary as natural language for Mem0 storage.
    
    This format is better for semantic search.
    """
    lines = [
        f"[Session Summary - {project_name}]",
        f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "Key Decisions:",
    ]
    
    for i, decision in enumerate(key_decisions, 1):
        lines.append(f"  {i}. {decision}")
    
    lines.append("")
    lines.append("Code Patterns:")
    for i, pattern in enumerate(code_patterns, 1):
        lines.append(f"  {i}. {pattern}")
    
    lines.append("")
    lines.append("Pending Tasks:")
    for i, task in enumerate(pending_tasks, 1):
        lines.append(f"  {i}. {task}")
    
    lines.append("")
    lines.append(f"Next Steps: {next_steps}")
    
    return "\n".join(lines)


# Example usage template
USAGE_TEMPLATE = """
When your context is getting full, ask the AI:

"Please summarize this session and save to memory:
- Key decisions made
- Code patterns established
- Pending tasks
- Where to continue next time"

Then the AI will use Mem0 to store the summary.
"""