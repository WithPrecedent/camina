"""Tests for `camina.clock`."""

from __future__ import annotations

import datetime
import re

import pytest

import camina
from camina import clock


def test_how_soon_is_now_default_format() -> None:
    result = camina.how_soon_is_now()
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}", result)
    parsed = datetime.datetime.strptime(result, "%Y-%m-%d_%H-%M")  # noqa: DTZ007
    assert abs(parsed - datetime.datetime.now()) < datetime.timedelta(minutes=2)  # noqa: DTZ005


def test_how_soon_is_now_prefix_and_format() -> None:
    result = camina.how_soon_is_now(prefix="run_", time_format="%Y")
    assert result == f"run_{datetime.datetime.now().year}"  # noqa: DTZ005


def test_timer_returns_result_and_reports(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    ticks = iter([100.0, 100.0 + 3725])
    monkeypatch.setattr(clock.time, "perf_counter", lambda: next(ticks))

    @camina.timer
    def add(x: int, y: int = 1) -> int:
        """Adds numbers."""
        return x + y

    assert add(2, y=3) == 5
    assert add.__name__ == "add"
    assert add.__doc__ == "Adds numbers."
    assert capsys.readouterr().out == "add completed in 1:02:05\n"


def test_timer_with_callable_object(capsys: pytest.CaptureFixture[str]) -> None:
    class Worker:
        def __call__(self) -> str:
            return "done"

    assert camina.timer(Worker())() == "done"
    assert capsys.readouterr().out.startswith("Worker completed in 0:00:0")
