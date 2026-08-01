from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from src import before_task


class TestMain:
    def test_quotes_task_dir_in_cd_command(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            sys, "argv", ["before_task.py", "/mnt/runner", "my task"]
        )
        manager = MagicMock()
        manager.in_fifo.exists.return_value = True
        with patch.object(before_task, "ProotManager", return_value=manager):
            with pytest.raises(SystemExit) as excinfo:
                before_task.main()
        assert excinfo.value.code == 0
        manager.send_command.assert_any_call(
            "cd '/mnt/runner/tasks/my task'", 10
        )
        manager.send_command.assert_any_call("poetry install")

    def test_exits_when_proot_not_running(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            sys, "argv", ["before_task.py", "/mnt/runner", "my_task"]
        )
        manager = MagicMock()
        manager.in_fifo.exists.return_value = False
        with patch.object(before_task, "ProotManager", return_value=manager):
            with pytest.raises(SystemExit) as excinfo:
                before_task.main()
        assert excinfo.value.code == 1
        manager.send_command.assert_not_called()
