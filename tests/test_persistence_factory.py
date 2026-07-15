import pytest

from rtkaiagents.factories.persistence_factory import PersistenceFactory


@pytest.mark.asyncio
async def test_persistence_factory_tracks_state_per_thread() -> None:
    factory = PersistenceFactory({"type": "memory"})
    await factory.initialize()

    first = await factory.save_state("thread-1", {"step": 1})
    second = await factory.save_state("thread-1", {"step": 2})
    other = await factory.load_state("thread-2")

    assert first["step"] == 1
    assert second["step"] == 2
    assert other is None
