# tt-selenium-runner

A Selenium runner for [termux-tasker](https://github.com/kpliuta/termux-tasker).

Manages a `proot-distro` Ubuntu container with VNC and Firefox to execute
Selenium-based Python tasks on Android via Termux.

## Lifecycle

1. **initialization** — Install proot-distro, Ubuntu container, VNC, and Firefox (honours `upgrade_on_startup` property)
2. **before-exec** — Start proot-distro in background with fifo command listener, start VNC
3. **before-task** — `poetry install` on the task directory
4. **task-exec** — `poetry run` on the task with `MNT_OUTPUT_DIR` env var
5. **after-exec** — Gracefully shut down proot session

## Configuration

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `upgrade_on_startup` | `true`/`false` | `false` | Run `apt-get upgrade` during container initialization |
