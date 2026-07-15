from __future__ import annotations

from typing import Any

from yaga.factories.mcps_factory import MCPsFactory
from yaga.factories.models_factory import ModelsFactory, RuntimeModel
from yaga.factories.tools_factory import ToolsFactory
from yaga.models import AgentConfig
from yaga.utils import render_prompt


class RuntimeAgent:
    def __init__(self, name: str, config: AgentConfig, model_provider: RuntimeModel | None = None, tools_factory: ToolsFactory | None = None, mcps_factory: MCPsFactory | None = None):
        self.name = name
        self.config = config
        self.model_provider = model_provider
        self.tools_factory = tools_factory
        self.mcps_factory = mcps_factory

    async def ainvoke(self, payload: dict[str, Any], config: dict[str, Any] | None = None) -> dict[str, Any]:
        prompt_cfg = self.config.prompt_provider.inline if self.config.prompt_provider else None
        system_prompt = prompt_cfg.system_prompt if prompt_cfg else None
        user_prompt = prompt_cfg.user_prompt if prompt_cfg else None
        context = payload.get("context", {})
        rendered_system = render_prompt(system_prompt, context)
        rendered_user = render_prompt(user_prompt, context)
        model_result = None
        if self.model_provider is not None:
            model_result = await self.model_provider.ainvoke(payload)

        tool_results = []
        tool_calls = payload.get("tool_calls") or []
        if self.tools_factory and tool_calls:
            for tool_call in tool_calls:
                tool_name = tool_call.get("name") if isinstance(tool_call, dict) else None
                tool_input = tool_call.get("input") if isinstance(tool_call, dict) else None
                if tool_name:
                    tool_results.append(await self.tools_factory.execute_tool(tool_name, tool_input or {}))

        return {
            "agent": self.name,
            "system_prompt": rendered_system,
            "user_prompt": rendered_user,
            "payload": payload,
            "config": config,
            "model_result": model_result,
            "tools": self.tools_factory.build_tools(self.name) if self.tools_factory else [],
            "mcp_servers": self.mcps_factory.build_mcps() if self.mcps_factory else [],
            "tool_results": tool_results,
        }


SimpleAgent = RuntimeAgent


class AgentsFactory:
    def __init__(self, config: list[AgentConfig], models_factory: ModelsFactory | None = None, tools_factory: ToolsFactory | None = None, mcps_factory: MCPsFactory | None = None):
        self._config = {agent.name: agent for agent in config}
        self._agents_cache: dict[str, RuntimeAgent] = {}
        self._models_factory = models_factory or ModelsFactory(list(self._config.values()))
        self._tools_factory = tools_factory
        self._mcps_factory = mcps_factory

    async def create_agent(self, agent_name: str) -> RuntimeAgent:
        if agent_name in self._agents_cache:
            return self._agents_cache[agent_name]
        agent_cfg = self._config.get(agent_name)
        if not agent_cfg:
            raise KeyError(f"Agent '{agent_name}' not found")
        model_provider = self._models_factory.get_model(agent_cfg)
        agent = RuntimeAgent(name=agent_name, config=agent_cfg, model_provider=model_provider, tools_factory=self._tools_factory, mcps_factory=self._mcps_factory)
        self._agents_cache[agent_name] = agent
        return agent
