"""CLI entry point for claudiminder."""

from __future__ import annotations

import json
import sys

import typer
from loguru import logger

from .api.usage import get_usage_sync, is_token_expired
from .utils.credentials import is_token_available

app = typer.Typer(
    name="claudiminder",
    help="Claude usage tracking & reminder tool",
    no_args_is_help=True,
)


def setup_logging(debug: bool = False) -> None:
    """Configure loguru logging."""
    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level, format="{time:HH:mm:ss} | {level} | {message}")


@app.command()
def status(
    json_output: bool = typer.Option(False, "--json", "-j", help="Output as JSON"),
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug logging"),
) -> None:
    """Show current Claude usage status."""
    setup_logging(debug)

    if not is_token_available():
        if json_output:
            print(json.dumps({"error": "No OAuth token found", "token_expired": True}))
        else:
            typer.echo("❌ No OAuth token found. Please login to Claude.")
        raise typer.Exit(1)

    usage = get_usage_sync()

    if usage is None:
        if json_output:
            print(json.dumps({"error": "Failed to fetch usage", "token_expired": is_token_expired()}))
        else:
            if is_token_expired():
                typer.echo("❌ Token expired. Please re-login to Claude.")
            else:
                typer.echo("❌ Failed to fetch usage data.")
        raise typer.Exit(1)

    if json_output:
        print(usage.model_dump_json(indent=2))
    else:
        if usage.five_hour:
            pct = usage.five_hour.utilization * 100
            typer.echo(f"📊 Usage: {pct:.1f}%")
            typer.echo(f"🔄 Resets at: {usage.five_hour.resets_at}")
        else:
            typer.echo("⚠️ No usage data available")


@app.command()
def tui() -> None:
    """Launch interactive TUI mode."""
    typer.echo("TUI mode not yet implemented")
    raise typer.Exit(0)


@app.command()
def version() -> None:
    """Show version information."""
    from . import __version__
    typer.echo(f"claudiminder v{__version__}")


def main() -> None:
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
