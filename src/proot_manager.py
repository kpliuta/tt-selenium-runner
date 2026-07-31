from __future__ import annotations

import os
import signal
import subprocess
import threading
import time
from pathlib import Path

from src import log

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
        self.proot_log = runner_path / "proot_output.log"

    def _clean_fifos(self) -> None:
        for p in [self.in_fifo, self.out_fifo, self.pid_file, self.proot_log]:
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

        log(f"Sending command: {command}")

        # Follow new container output from the persistent log file
        # so it appears live in the runner's stderr stream regardless
        # of which lifecycle script is running.
        stop_follow = threading.Event()

        def _follow_log() -> None:
            try:
                with open(self.proot_log) as f:
                    f.seek(0, 2)
                    while not stop_follow.is_set():
                        line = f.readline()
                        if line:
                            log(f"[container] {line.rstrip()}")
                        else:
                            time.sleep(0.1)
            except FileNotFoundError:
                pass

        thread = threading.Thread(target=_follow_log, daemon=True)
        thread.start()

        try:
            with open(self.in_fifo, "w") as f:
                f.write(command + "\n")

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

            raise ProotTimeoutError(
                f"Timeout ({timeout}s) waiting for command response"
            )
        finally:
            # drain: let follower read remaining output
            time.sleep(0.2)
            stop_follow.set()

    def start_proot(self) -> None:
        """Start proot-distro in the background with the listener script.

        Creates fifos, starts the proot-distro process, redirects its stdout
        to a persistent log file so container output is available across
        all lifecycle scripts. Raises ProotError on failure.
        """
        self._clean_fifos()
        self._create_fifos()

        listener_path = self.runner_path / "sh" / "proot_listener.sh"
        if not listener_path.exists():
            raise ProotError(f"Listener script not found at {listener_path}")

        # proot-distro login uses env -i, which strips all host env vars.
        # Inject VAR_* vars so they survive into the container.
        var_env_args = [
            f"{k}={v}" for k, v in os.environ.items()
            if k.startswith("VAR_")
        ]

        entry = (
            ["env", *var_env_args, "sh", "/mnt/runner/sh/proot_listener.sh"]
            if var_env_args else
            ["sh", "/mnt/runner/sh/proot_listener.sh"]
        )

        cmd = [
            "proot-distro", "login", "ubuntu",
            "--bind", f"{self.runner_path}:/mnt/runner",
            "--no-sysvipc", "--",
            *entry,
        ]

        log(f"Starting proot: {' '.join(cmd)}")
        try:
            self.proot_log.parent.mkdir(parents=True, exist_ok=True)
            proc = subprocess.Popen(
                cmd,
                stdout=open(self.proot_log, "a"),
                stderr=subprocess.STDOUT,
                preexec_fn=lambda: signal.signal(signal.SIGINT, signal.SIG_IGN),
            )
        except FileNotFoundError as e:
            self._clean_fifos()
            raise ProotError("proot-distro not found. Run initialization first.") from e

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

        log(f"Warning: proot process {pid} not responding, sending SIGTERM")
        try:
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, OSError):
            pass
        time.sleep(2)

        log(f"Warning: proot process {pid} not responding, sending SIGKILL")
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
