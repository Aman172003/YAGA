import json
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent.parent
load_dotenv(project_root / ".env")

from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from yaga.service import AgentService
from yaga.tracing import get_trace_id, trace_scope
from .config import AppSettings


class AgentRunRequest(BaseModel):
    input: dict[str, Any] = {}


class GraphRunRequest(BaseModel):
    input: dict[str, Any] = {}
    featureflags_context: dict[str, Any] = {}


def create_app(service: AgentService | None = None, settings: AppSettings | None = None) -> FastAPI:
    app = FastAPI(title="AI Agents Platform")
    settings = settings or AppSettings()

    if service is not None:
        app.state.service = service
    else:
        app.state.service = None

    @app.on_event("startup")
    async def initialize_service() -> None:
        if app.state.service is None:
            app.state.service = await AgentService.from_configs([
                settings.agents_config,
                settings.graphs_config,
                settings.mcps_config,
            ])

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/agents/{agent_name}/run")
    async def run_agent(request: Request, agent_name: str, body: AgentRunRequest) -> dict[str, Any]:
        trace_id = request.headers.get("x-trace-id") or body.input.get("trace_id")
        with trace_scope(trace_id) as active_trace_id:
            result = await app.state.service.run_agent(agent_name, body.input, config={"trace_id": active_trace_id})
            result.setdefault("metadata", {})["trace_id"] = active_trace_id
            return result

    @app.post("/agents/{agent_name}/stream")
    async def stream_agent(request: Request, agent_name: str, body: AgentRunRequest) -> StreamingResponse:
        trace_id = request.headers.get("x-trace-id") or body.input.get("trace_id")

        async def gen() -> Any:
            with trace_scope(trace_id):
                async for chunk in app.state.service.stream_agent(agent_name, body.input, config={"trace_id": get_trace_id()}):
                    yield f"data: {json.dumps(chunk)}\n\n"

        return StreamingResponse(gen(), media_type="text/event-stream")

    @app.post("/graphs/{graph_name}/run")
    async def run_graph(request: Request, graph_name: str, body: GraphRunRequest) -> dict[str, Any]:
        trace_id = request.headers.get("x-trace-id") or body.input.get("trace_id")
        with trace_scope(trace_id) as active_trace_id:
            result = await app.state.service.run_graph(graph_name, body.input, context={"request": body.featureflags_context}, config={"trace_id": active_trace_id})
            result.setdefault("metadata", {})["trace_id"] = active_trace_id
            return result

    return app
