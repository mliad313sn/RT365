"""Monotonic state machines [Source: 03]. A transition not in the table raises; states never go back."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Generic, TypeVar

from rtcore.errors import TransitionError

S = TypeVar("S")


class MonotonicStateMachine(Generic[S]):
    def __init__(self, transitions: Mapping[S, frozenset[S]], terminal: frozenset[S]) -> None:
        self._transitions = dict(transitions)
        self._terminal = terminal

    def is_terminal(self, state: S) -> bool:
        return state in self._terminal

    def can(self, current: S, nxt: S) -> bool:
        return nxt in self._transitions.get(current, frozenset())

    def assert_transition(self, current: S, nxt: S) -> S:
        if current in self._terminal:
            raise TransitionError(f"{current} is terminal; cannot move to {nxt}")
        if not self.can(current, nxt):
            raise TransitionError(f"illegal transition {current} -> {nxt}")
        return nxt
