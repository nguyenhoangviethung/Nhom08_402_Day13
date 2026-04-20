from __future__ import annotations

import logging
import os
import hashlib
from pathlib import Path
from typing import Any

import structlog
from structlog.contextvars import merge_contextvars

from .pii import scrub_text

LOG_PATH = Path(os.getenv("LOG_PATH", "data/logs.jsonl"))


class JsonlFileProcessor:
    def __call__(self, logger: Any, method_name: str, event_dict: dict[str, Any]) -> dict[str, Any]:
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        rendered = structlog.processors.JSONRenderer()(logger, method_name, event_dict)
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(rendered + "\n")
        return event_dict


def ensure_schema_fields(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    event_dict.setdefault("service", "app")
    event_dict.setdefault("env", os.getenv("APP_ENV", "dev"))

    # Keep schema-compatible correlation IDs even for startup/system logs.
    base_correlation = event_dict.get("correlation_id") or event_dict.get("request_id") or "system"
    event_dict["correlation_id"] = str(base_correlation)

    if event_dict.get("service") == "api":
        correlation_seed = str(event_dict.get("correlation_id", "legacy"))
        event_dict.setdefault("model", "unknown-model")
        event_dict.setdefault("feature", "legacy-feature")
        event_dict.setdefault("session_id", f"legacy-session-{correlation_seed[-8:]}")
        event_dict.setdefault("user_id_hash", hashlib.sha256(correlation_seed.encode("utf-8")).hexdigest()[:12])

    return event_dict



def scrub_event(_: Any, __: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    payload = event_dict.get("payload")
    if isinstance(payload, dict):
        event_dict["payload"] = {
            k: scrub_text(v) if isinstance(v, str) else v for k, v in payload.items()
        }
    if "event" in event_dict and isinstance(event_dict["event"], str):
        event_dict["event"] = scrub_text(event_dict["event"])
    return event_dict



def configure_logging() -> None:
    logging.basicConfig(format="%(message)s", level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")))
    structlog.configure(
        processors=[
            merge_contextvars,
            ensure_schema_fields,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True, key="ts"),
            # Đăng ký bộ lọc PII ở đây để nó quét qua mọi log trước khi in ra
            scrub_event,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            JsonlFileProcessor(),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )



def get_logger() -> structlog.typing.FilteringBoundLogger:
    return structlog.get_logger()
