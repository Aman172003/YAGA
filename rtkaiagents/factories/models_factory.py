from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from rtkaiagents.models import AgentConfig, ModelConfig


class BaseModelProvider:
    def __init__(self, config: ModelConfig):
        self.config = config

    async def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


class MockModelProvider(BaseModelProvider):
    async def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "messages": payload.get("messages", []),
            "model": self.config.model_name,
            "provider": self.config.provider,
            "mode": "mock",
        }


class LiteLLMModelProvider(BaseModelProvider):
    async def invoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        try:
            import litellm
        except ImportError:
            raise RuntimeError("litellm is not installed. Run: pip install litellm")

        messages = payload.get("messages", [])
        response = await litellm.acompletion(
            model=self.config.model_name,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            **(self.config.additional_params or {}),
        )
        choice = response.choices[0]
        return {
            "messages": messages + [{"role": "assistant", "content": choice.message.content}],
            "model": self.config.model_name,
            "provider": self.config.provider,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "additional_params": self.config.additional_params,
            "structured_response": self.config.structured_response.model_dump() if self.config.structured_response else None,
            "usage": response.usage.model_dump() if response.usage else None,
        }


@dataclass
class RuntimeModel:
    name: str
    config: ModelConfig

    def __post_init__(self) -> None:
        provider_name = (self.config.provider or "litellm").lower()
        if provider_name == "mock":
            self._provider = MockModelProvider(self.config)
        elif provider_name == "litellm":
            self._provider = LiteLLMModelProvider(self.config)
        else:
            self._provider = LiteLLMModelProvider(self.config)

    @property
    def provider(self) -> str:
        return self.config.provider

    @property
    def model_name(self) -> str:
        return self.config.model_name

    async def ainvoke(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._provider.invoke(payload)


SimpleModel = RuntimeModel


class ModelsFactory:
    def __init__(self, config: list[AgentConfig]):
        self._config = {agent.name: agent for agent in config}
        self._models_cache: dict[str, RuntimeModel] = {}

    def get_model(self, agent_config: AgentConfig) -> RuntimeModel:
        if agent_config.name in self._models_cache:
            return self._models_cache[agent_config.name]
        model = RuntimeModel(name=agent_config.name, config=agent_config.model)
        self._models_cache[agent_config.name] = model
        return model
