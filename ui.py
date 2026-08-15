"""
Terminal UI helpers for a cleaner CLI experience.
"""

from __future__ import annotations

from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
except ImportError:  # pragma: no cover - graceful fallback when rich is unavailable
    Console = None
    Panel = None
    Table = None


class TerminalUI:
    """Wrapper around rich with a plain-text fallback."""

    def __init__(self) -> None:
        self.console = Console(highlight=False) if Console is not None else None

    def banner(self, title: str, subtitle: str = "") -> None:
        if self.console and Panel is not None:
            body = title if not subtitle else f"{title}\n{subtitle}"
            self.console.print(Panel.fit(body, border_style="cyan", padding=(1, 2)))
            return

        print("\n" + "=" * 70)
        print(f"  {title}")
        if subtitle:
            print(f"  {subtitle}")
        print("=" * 70 + "\n")

    def rule(self, title: str) -> None:
        if self.console:
            self.console.rule(f"[bold cyan]{title}")
            return

        print("\n" + "-" * 70)
        print(f"  {title}")
        print("-" * 70)

    def info(self, message: str) -> None:
        if self.console:
            self.console.print(f"[cyan]i[/cyan] {message}")
            return
        print(message)

    def success(self, message: str) -> None:
        if self.console:
            self.console.print(f"[green]OK[/green] {message}")
            return
        print(message)

    def warning(self, message: str) -> None:
        if self.console:
            self.console.print(f"[yellow]![/yellow] {message}")
            return
        print(message)

    def error(self, message: str) -> None:
        if self.console:
            self.console.print(f"[red]x[/red] {message}")
            return
        print(message)

    def progress_summary(self, passing: int, total: int) -> None:
        if total <= 0:
            self.info("Progress: feature_list.json not yet created")
            return

        percentage = (passing / total) * 100

        if self.console and Table is not None:
            table = Table(title="Current Progress", show_header=True, header_style="bold blue")
            table.add_column("Metric")
            table.add_column("Value", justify="right")
            table.add_row("Passing tests", str(passing))
            table.add_row("Total tests", str(total))
            table.add_row("Completion", f"{percentage:.1f}%")
            self.console.print(table)
            return

        print(f"Progress: {passing}/{total} tests passing ({percentage:.1f}%)")

    def session_header(self, session_num: int, session_type: str) -> None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.rule(f"Session {session_num}: {session_type}")
        self.info(f"Started at {timestamp}")
