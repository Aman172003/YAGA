import pytest

from yaga.factories.models_factory import ModelsFactory
from yaga.models.agent_models import AgentConfig, InlinePromptConfig, ModelConfig, PromptProviderConfig


@pytest.mark.asyncio
async def test_model_factory_exposes_provider_metadata_and_invocation() -> None:
    agent_cfg = AgentConfig(
        name="demo-agent",
        model=ModelConfig(provider="mock", model_name="demo-model"),
        prompt_provider=PromptProviderConfig(inline=InlinePromptConfig(user_prompt="hello")),
    )

    factory = ModelsFactory([agent_cfg])
    provider = factory.get_model(agent_cfg)
    result = await provider.ainvoke({"messages": [{"role": "user", "content": "hello"}]})

    assert result["provider"] == "mock"
    assert result["model"] == "demo-model"
