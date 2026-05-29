from __future__ import annotations

import os
import re
import signal
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path


class ProotError(Exception):
    pass


class ProotTimeoutError(ProotError):
    pass


class ProotManager:
    """Manages the proot-distro session and fifo-based command communication."""

    def __init__(self, runner_path: Path) -> None:
        self.runner_path = runner_path
        self.in_fifo = runner_path / "in.fifo"
        self.out_fifo = runner_path / "out.fifo"
        self.pid_file = runner_path / ".proot_pid"
        self.stdout_path = runner_path / "stdout"

    def _clean_fifos(self) -> None:
        for p in [self.in_fifo, self.out_fifo, self.pid_file]:
            try:
                p.unlink(missing_ok=True)
            except OSError as e:
                raise ProotError(f"Failed to remove {p}: {e}") from e

    def _create_fifos(self) -> None:
        try:
            os.mkfifo(self.in_fifo)
            os.mkfifo(self.out_fifo)
        except OSError as e:
            raise ProotError(f"Failed to create fifos: {e}") from e

    def send_command(self, command: str, timeout: int = 600) -> None:
        """Send a shell command to the proot session.

        Raises ProotError on communication failure or non-zero exit.
        Raises ProotTimeoutError on timeout.
        """
        if not self.in_fifo.exists():
            raise ProotError("in.fifo not found — is the proot session running?")

        print(f"Sending command: {command}", file=sys.stderr)
        try:
            with open(self.in_fifo, "w") as f:
                f.write(command + "\n")
        except OSError as e:
            raise ProotError(f"Failed to write to in.fifo: {e}") from e

        start = time.time()
        while time.time() - start < timeout:
            try:
                with open(self.out_fifo, "r") as f:
                    status_str = f.read().strip()
            except OSError as e:
                raise ProotError(f"Failed to read from out.fifo: {e}") from e

            if status_str:
                exit_code = int(status_str)
                if exit_code != 0:
                    raise ProotError(
                        f"Command exited with code {exit_code}"
                    )
                return

            time.sleep(0.1)

        raise ProotTimeoutError(
            f"Timeout ({timeout}s) waiting for command response"
        )

    def start_proot(self) -> None:
        """Start proot-distro in the background with the listener script.

        Creates fifos, starts the proot-distro process, and begins logging
        its stdout. Raises ProotError on failure.
        """
        self._clean_fifos()
        self._create_fifos()

        listener_path = self.runner_path / "scripts" / "sh" / "proot_listener.sh"
        if not listener_path.exists():
            raise ProotError(f"Listener script not found at {listener_path}")

        cmd = [
            "proot-distro", "login", "ubuntu",
            "--bind", f"{self.runner_path}:/mnt/runner",
            "--no-sysvipc", "--",
            "sh", "/mnt/runner/scripts/sh/proot_listener.sh",
        ]

        print(f"Starting proot: {' '.join(cmd)}")
        try:
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                # ignore SIGINT so Ctrl+C on the host doesn't kill the container
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
            )
        except FileNotFoundError as e:
            self._clean_fifos()
            raise ProotError("proot-distro not found. Run initialization first.") from e

        def _log_output() -> None:
            assert proc.stdout is not None
            self.stdout_path.parent.mkdir(parents=True, exist_ok=True)
            # proot-distro emits ANSI escape sequences (\r, [K, color codes) for progress spinners.
            # Strip them so the log is clean and readable.
            ansi_escape = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]|\x1b\][0-9;]*\x07|\r")
            with open(self.stdout_path, "a") as log:
                for line in iter(proc.stdout.readline, b""):
                    text = ansi_escape.sub("", line.decode(errors="replace")).strip()
                    if text:
                        ts = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] [container]")
                        log.write(f"{ts} {text}\n")
                        log.flush()

        thread = threading.Thread(target=_log_output, daemon=True)
        thread.start()

        self.pid_file.write_text(str(proc.pid))

    def stop_proot(self, timeout: int = 60) -> None:
        """Gracefully shut down the proot session.

        Sends the shutdown command via fifo, then waits for the proot
        process to exit. Raises ProotError on failure.
        """
        if self.in_fifo.exists():
            try:
                self.send_command("__shutdown__", timeout=30)
            except ProotError:
                pass

        if not self.pid_file.exists():
            self._clean_fifos()
            return

        try:
            pid = int(self.pid_file.read_text().strip())
        except (ValueError, FileNotFoundError):
            self._clean_fifos()
            return

        start = time.time()
        while time.time() - start < timeout:
            if not self._is_process_alive(pid):
                self.pid_file.unlink(missing_ok=True)
                self._clean_fifos()
                return
            time.sleep(1)

        print(f"Warning: proot process {pid} not responding, sending SIGTERM", file=sys.stderr)
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        time.sleep(2)

        print(f"Warning: proot process {pid} not responding, sending SIGKILL", file=sys.stderr)
        try:
            os.kill(pid, signal.SIGKILL)
        except (ProcessLookupError, OSError):
            pass

        self.pid_file.unlink(missing_ok=True)
        self._clean_fifos()

    @staticmethod
    def _is_process_alive(pid: int) -> bool:
        # kill -0 only checks if the process exists; doesn't send a signal
        try:
            result = subprocess.run(
                ["kill", "-0", str(pid)],
                capture_output=True, timeout=5,
            )
            return result.returncode == 0
        except (subprocess.SubprocessError, OSError):
            return False
