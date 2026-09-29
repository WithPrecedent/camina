"""Tests that the README is accurate and its examples work."""

from __future__ import annotations

import ast
import doctest
import pathlib
import re

import pytest

import camina

README = pathlib.Path(__file__).parent.parent / "README.md"
TEXT = README.read_text(encoding="utf8")
EXPECTED = re.compile(r"# -> (.*?)(?:  #.*)?$")
BLOCKS = re.findall(r"```python\n(.*?)```", TEXT, flags=re.DOTALL)


def test_readme_has_no_placeholders() -> None:
    assert "TODO" not in TEXT
    assert "[summary]" not in TEXT


def test_readme_examples_run() -> None:
    """Runs every `python` block in the README as one session.

    A trailing `# -> value` comment on a line states what the line returns.
    """
    assert len(BLOCKS) >= 3
    checker = doctest.OutputChecker()
    namespace: dict[str, object] = {}
    failures = []
    checked = 0
    for number, block in enumerate(BLOCKS):
        lines = block.splitlines()
        for node in ast.parse(block).body:
            match = EXPECTED.search(lines[node.end_lineno - 1])
            if match and isinstance(node, ast.Expr):
                code = compile(ast.Expression(node.value), "README", "eval")
                got = repr(eval(code, namespace))  # noqa: S307
                want = match.group(1)
                checked += 1
                if not checker.check_output(want, got, doctest.ELLIPSIS):
                    failures.append(f"block {number}: {want} != {got}")
            else:
                code = compile(ast.Module([node], []), "README", "exec")
                exec(code, namespace)  # noqa: S102
    assert not failures, "\n".join(failures)
    assert checked > 30


def _listed_names() -> list[str]:
    """Returns the names in backticks that start bullet points."""
    return re.findall(r"^\s*\* `(\w+)`", TEXT, flags=re.MULTILINE)


@pytest.mark.parametrize("name", sorted(set(_listed_names())))
def test_documented_names_exist(name: str) -> None:
    assert hasattr(camina, name) or hasattr(camina.convert, name)


@pytest.mark.parametrize("name", camina.__all__)
def test_exported_names_are_documented(name: str) -> None:
    assert f"`{name}`" in TEXT
