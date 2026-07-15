from __future__ import annotations

from pathlib import Path
from typing import Any

from yaga.exceptions import AgentNotFoundError, GraphNotFoundError
from yaga.factories.agents_factory import AgentsFactory
from yaga.factories.graphs_factory import GraphsFactory
from yaga.factories.mcps_factory import MCPsFactory
from yaga.factories.models_factory import ModelsFactory
from yaga.factories.persistence_factory import PersistenceFactory
from yaga.factories.tools_factory import ToolsFactory
from yaga.models import AgentConfig, GraphConfig, UnifiedConfig
from yaga.models.agent_models import MCPConfig, ToolConfig
from yaga.logging import get_logger, log_event
from yaga.tracing import get_trace_id, trace_event, trace_scope
from yaga.utils import load_yaml_file, merge_config_dicts

logger = get_logger(__name__)


class AgentService:
    def __init__(self, config: UnifiedConfig):
        self._config = config
        agents = config.get_agents_config()
        graphs = config.get_graphs_config()
        self._models_factory = ModelsFactory(agents)
        self._tools_factory = ToolsFactory([tool.model_dump() for tool in config.tools])
        self._mcps_factory = MCPsFactory([mcp.model_dump() for mcp in config.mcps])
        self._agents_factory = AgentsFactory(agents, models_factory=self._models_factory, tools_factory=self._tools_factory, mcps_factory=self._mcps_factory)
        self._graphs_factory = GraphsFactory(graphs)
        self._persistence_factory = PersistenceFactory(config.persistence.model_dump() if config.persistence else None)

    @classmethod
    async def from_configs(cls, config_paths: str | list[str], *args: Any, **kwargs: Any) -> "AgentService":
        paths = [config_paths] if isinstance(config_paths, str) else list(config_paths)
        merged: dict[str, Any] = {}
        for path in paths:
            data = load_yaml_file(path)
            merged = merge_config_dicts(merged, data)

        unified_config = UnifiedConfig(**merged)
        return cls(unified_config)

    async def run_agent(self, agent_name: str, input_data: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        agent_cfg = next((agent for agent in self._config.agents if agent.name == agent_name), None)
        if agent_cfg is None:
            raise AgentNotFoundError(f"Agent '{agent_name}' not found")
        request_config = config or {}
        trace_id = request_config.get("trace_id") or request_config.get("configurable", {}).get("trace_id") if isinstance(request_config.get("configurable"), dict) else None
        with trace_scope(trace_id) as active_trace_id:
            trace_event("agent.run.start", agent=agent_name, input=input_data)
            agent = await self._agents_factory.create_agent(agent_name)
            payload = {
                "messages": [{"role": "user", "content": input_data.get("question") or str(input_data)}],
                "context": {
                    "input": input_data,
                    "agent": agent_name,
                    "trace_id": active_trace_id,
                },
            }
            result = await agent.ainvoke(payload, config=config)
            trace_event("agent.run.complete", agent=agent_name, result=result)
            return {
                "agent": agent_name,
                "result": result,
                "metadata": {
                    "thread_id": request_config.get("configurable", {}).get("thread_id") if request_config.get("configurable") else None,
                    "trace_id": active_trace_id,
                },
            }

    async def stream_agent(self, agent_name: str, input_data: dict[str, Any], config: dict[str, Any] | None = None):
        result = await self.run_agent(agent_name, input_data, config=config)
        yield {"type": "done", "content": result}

    async def run_graph(self, graph_name: str, input_data: dict[str, Any], context: dict[str, Any] | None = None, config: dict[str, Any] | None = None) -> dict[str, Any]:
        graph_cfg = next((graph for graph in self._config.graphs if graph.name == graph_name), None)
        if graph_cfg is None:
            raise GraphNotFoundError(f"Graph '{graph_name}' not found")
        request_config = config or {}
        trace_id = request_config.get("trace_id") or request_config.get("configurable", {}).get("trace_id") if isinstance(request_config.get("configurable"), dict) else None
        with trace_scope(trace_id) as active_trace_id:
            trace_event("graph.run.start", graph=graph_name, input=input_data)
            compiled_graph = await self._graphs_factory.create_graph(graph_name)
            state: dict[str, Any] = {
                "input": input_data,
                "intermediate_results": {},
                "feature_flags": {},
                "errors": [],
            }
            result = await compiled_graph.ainvoke(state)
            trace_event("graph.run.complete", graph=graph_name, result=result)
            return {
                "graph": graph_name,
                "result": result,
                "context": context or {},
                "metadata": {"trace_id": active_trace_id},
            }

    async def stream_graph(self, graph_name: str, input_data: dict[str, Any], context: dict[str, Any] | None = None, config: dict[str, Any] | None = None):
        result = await self.run_graph(graph_name, input_data, context=context, config=config)
        yield {"type": "done", "content": result}


AIAgentService = AgentService
