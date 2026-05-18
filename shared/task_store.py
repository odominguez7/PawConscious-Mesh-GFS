"""In-process task state store for async A2A v0.3 task lifecycle (Phase 5.5).

v0.1 is in-process: dict guarded by asyncio.Lock. Lost on Cloud Run cold start.
Phase 5.6 promotes to Firestore for durability + cross-instance state.

Per A2A v0.3 spec, task states are: submitted | working | input-required |
completed | failed | canceled. We use: submitted → working → completed/failed.
"""
from __future__ import annotations

import asyncio
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class TaskState:
    task_id: str
    status: str = "submitted"  # submitted | working | completed | failed
    progress_message: str = ""
    output: Optional[dict[str, Any]] = None
    error: Optional[str] = None
    bundle_hash: Optional[str] = None
    bundle_signature: Optional[str] = None
    chain_anchor: Optional[str] = None
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    input: dict[str, Any] = field(default_factory=dict)


class TaskStore:
    def __init__(self, ttl_seconds: int = 86400):  # 24 hour default retention
        self._tasks: dict[str, TaskState] = {}
        self._lock = asyncio.Lock()
        self._ttl_seconds = ttl_seconds

    async def create(self, input_data: dict[str, Any]) -> TaskState:
        async with self._lock:
            task_id = "task-" + uuid.uuid4().hex[:16]
            state = TaskState(task_id=task_id, input=input_data)
            self._tasks[task_id] = state
            return state

    async def get(self, task_id: str) -> Optional[TaskState]:
        async with self._lock:
            await self._purge_expired_unlocked()
            return self._tasks.get(task_id)

    async def update(
        self,
        task_id: str,
        *,
        status: Optional[str] = None,
        progress_message: Optional[str] = None,
        output: Optional[dict[str, Any]] = None,
        error: Optional[str] = None,
        bundle_hash: Optional[str] = None,
        bundle_signature: Optional[str] = None,
        chain_anchor: Optional[str] = None,
    ) -> None:
        async with self._lock:
            state = self._tasks.get(task_id)
            if state is None:
                return
            if status is not None:
                state.status = status
                if status in {"completed", "failed", "canceled"}:
                    state.completed_at = time.time()
            if progress_message is not None:
                state.progress_message = progress_message
            if output is not None:
                state.output = output
            if error is not None:
                state.error = error
            if bundle_hash is not None:
                state.bundle_hash = bundle_hash
            if bundle_signature is not None:
                state.bundle_signature = bundle_signature
            if chain_anchor is not None:
                state.chain_anchor = chain_anchor

    async def _purge_expired_unlocked(self) -> None:
        """Caller must hold the lock."""
        now = time.time()
        expired = [tid for tid, s in self._tasks.items()
                   if s.completed_at is not None and (now - s.completed_at) > self._ttl_seconds]
        for tid in expired:
            del self._tasks[tid]


# Module-level singleton for the mesh_api process
task_store = TaskStore(ttl_seconds=86400)
