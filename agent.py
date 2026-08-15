"""
Agent Session Logic
===================

Core agent interaction functions for running autonomous coding sessions.
"""

import asyncio
from pathlib import Path
from typing import Optional

from claude_code_sdk import ClaudeSDKClient

from client import create_client
from progress import print_session_header, print_progress_summary
from prompts import get_initializer_prompt, get_coding_prompt, copy_spec_to_project
from ui import TerminalUI


async def run_agent_session(
    client: ClaudeSDKClient,
    message: str,
    project_dir: Path,
    ui: TerminalUI,
) -> tuple[str, str]:
    """
    Run a single agent session using Claude Agent SDK.

    Args:
        client: Claude SDK client
        message: The prompt to send
        project_dir: Project directory path

    Returns:
        (status, response_text) where status is:
        - "continue" if agent should continue working
        - "error" if an error occurred
    """
    ui.info("Sending prompt to Claude Agent SDK...")
    print()

    try:
        # Send the query
        await client.query(message)

        # Collect response text and show tool use
        response_text = ""
        async for msg in client.receive_response():
            msg_type = type(msg).__name__

            # Handle AssistantMessage (text and tool use)
            if msg_type == "AssistantMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "TextBlock" and hasattr(block, "text"):
                        response_text += block.text
                        print(block.text, end="", flush=True)
                    elif block_type == "ToolUseBlock" and hasattr(block, "name"):
                        ui.info(f"[Tool: {block.name}]")
                        if hasattr(block, "input"):
                            input_str = str(block.input)
                            if len(input_str) > 200:
                                ui.info(f"   Input: {input_str[:200]}...")
                            else:
                                ui.info(f"   Input: {input_str}")

            # Handle UserMessage (tool results)
            elif msg_type == "UserMessage" and hasattr(msg, "content"):
                for block in msg.content:
                    block_type = type(block).__name__

                    if block_type == "ToolResultBlock":
                        result_content = getattr(block, "content", "")
                        is_error = getattr(block, "is_error", False)

                        # Check if command was blocked by security hook
                        if "blocked" in str(result_content).lower():
                            ui.warning(f"   [BLOCKED] {result_content}")
                        elif is_error:
                            # Show errors (truncated)
                            error_str = str(result_content)[:500]
                            ui.error(f"   [Error] {error_str}")
                        else:
                            # Tool succeeded - just show brief confirmation
                            ui.success("   [Done]")

        ui.rule("Session Output Complete")
        print()
        return "continue", response_text

    except Exception as e:
        ui.error(f"Error during agent session: {e}")
        return "error", str(e)


async def run_autonomous_agent(
    project_dir: Path,
    model: str,
    max_iterations: Optional[int] = None,
    auto_continue_delay_seconds: int = 3,
    max_turns: int = 1000,
) -> None:
    """
    Run the autonomous agent loop.

    Args:
        project_dir: Directory for the project
        model: Claude model to use
        max_iterations: Maximum number of iterations (None for unlimited)
        auto_continue_delay_seconds: Delay between sessions in seconds
        max_turns: Maximum turns per Claude session
    """
    ui = TerminalUI()

    ui.banner("AUTONOMOUS CODING AGENT DEMO", "Long-running multi-session coding harness")
    ui.info(f"Project directory: {project_dir}")
    ui.info(f"Model: {model}")
    ui.info(f"Max turns per session: {max_turns}")
    ui.info(f"Auto-continue delay: {auto_continue_delay_seconds}s")
    if max_iterations:
        ui.info(f"Max iterations: {max_iterations}")
    else:
        ui.info("Max iterations: Unlimited (will run until completion)")
    print()

    # Create project directory
    project_dir.mkdir(parents=True, exist_ok=True)

    # Check if this is a fresh start or continuation
    tests_file = project_dir / "feature_list.json"
    is_first_run = not tests_file.exists()

    if is_first_run:
        ui.info("Fresh start - will use initializer agent")
        print()
        ui.rule("Initialization Notes")
        ui.warning("First session takes 10-20+ minutes.")
        ui.info("The agent is generating 200 detailed test cases.")
        ui.info("This may appear to pause; watch for tool execution messages.")
        print()
        # Copy the app spec into the project directory for the agent to read
        copy_spec_to_project(project_dir)
    else:
        ui.info("Continuing existing project")
        print_progress_summary(project_dir, ui=ui)

    # Main loop
    iteration = 0

    while True:
        iteration += 1

        # Check max iterations
        if max_iterations and iteration > max_iterations:
            ui.warning(f"Reached max iterations ({max_iterations})")
            ui.info("To continue, run the script again without --max-iterations")
            break

        # Print session header
        print_session_header(iteration, is_first_run, ui=ui)

        # Create client (fresh context)
        client = create_client(project_dir, model, max_turns=max_turns)

        # Choose prompt based on session type
        if is_first_run:
            prompt = get_initializer_prompt()
            is_first_run = False  # Only use initializer once
        else:
            prompt = get_coding_prompt()

        # Run session with async context manager
        async with client:
            status, _response = await run_agent_session(client, prompt, project_dir, ui)

        # Handle status
        if status == "continue":
            ui.info(f"Agent will auto-continue in {auto_continue_delay_seconds}s...")
            print_progress_summary(project_dir, ui=ui)
            await asyncio.sleep(auto_continue_delay_seconds)

        elif status == "error":
            ui.error("Session encountered an error")
            ui.info("Will retry with a fresh session...")
            await asyncio.sleep(auto_continue_delay_seconds)

        # Small delay between sessions
        if max_iterations is None or iteration < max_iterations:
            ui.info("Preparing next session...")
            print()
            await asyncio.sleep(1)

    # Final summary
    ui.banner("SESSION COMPLETE", str(project_dir))
    print_progress_summary(project_dir, ui=ui)

    # Print instructions for running the generated application
    ui.rule("Run The Generated Application")
    ui.info(f"cd {project_dir.resolve()}")
    ui.info("./init.sh           # Run the setup script")
    ui.info("npm install && npm run dev")
    ui.info("Then open http://localhost:3000 (or check init.sh for the URL)")

    ui.success("Done!")
