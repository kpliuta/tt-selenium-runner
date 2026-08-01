# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- Unit tests for `src/before_exec.py` (`tests/unit/test_before_exec.py`).

### Fixed

- before-exec now exports `DISPLAY=:1` inside the container before VNC setup, so tasks running in the container share one consolidated display value with the VNC server (previously only VNC scripts defaulted to `:1`, while task processes had no `DISPLAY`).

## [0.1.5] - 2026-08-01

### Added

- Unit tests for `build_env_prefix` (`tests/unit/test_task_exec.py`).
- pytest step enabled in CI.

### Fixed

- task-exec now passes both runner and task parameters plus `MNT_OUTPUT_DIR` into the container as a shell-quoted env-assignment command prefix (e.g. `MNT_OUTPUT_DIR=... VAR_1=1 poetry run python src/main.py`), so tasks can read their own properties (`src/main.py` previously only saw runner properties).
- before-task `cd` now shell-quotes the task dir path, so task directory names containing spaces or shell metacharacters are handled safely.

## [0.1.4] - 2026-07-31

### Changed

- Moved Python source from `scripts/` to `src/` and shell scripts from `scripts/sh/` to `sh/`.
- Task entry point is now `src/main.py` (task-exec command and entry point task validator updated).

## [0.1.3] - 2026-07-29

### Added

- tt-selenium-cita-extranjeria-alert-task to bundled.toml.

## [0.1.2] - 2026-07-15

### Fixed

- metadata.toml version now stays in sync with pyproject.toml during releases

## [0.1.1] - 2026-07-14

### Added

- Integration with mypy and autoflake
- CI workflow and release process
