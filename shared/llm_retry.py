"""Retry + timeout wrapper for Gemini Vertex AI calls.

Per codex G9 #6: Phase 3 blocking risk is model quota/latency spikes and
inconsistent grading. Wrap every Gemini call with deterministic sampling
(temperature 0) + retry with exponential backoff + hard timeout.
"""
from __future__ import annotations

import asyncio
from typing import Any, Callable, TypeVar

T = TypeVar("T")


async def with_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 8.0,
    timeout_seconds: float = 60.0,
) -> T:
    """Run an async callable with retry on transient failures.

    Catches Google API ResourceExhausted, DeadlineExceeded, and ServiceUnavailable.
    Retries with exponential backoff. Hard timeout per attempt.
    """
    last_exc: Exception | None = None
    delay = initial_delay
    for attempt in range(1, max_attempts + 1):
        try:
            return await asyncio.wait_for(fn(), timeout=timeout_seconds)
        except asyncio.TimeoutError as e:
            last_exc = e
            print(f"[llm_retry] timeout attempt {attempt}/{max_attempts}")
        except Exception as e:
            exc_name = type(e).__name__
            if exc_name in {"ResourceExhausted", "DeadlineExceeded", "ServiceUnavailable", "InternalServerError"}:
                last_exc = e
                print(f"[llm_retry] transient {exc_name} attempt {attempt}/{max_attempts}: {e}")
            else:
                raise

        if attempt < max_attempts:
            await asyncio.sleep(delay)
            delay = min(delay * 2, max_delay)

    if last_exc is not None:
        raise last_exc
    raise RuntimeError("with_retry exhausted attempts with no exception captured")


async def agenerate(client, **kwargs):
    """Run a blocking Vertex `generate_content` in a worker thread so it never
    blocks the asyncio event loop. Without this, one in-flight mesh run freezes
    the whole worker (every other request, including /tasks/get polls, hangs)
    for the duration of the synchronous Gemini call. Pure offload, no retry, so
    it composes with callers that already retry (e.g. /api/ask-gemini)."""
    return await asyncio.to_thread(lambda: client.models.generate_content(**kwargs))
