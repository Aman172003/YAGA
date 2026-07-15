from __future__ import annotations

from typing import Any


class MCPsFactory:
    def __init__(self, mcps: list[dict[str, Any]] | None = None):
        self._mcps = mcps or []

    def build_mcps(self) -> list[dict[str, Any]]:
        return [dict(mcp) for mcp in self._mcps]

    def get_mcp(self, name: str) -> dict[str, Any] | None:
        for mcp in self._mcps:
            if mcp.get("name") == name:
                return dict(mcp)
        return None
