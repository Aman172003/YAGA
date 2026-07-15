import logging

from yaga.logging import get_logger, log_event


def test_logging_helpers_emit_structured_records() -> None:
    logger = get_logger("test.logger")
    records = []

    class CaptureHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            records.append(record)

    logger.handlers.clear()
    handler = CaptureHandler()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    log_event(logger, "demo.event", agent="demo")

    assert len(records) == 1
    assert records[0].getMessage().startswith("{'event': 'demo.event'" )
