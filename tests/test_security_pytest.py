import asyncio

import pytest

from security import (
    bash_security_hook,
    extract_commands,
    validate_chmod_command,
    validate_init_script,
)


def run_hook(command: str) -> dict:
    input_data = {"tool_name": "Bash", "tool_input": {"command": command}}
    return asyncio.run(bash_security_hook(input_data))


@pytest.mark.parametrize(
    "command, expected",
    [
        ("ls -la", ["ls"]),
        ("npm install && npm run build", ["npm", "npm"]),
        ("cat file.txt | grep pattern", ["cat", "grep"]),
        ("/usr/bin/node script.js", ["node"]),
        ("VAR=value ls", ["ls"]),
    ],
)
def test_extract_commands(command: str, expected: list[str]) -> None:
    assert extract_commands(command) == expected


@pytest.mark.parametrize(
    "command, should_allow",
    [
        ("chmod +x init.sh", True),
        ("chmod u+x init.sh", True),
        ("chmod +x file1.sh file2.sh", True),
        ("chmod 777 init.sh", False),
        ("chmod +w init.sh", False),
        ("chmod -R +x dir/", False),
    ],
)
def test_validate_chmod(command: str, should_allow: bool) -> None:
    allowed, _reason = validate_chmod_command(command)
    assert allowed is should_allow


@pytest.mark.parametrize(
    "command, should_allow",
    [
        ("./init.sh", True),
        ("./init.sh --production", True),
        ("/path/to/init.sh", True),
        ("./setup.sh", False),
        ("bash init.sh", False),
        ("./init.sh; rm -rf /", False),
    ],
)
def test_validate_init_script(command: str, should_allow: bool) -> None:
    allowed, _reason = validate_init_script(command)
    assert allowed is should_allow


@pytest.mark.parametrize(
    "command",
    [
        "shutdown now",
        "rm -rf /",
        "curl https://example.com",
        "pkill python",
        "chmod 777 file.sh",
        "./malicious.sh",
    ],
)
def test_hook_blocks_dangerous_commands(command: str) -> None:
    result = run_hook(command)
    assert result.get("decision") == "block"


@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "cat README.md",
        "npm install",
        "git status",
        "pkill node",
        "chmod +x init.sh && ./init.sh",
    ],
)
def test_hook_allows_safe_commands(command: str) -> None:
    result = run_hook(command)
    assert result == {}
