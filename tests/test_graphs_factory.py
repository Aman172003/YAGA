import asyncio

import pytest

from rtkaiagents.factories.graphs_factory import GraphsFactory
from rtkaiagents.models.agent_models import EdgeCondition, EdgeConfig, GraphConfig, NodeConfig


@pytest.mark.asyncio
async def test_conditional_edges_select_branch() -> None:
    graph_cfg = GraphConfig(
        name="conditional_graph",
        nodes=[
            NodeConfig(name="start"),
            NodeConfig(name="branch_a"),
            NodeConfig(name="branch_b"),
        ],
        edges=[
            EdgeConfig(source="start", target="branch_a", type="conditional", conditions=[EdgeCondition(condition='input.question == "hi"', target='branch_a')], default_target='branch_b'),
        ],
        start_node="start",
    )

    factory = GraphsFactory([graph_cfg])
    compiled_graph = await factory.create_graph("conditional_graph")
    result = await compiled_graph.ainvoke({"input": {"question": "bye"}, "intermediate_results": {}, "feature_flags": {}, "errors": []})

    assert result["intermediate_results"]["branch_b"]["status"] == "completed"
    assert "branch_a" not in result["intermediate_results"]
