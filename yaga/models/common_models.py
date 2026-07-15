from typing import Any, Dict, List, TypedDict


class GraphState(TypedDict, total=False):
    input: Dict[str, Any]
    intermediate_results: Dict[str, Any]
    feature_flags: Dict[str, Any]
    errors: List[str]
