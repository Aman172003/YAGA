import pytest

from yaga.factories.persistence_factory import PersistenceFactory


@pytest.mark.asyncio
async def test_persistence_factory_supports_memory_and_postgres_like_configs() -> None:
    memory_factory = PersistenceFactory({"type": "memory"})
    await memory_factory.initialize()
    await memory_factory.save_state("thread-1", {"step": 1})

    postgres_factory = PersistenceFactory({"type": "postgres", "config": {"dsn": "postgresql://example"}})
    await postgres_factory.initialize()
    await postgres_factory.save_state("thread-2", {"step": 2})

    assert await memory_factory.load_state("thread-1") == {"step": 1}
    assert await postgres_factory.load_state("thread-2") == {"step": 2}
    assert memory_factory.backend == "memory"
    assert postgres_factory.backend == "postgres"
