#!/usr/bin/env python3
"""
Autonomous Coding Agent Demo
============================

A minimal harness demonstrating long-running autonomous coding with Claude.
This script implements the two-agent pattern (initializer + coding agent) and
incorporates all the strategies from the long-running agents guide.

Example Usage:
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo
    python autonomous_agent_demo.py --project-dir ./claude_clone_demo --max-iterations 5
"""

import argparse
import asyncio
import os
from pathlib import Path

from agent import run_autonomous_agent
from settings import AppSettings, load_settings, resolve_project_dir
from ui import TerminalUI


def parse_args(settings: AppSettings) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Autonomous Coding Agent Demo - Long-running agent harness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start fresh project
  python autonomous_agent_demo.py --project-dir ./claude_clone

  # Use a specific model
  python autonomous_agent_demo.py --project-dir ./claude_clone --model claude-sonnet-4-5-20250929

  # Limit iterations for testing
  python autonomous_agent_demo.py --project-dir ./claude_clone --max-iterations 5

  # Continue existing project
  python autonomous_agent_demo.py --project-dir ./claude_clone

Environment Variables:
  ANTHROPIC_API_KEY    Your Anthropic API key (required)
  AUTONOMOUS_DEFAULT_MODEL
  AUTONOMOUS_AUTO_CONTINUE_DELAY_SECONDS
  AUTONOMOUS_MAX_TURNS
  AUTONOMOUS_GENERATIONS_DIR
        """,
    )

    parser.add_argument(
        "--project-dir",
        type=Path,
        default=Path("./autonomous_demo_project"),
        help=f"Directory for the project (default root: {settings.generations_root}/). Relative paths are placed under this root.",
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=None,
        help="Maximum number of agent iterations (default: unlimited)",
    )

    parser.add_argument(
        "--auto-continue-delay",
        type=int,
        default=settings.auto_continue_delay_seconds,
        help=(
            "Delay in seconds between sessions "
            f"(default: {settings.auto_continue_delay_seconds})"
        ),
    )

    parser.add_argument(
        "--max-turns",
        type=int,
        default=settings.max_turns,
        help=f"Max turns per agent session (default: {settings.max_turns})",
    )

    parser.add_argument(
        "--model",
        type=str,
        default=settings.default_model,
        help=f"Claude model to use (default: {settings.default_model})",
    )

    return parser.parse_args()


def main() -> None:
    """Main entry point."""
    settings = load_settings()
    args = parse_args(settings)
    ui = TerminalUI()

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        ui.error("ANTHROPIC_API_KEY environment variable not set")
        ui.info("Get your API key from: https://console.anthropic.com/")
        ui.info("Then set it: export ANTHROPIC_API_KEY='your-api-key-here'")
        return

    # Automatically place projects under configured generations root.
    project_dir = resolve_project_dir(args.project_dir, settings.generations_root)

    if args.auto_continue_delay < 1:
        ui.warning("--auto-continue-delay must be >= 1; using 1 second")
        args.auto_continue_delay = 1

    if args.max_turns < 1:
        ui.warning("--max-turns must be >= 1; using 1")
        args.max_turns = 1

    # Run the agent
    try:
        asyncio.run(
            run_autonomous_agent(
                project_dir=project_dir,
                model=args.model,
                max_iterations=args.max_iterations,
                auto_continue_delay_seconds=args.auto_continue_delay,
                max_turns=args.max_turns,
            )
        )
    except KeyboardInterrupt:
        ui.warning("Interrupted by user")
        ui.info("To resume, run the same command again")
    except Exception as e:
        ui.error(f"Fatal error: {e}")
        raise


if __name__ == "__main__":
    main()
