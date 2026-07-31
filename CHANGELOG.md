# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

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
