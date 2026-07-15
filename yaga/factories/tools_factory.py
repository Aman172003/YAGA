from __future__ import annotations

from typing import Any


class ToolsFactory:
    def __init__(self, tool_configs: list[dict[str, Any]] | None = None):
        self._tool_configs = tool_configs or []

    def build_tools(self, agent_name: str) -> list[dict[str, Any]]:
        matched_tools = []
        for tool in self._tool_configs:
            tool_name = tool.get("name")
            if tool_name in {agent_name, "default"}:
                matched_tools.append({
                    "name": tool_name,
                    "config": tool.get("config", {}),
                    "kind": tool.get("config", {}).get("kind", "generic"),
                })
        return matched_tools

    async def execute_tool(self, tool_name: str, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        tool_config = next((tool for tool in self._tool_configs if tool.get("name") == tool_name), None)
        if tool_config is None:
            return {"tool": tool_name, "status": "not_found", "input": input_data or {}, "config": {}}

        config = tool_config.get("config", {})
        return {
            "tool": tool_name,
            "status": "ok",
            "input": input_data or {},
            "config": config,
        }
