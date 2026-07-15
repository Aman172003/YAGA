from __future__ import annotations

import ast
from typing import Any

from langgraph.graph import END, StateGraph

from yaga.models import GraphConfig, GraphState


class _AttrDict(dict):
    def __getattr__(self, item: str) -> Any:
        return self.get(item)


class GraphsFactory:
    def __init__(self, graphs: list[GraphConfig]):
        self._graphs = {graph.name: graph for graph in graphs}
        self._graphs_cache: dict[str, Any] = {}

    def _to_context(self, state: dict[str, Any]) -> dict[str, Any]:
        return {
            "input": _AttrDict(state.get("input", {})),
            "feature_flags": _AttrDict(state.get("feature_flags", {})),
            "intermediate_results": _AttrDict(state.get("intermediate_results", {})),
        }

    def _evaluate_condition(self, expression: str, state: dict[str, Any]) -> bool:
        context = self._to_context(state)
        context.update({"True": True, "False": False, "None": None})
        try:
            return bool(ast.literal_eval(expression)) if expression in {"True", "False"} else bool(eval(expression, {"__builtins__": {}}, context))
        except Exception:
            return False

    async def create_graph(self, graph_name: str) -> Any:
        if graph_name in self._graphs_cache:
            return self._graphs_cache[graph_name]
        graph_cfg = self._graphs.get(graph_name)
        if not graph_cfg:
            raise KeyError(f"Graph '{graph_name}' not found")

        builder = StateGraph(GraphState)
        for node_cfg in graph_cfg.nodes:
            async def node_fn(state: dict[str, Any], node_name: str = node_cfg.name) -> dict[str, Any]:
                state.setdefault("intermediate_results", {})
                entry = {"status": "completed", "node": node_name}
                if node_name == graph_cfg.nodes[-1].name:
                    entry["terminal"] = True
                state["intermediate_results"][node_name] = entry
                return state

            builder.add_node(node_cfg.name, node_fn)

        for edge in graph_cfg.edges:
            if edge.type == "conditional":
                condition_targets = {cond.target: cond.target for cond in edge.conditions}
                if edge.default_target:
                    condition_targets[edge.default_target] = edge.default_target
                if edge.target and edge.target not in condition_targets:
                    condition_targets[edge.target] = edge.target

                def condition_fn(state: dict[str, Any], edge_obj: Any = edge) -> str:
                    for condition in edge_obj.conditions:
                        if self._evaluate_condition(condition.condition, state):
                            return condition.target
                    return edge_obj.default_target or edge_obj.target

                path_map = {}
                for target_name in condition_targets.values():
                    path_map[target_name] = END if target_name == "__end__" else target_name
                builder.add_conditional_edges(edge.source, condition_fn, path_map)
            else:
                target = END if edge.target == "__end__" else edge.target
                builder.add_edge(edge.source, target)

        builder.set_entry_point(graph_cfg.start_node or graph_cfg.nodes[0].name)
        compiled = builder.compile()
        self._graphs_cache[graph_name] = compiled
        return compiled
