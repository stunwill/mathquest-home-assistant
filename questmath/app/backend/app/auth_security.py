from __future__ import annotations

import math
import threading
import time
from collections import deque
from dataclasses import dataclass, field


@dataclass
class FailureState:
    failures: deque[float] = field(default_factory=deque)
    updated_at: float = 0


class LoginRateLimiter:
    """Bounded, in-memory failed-login throttling for a single add-on instance."""

    def __init__(
        self,
        *,
        failure_limit: int = 5,
        window_seconds: int = 300,
        max_entries: int = 10_000,
    ) -> None:
        self.failure_limit = failure_limit
        self.window_seconds = window_seconds
        self.max_entries = max_entries
        self._states: dict[tuple[str, str], FailureState] = {}
        self._lock = threading.Lock()

    @staticmethod
    def key(client_host: str | None, username: str) -> tuple[str, str]:
        return (client_host or 'unknown', username.strip().casefold())

    def _trim(self, state: FailureState, now: float) -> None:
        cutoff = now - self.window_seconds
        while state.failures and state.failures[0] <= cutoff:
            state.failures.popleft()

    def _prune(self, now: float) -> None:
        stale = []
        for key, state in self._states.items():
            self._trim(state, now)
            if not state.failures:
                stale.append(key)
        for key in stale:
            self._states.pop(key, None)
        if len(self._states) >= self.max_entries:
            oldest = min(self._states, key=lambda key: self._states[key].updated_at)
            self._states.pop(oldest, None)

    def retry_after(self, key: tuple[str, str], now: float | None = None) -> int:
        current = time.monotonic() if now is None else now
        with self._lock:
            state = self._states.get(key)
            if state is None:
                return 0
            self._trim(state, current)
            if len(state.failures) < self.failure_limit:
                if not state.failures:
                    self._states.pop(key, None)
                return 0
            return max(1, math.ceil(state.failures[0] + self.window_seconds - current))

    def record_failure(self, key: tuple[str, str], now: float | None = None) -> None:
        current = time.monotonic() if now is None else now
        with self._lock:
            self._prune(current)
            state = self._states.setdefault(key, FailureState())
            self._trim(state, current)
            state.failures.append(current)
            state.updated_at = current

    def record_success(self, key: tuple[str, str]) -> None:
        with self._lock:
            self._states.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._states.clear()

    @property
    def state_size(self) -> int:
        with self._lock:
            return len(self._states)
