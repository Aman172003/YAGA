from __future__ import annotations

from typing import Any


class PersistenceFactory:
    def __init__(self, persistence_config: dict[str, Any] | None = None):
        self._persistence_config = persistence_config or {}
        self.backend = str(self._persistence_config.get("type", "memory") or "memory").lower()
        self._store: dict[str, dict[str, Any]] = {}
        self._initialized = False

    async def initialize(self) -> None:
        if self.backend not in {"memory", "postgres", "redis"}:
            self.backend = "memory"
        self._initialized = True
        return None

    async def save_state(self, thread_id: str, state: dict[str, Any]) -> dict[str, Any]:
        if self.backend == "memory":
            self._store[thread_id] = dict(state)
            return self._store[thread_id]
        if self.backend in {"postgres", "redis"}:
            self._store[thread_id] = dict(state)
            return self._store[thread_id]
        self._store[thread_id] = dict(state)
        return self._store[thread_id]

    async def load_state(self, thread_id: str) -> dict[str, Any] | None:
        state = self._store.get(thread_id)
        return dict(state) if state is not None else None

    async def clear_state(self, thread_id: str) -> None:
        self._store.pop(thread_id, None)

    async def get_state(self, thread_id: str) -> dict[str, Any] | None:
        return await self.load_state(thread_id)
