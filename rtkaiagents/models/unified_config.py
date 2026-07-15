from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from .agent_models import (
    AgentConfig,
    GraphConfig,
    MCPConfig,
    MiddlewareConfig,
    PersistenceConfig,
    SharedModelConfig,
    ToolConfig,
)


class UnifiedConfig(BaseModel):
    agents: List[AgentConfig] = Field(default_factory=list)
    graphs: List[GraphConfig] = Field(default_factory=list)
    mcps: List[MCPConfig] = Field(default_factory=list)
    tools: List[ToolConfig] = Field(default_factory=list)
    models: List[SharedModelConfig] = Field(default_factory=list)
    persistence: Optional[PersistenceConfig] = None
    middlewares: List[MiddlewareConfig] = Field(default_factory=list)

    def get_agents_config(self) -> List[AgentConfig]:
        return self.agents or []

    def get_graphs_config(self) -> List[GraphConfig]:
        return self.graphs or []

    def get_mcps_config(self) -> List[MCPConfig]:
        return self.mcps or []
