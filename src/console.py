from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.theme import Theme

# ── Shared Console Instance ──────────────────────────────────────

custom_theme = Theme({
    "step": "bold cyan",
    "success": "bold green",
    "error": "bold red",
    "info": "dim",
})

console = Console(theme=custom_theme)


# ── Helper Functions ─────────────────────────────────────────────

def print_header(text):
    """Display a styled header panel."""
    panel = Panel(
        Text(text, justify="center"),
        style="bold white",
        border_style="bright_cyan",
        padding=(1, 2),
    )
    console.print(panel)


def print_step(step_number, total_steps, text):
    """Display a step indicator."""
    console.print(f"\n [step]▸ Step {step_number}/{total_steps}[/step] — {text}")


def print_success(text):
    """Display a success message."""
    console.print(f" [success]✓[/success] {text}")


def print_error(text):
    """Display an error message."""
    console.print(f" [error]✗[/error] {text}")


def print_info(text):
    """Display an info/dim message."""
    console.print(f" [info]{text}[/info]")
