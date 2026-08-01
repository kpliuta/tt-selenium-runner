from __future__ import annotations

import shlex

import pytest

from src.task_exec import build_env_prefix


class TestBuildEnvPrefix:
    def test_empty_when_no_var_env(self) -> None:
        assert build_env_prefix({"PATH": "/bin", "HOME": "/root"}) == ""

    def test_empty_with_empty_extra(self) -> None:
        assert build_env_prefix({}, extra={}) == ""

    def test_ignores_non_var_keys(self) -> None:
        command = build_env_prefix(
            {"PATH": "/bin", "VAR_RUNNER_PARAM": "true", "HOME": "/root"}
        )
        assert command == "VAR_RUNNER_PARAM=true"

    def test_quotes_values_with_special_characters(self) -> None:
        command = build_env_prefix(
            {"VAR_QUERY": "price > 5 && echo $HOME", "HOME": "/root"}
        )
        assert command == "VAR_QUERY='price > 5 && echo $HOME'"

    def test_joins_multiple_vars_with_space(self) -> None:
        command = build_env_prefix({"VAR_A": "1", "VAR_B": "2", "VAR_C": "3"})
        assert command == "VAR_A=1 VAR_B=2 VAR_C=3"

    def test_extra_vars_come_first(self) -> None:
        command = build_env_prefix(
            {"VAR_A": "1"},
            extra={"MNT_OUTPUT_DIR": "/mnt/runner/tasks/tt-selenium-example-task/output"},
        )
        assert command == (
            "MNT_OUTPUT_DIR=/mnt/runner/tasks/tt-selenium-example-task/output VAR_A=1"
        )

    def test_extra_value_with_spaces_is_quoted(self) -> None:
        command = build_env_prefix(
            {},
            extra={"MNT_OUTPUT_DIR": "/mnt/runner/tasks/my task/output"},
        )
        assert command == "MNT_OUTPUT_DIR='/mnt/runner/tasks/my task/output'"

    @pytest.mark.parametrize(
        ("value",),
        [
            ("plain",),
            ("with space",),
            ("with $dollar and `backtick`",),
            ("with 'single quotes'",),
            ("with \"double quotes\"",),
            ("with\nnewline",),
            ("",),
        ],
    )
    def test_prefix_is_shell_safe(self, value: str) -> None:
        prefix = build_env_prefix({"VAR_PARAM": value})
        assert shlex.split(prefix) == [f"VAR_PARAM={value}"]

    def test_extra_value_is_shell_safe(self) -> None:
        prefix = build_env_prefix(
            {}, extra={"MNT_OUTPUT_DIR": "out dir with $ and 'quotes'"}
        )
        assert shlex.split(prefix) == ["MNT_OUTPUT_DIR=out dir with $ and 'quotes'"]
