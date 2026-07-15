from __future__ import annotations

import logging
import sys
from typing import Any


def get_logger(name: str = "yaga") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False
    return logger


def log_event(logger: logging.Logger, event: str, **context: Any) -> None:
    payload = {"event": event, **context}
    logger.info("%s", payload)
