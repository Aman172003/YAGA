import asyncio

import pytest

from yaga import AgentService, AIAgentService
from yaga.service import AIAgentService as LegacyAIAgentService


def test_service_exports_use_canonical_and_legacy_names() -> None:
    assert AgentService is AIAgentService
    assert AIAgentService is LegacyAIAgentService


@pytest.mark.asyncio
async def test_run_agent_and_graph() -> None:
    service = await AIAgentService.from_configs(["config/agents.yaml", "config/graphs.yaml", "config/mcps.yaml"])
    agent_result = await service.run_agent("my_agent", {"question": "What is 2+2?"})
    assert "my_agent" in agent_result["agent"]
    graph_result = await service.run_graph("my_graph", {"question": "What is 2+2?"})
    assert graph_result["graph"] == "my_graph"
