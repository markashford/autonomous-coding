# Architecture

## Goal

This harness runs autonomous coding sessions over long time windows while
preserving progress and enforcing security controls for agent tool usage.

## Runtime Flow

1. CLI parses args and environment defaults.
2. Project directory is resolved and created if needed.
3. Session type is selected:
   - Initializer session for fresh projects.
   - Coding session for continuation runs.
4. A fresh Claude SDK client is created per session.
5. Security policy and hooks gate tool usage during execution.
6. Session output is streamed to terminal with progress summaries.
7. Loop continues until completion, interrupt, or max iterations.

## Main Components

- autonomous_agent_demo.py
  - Entry point.
  - Input validation.
  - Runtime settings binding.

- agent.py
  - Autonomous session loop.
  - Prompt selection.
  - Progress and completion reporting.

- client.py
  - Claude client options.
  - Tool allowlist.
  - Sandbox and permission settings.

- security.py
  - Command extraction and parsing.
  - Allowlist validation.
  - Extra checks for sensitive commands.

- settings.py
  - Environment variable defaults.
  - Safe integer parsing.
  - Project path normalization.

- ui.py and progress.py
  - Terminal rendering.
  - Passing/total feature summaries.

## Security Design

The implementation follows defense in depth:

1. Sandbox: isolate bash command execution context.
2. Scope controls: limit filesystem operations to project paths.
3. Allowlist: permit only approved shell commands.
4. Command hardening: add dedicated validation rules for high-risk commands.

## Testing Strategy

- tests/test_security_pytest.py: fast pytest suite for core security behavior.
- test_security.py: script-friendly regression checks and output readability.
- .github/workflows/ci.yml: CI matrix testing across Python versions.

## Operational Concerns

- Initializer sessions can be long (feature planning and project setup).
- Continuation sessions are intentionally isolated by creating fresh clients.
- Docker Compose setup keeps generated artifacts mounted to host folders.
