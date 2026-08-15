# Autonomous Coding Agent Harness

[![CI](https://img.shields.io/github/actions/workflow/status/your-username/autonomous-coding/ci.yml?branch=main&label=CI)](#testing-and-quality)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#quick-start-local)
[![Docker](https://img.shields.io/badge/Container-Ready-informational)](#quick-start-docker)

Production-style autonomous coding harness built around the Claude Agent SDK.
It runs a two-phase agent workflow (initializer + coding agent), preserves state
between sessions, enforces command-level security controls, and includes CI,
tests, and containerized execution.

This repository is designed to be portfolio-friendly: clear architecture,
incremental development workflow, and operational tooling you can demo quickly.


## System Overview

1. Session 1 runs an initializer agent using the app specification.
2. The initializer creates project scaffolding plus feature-driven test plans.
3. Follow-up sessions run a coding agent that implements pending features.
4. Progress is persisted in generated artifacts, so runs can resume cleanly.

## Architecture

Core modules:

- autonomous_agent_demo.py: CLI entry point and runtime orchestration.
- agent.py: autonomous loop, per-session execution, and lifecycle handling.
- client.py: Claude SDK client creation, security settings, and hooks.
- security.py: allowlist-based bash validation and sensitive command checks.
- settings.py: environment-driven defaults and project path resolution.
- ui.py: rich terminal output with graceful fallback to plain text.
- progress.py: feature pass-rate summary for generated projects.

## Quick Start (Local)

1. Install dependencies:

```bash
python3 -m pip install -r requirements-dev.txt
```

2. Set API key:

```bash
export ANTHROPIC_API_KEY="your-api-key"
```

3. Run one short iteration (safe smoke test):

```bash
python3 autonomous_agent_demo.py --project-dir demo_app --max-iterations 1
```

Generated output is written under generations by default.

## Quick Start (Docker)

1. Build image:

```bash
docker compose build
```

2. Run containerized agent:

```bash
ANTHROPIC_API_KEY="your-api-key" docker compose run --rm autonomous-agent
```

The compose setup mounts generations and logs for persistence between runs.

## CLI Options

| Option | Description | Default |
| --- | --- | --- |
| --project-dir | Target generated project directory | autonomous_demo_project |
| --max-iterations | Upper bound on autonomous sessions | unlimited |
| --auto-continue-delay | Delay in seconds between sessions | 3 |
| --max-turns | Max Claude turns per session | 1000 |
| --model | Claude model to use | claude-sonnet-4-5-20250929 |

## Environment Variables

| Variable | Purpose | Default |
| --- | --- | --- |
| ANTHROPIC_API_KEY | Required API key | none |
| AUTONOMOUS_DEFAULT_MODEL | Default CLI model value | claude-sonnet-4-5-20250929 |
| AUTONOMOUS_AUTO_CONTINUE_DELAY_SECONDS | Default delay between sessions | 3 |
| AUTONOMOUS_MAX_TURNS | Default max turns per session | 1000 |
| AUTONOMOUS_GENERATIONS_DIR | Base directory for relative project paths | generations |

Use .env.example as a starting point for local configuration.

## Security Model

The harness applies layered protections around agent tool execution:

1. Sandboxed bash execution in Claude settings.
2. Filesystem scope restricted to project workspace.
3. Bash command allowlist in security.py.
4. Extra validation for potentially risky commands:
   pkill, chmod, and init.sh execution.

Commands outside policy are blocked before execution.

## Testing And Quality

Run tests locally:

```bash
pytest
python3 test_security.py
```

CI pipeline:

- GitHub Actions workflow in .github/workflows/ci.yml.
- Matrix testing on Python 3.10, 3.11, and 3.12.

## Developer Commands

Common tasks are available through Make:

```bash
make install
make install-dev
make test
make test-legacy
make run
make docker-build
make docker-run
```

## Typical Generated Output

```text
generations/my_project/
|- feature_list.json
|- app_spec.txt
|- init.sh
|- claude-progress.txt
|- .claude_settings.json
`- application source files
```

## Customization Guide

- Update prompts/app_spec.txt to target a different application domain.
- Edit prompts/initializer_prompt.md to adjust initial feature volume.
- Tune allowed shell commands in security.py for your policy boundaries.
- Override runtime defaults through environment variables for experiments.

## Notes For Public GitHub Publishing

- Keep API keys out of commits and CI logs.
- Add your preferred open-source license before publishing publicly.
- Replace badge owner/repo placeholders with your actual GitHub repository.

## Acknowledgment

Built as an autonomous coding harness around the Claude Agent SDK with a focus
on reproducibility, safety, and portfolio-grade engineering practices.
