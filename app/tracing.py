from __future__ import annotations

import os
import uuid
from contextlib import contextmanager
from typing import Any

class _NoopLangfuseClient:
    def update_current_trace(self, **kwargs: Any) -> None:
        return None

    def update_current_span(self, **kwargs: Any) -> None:
        return None

    def update_current_generation(self, **kwargs: Any) -> None:
        return None

    @contextmanager
    def start_as_current_span(self, **kwargs: Any):
        yield None

    def create_trace_id(self, *, seed: str | None = None) -> str:
        return uuid.uuid4().hex

    def flush(self) -> None:
        return None

    def shutdown(self) -> None:
        return None


try:
    from langfuse import get_client, observe
except Exception:  # pragma: no cover
    def observe(*args: Any, **kwargs: Any):
        def decorator(func):
            return func
        return decorator

    def get_client() -> _NoopLangfuseClient:
        return _NoopLangfuseClient()


def _safe_call(fn: Any, **kwargs: Any) -> bool:
    try:
        fn(**kwargs)
        return True
    except Exception:
        return False


def get_langfuse_client() -> Any:
    try:
        return get_client()
    except Exception:  # pragma: no cover
        return _NoopLangfuseClient()


class _LangfuseContextProxy:
    def update_current_trace(self, **kwargs: Any) -> None:
        _safe_call(get_langfuse_client().update_current_trace, **kwargs)

    def update_current_span(self, **kwargs: Any) -> None:
        _safe_call(get_langfuse_client().update_current_span, **kwargs)

    def update_current_generation(self, **kwargs: Any) -> None:
        _safe_call(get_langfuse_client().update_current_generation, **kwargs)

    def update_current_observation(self, **kwargs: Any) -> None:
        client = get_langfuse_client()
        generation_keys = {
            "model",
            "model_parameters",
            "usage_details",
            "cost_details",
            "completion_start_time",
            "prompt",
        }
        prefers_generation = any(key in kwargs for key in generation_keys)

        if prefers_generation:
            if _safe_call(client.update_current_generation, **kwargs):
                return
            _safe_call(client.update_current_span, **kwargs)
            return

        if _safe_call(client.update_current_span, **kwargs):
            return
        _safe_call(client.update_current_generation, **kwargs)


langfuse_context = _LangfuseContextProxy()


def create_trace_id(seed: str | None = None) -> str:
    client = get_langfuse_client()
    try:
        return client.create_trace_id(seed=seed)
    except Exception:  # pragma: no cover
        return uuid.uuid4().hex


def shutdown_tracing() -> None:
    _safe_call(get_langfuse_client().shutdown)


def tracing_enabled() -> bool:
    return bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
