from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from src import before_exec


class TestMain:
    def test_exports_display_before_vnc_setup(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            sys, "argv", ["before_exec.py", "/mnt/runner"]
        )
        manager = MagicMock()
        with patch.object(before_exec, "ProotManager", return_value=manager):
            with pytest.raises(SystemExit) as excinfo:
                before_exec.main()
        assert excinfo.value.code == 0
        sent = [call.args[0] for call in manager.send_command.call_args_list]
        assert sent.index("export DISPLAY=:1") < sent.index(
            "sh /mnt/runner/sh/setup_vnc.sh"
        )
        manager.send_command.assert_any_call("export DISPLAY=:1")
