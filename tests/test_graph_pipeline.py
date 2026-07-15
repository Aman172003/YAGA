import pytest

from yaga.factories.graphs_factory import GraphsFactory
from yaga.models.agent_models import EdgeConfig, GraphConfig, NodeConfig


@pytest.mark.asyncio
async def test_multi_step_graph_and_end_terminal_execution() -> None:
    graph_cfg = GraphConfig(
        name="pipeline_graph",
        nodes=[
            NodeConfig(name="start"),
            NodeConfig(name="middle"),
            NodeConfig(name="finish"),
        ],
        edges=[
            EdgeConfig(source="start", target="middle"),
            EdgeConfig(source="middle", target="finish"),
            EdgeConfig(source="finish", target="__end__"),
        ],
        start_node="start",
    )

    factory = GraphsFactory([graph_cfg])
    compiled_graph = await factory.create_graph("pipeline_graph")
    result = await compiled_graph.ainvoke({"input": {"question": "hi"}, "intermediate_results": {}, "feature_flags": {}, "errors": []})

    assert result["intermediate_results"]["start"]["status"] == "completed"
    assert result["intermediate_results"]["middle"]["status"] == "completed"
    assert result["intermediate_results"]["finish"]["status"] == "completed"
    assert result["intermediate_results"]["finish"].get("terminal") is True
