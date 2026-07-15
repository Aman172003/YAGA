import pytest

from rtkaiagents.factories.mcps_factory import MCPsFactory
from rtkaiagents.factories.tools_factory import ToolsFactory


@pytest.mark.asyncio
async def test_tools_factory_exposes_agent_scoped_tools_and_executes_requests() -> None:
    factory = ToolsFactory([
        {"name": "my_agent", "config": {"kind": "echo"}},
        {"name": "default", "config": {"kind": "echo"}},
    ])

    tools = factory.build_tools("my_agent")
    assert len(tools) == 2
    result = await factory.execute_tool("my_agent", {"question": "hello"})

    assert result["tool"] == "my_agent"
    assert result["status"] == "ok"
    assert result["input"]["question"] == "hello"


def test_mcps_factory_builds_registered_servers() -> None:
    factory = MCPsFactory([
        {"name": "weather", "config": {"url": "http://example.test"}},
    ])

    servers = factory.build_mcps()
    assert servers[0]["name"] == "weather"
    assert servers[0]["config"]["url"] == "http://example.test"
