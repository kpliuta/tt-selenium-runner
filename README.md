# tt-selenium-runner

A Selenium runner for [termux-tasker](https://github.com/kpliuta/termux-tasker).

Manages a `proot-distro` Ubuntu container with VNC and Firefox to execute
Selenium-based Python tasks on Android via Termux.

## Lifecycle

1. **initialization** — Install `proot-distro` and the Ubuntu container on the host (one-time)
2. **before-exec** — Start proot container with fifo listener, ensure packages are installed, install/upgrade Firefox from official Mozilla repo, configure VNC password/xstartup, start VNC server
3. **before-task** — `poetry install` on the task directory inside the container
4. **task-exec** — `poetry run` on the task with `MNT_OUTPUT_DIR` env var
5. **after-exec** — Send shutdown command to proot container, wait for graceful exit
6. **termination** — Placeholder (currently no-op)

## Configuration

| Property                 | Type           | Default | Description                                                                                   |
|--------------------------|----------------|---------|-----------------------------------------------------------------------------------------------|
| `upgrade_on_startup`     | `true`/`false` | `false` | Run `apt-get upgrade` during container startup (applied in before-exec)                       |
| `terminate_existing_vnc` | `true`/`false` | `false` | Terminate any running VNC server before starting a new one (prevents "already running" error) |

## Shell scripts

| Script               | Location      | Purpose                                                                                                  |
|----------------------|---------------|----------------------------------------------------------------------------------------------------------|
| `setup_container.sh` | `scripts/sh/` | Install/verify container packages (`xfce4`, `tightvncserver`, `python3-poetry`, etc.)                    |
| `install_firefox.sh` | `scripts/sh/` | Install/upgrade Firefox from the official Mozilla repository (avoids Ubuntu's snap transitional package) |
| `setup_vnc.sh`       | `scripts/sh/` | One-time VNC password (default: `termux`) and `xstartup` creation                                        |
| `start_vnc.sh`       | `scripts/sh/` | Start VNC server with configurable geometry (`VNC_GEOMETRY`, default `1920x1080`)                        |
| `terminate_vnc.sh`   | `scripts/sh/` | Gracefully terminate a running VNC server (cleans up lock, PID, and log files)                           |
| `proot_listener.sh`  | `scripts/sh/` | Fifo-based command listener that runs inside the container                                               |
