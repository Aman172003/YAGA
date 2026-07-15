# rtkaiagents

This repository contains a lightweight, YAML-driven agent runtime built around a small FastAPI surface and a LangGraph-style workflow layer.

## What is included

- YAML-defined agent and graph loading from the config directory.
- A service layer that can run an agent or a graph from Python.
- A FastAPI app exposing health, agent run, and graph run endpoints.
- Lightweight provider, tool, MCP, persistence, and logging hooks for the current runtime pass.

## Quickstart

### Run the tests

```bash
python3 -m pytest -q
```

### Start the API

```bash
python3 -m uvicorn rtkaiagents.api.factory:create_app --factory --host 127.0.0.1 --port 8000
```

### Example requests

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/agents/my_agent/run \
  -H 'Content-Type: application/json' \
  -d '{"input": {"question": "What is 2+2?"}}'
curl -X POST http://127.0.0.1:8000/graphs/my_graph/run \
  -H 'Content-Type: application/json' \
  -d '{"input": {"question": "What is 2+2?"}}'
```

### Use the service from Python

```python
import asyncio
from rtkaiagents.service import AgentService

async def main() -> None:
    service = await AgentService.from_configs([
        "config/agents.yaml",
        "config/graphs.yaml",
        "config/mcps.yaml",
    ])
    agent_result = await service.run_agent("my_agent", {"question": "What is 2+2?"})
    graph_result = await service.run_graph("my_graph", {"question": "What is 2+2?"})
    print(agent_result)
    print(graph_result)

asyncio.run(main())
```

## Project structure

- [config/](config/) contains YAML examples for agents, graphs, and MCP configuration.
- [rtkaiagents/](rtkaiagents/) contains the runtime package.
- [tests/](tests/) contains regression tests covering agents, graphs, tool/MCP hooks, persistence, and logging.
- [docs/QUICKSTART.md](docs/QUICKSTART.md) contains a compact walkthrough for local execution.
