import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from .core import BatchAnalyzer
from .report import ReportGenerator
from .models import ImputationStatus

app = typer.Typer(
    name="hla-analyst",
    help="Enterprise-grade HLA Imputation Pipeline Analyst",
    add_completion=False,
)
console = Console()

@app.command()
def analyze(
    batch_dir: Path = typer.Argument(..., help="Directory containing the imputation batch"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Path to save the report"),
    format: str = typer.Option("text", "--format", "-f", help="Output format: text, json, html"),
    compare: Optional[Path] = typer.Option(None, "--compare", "-c", help="Reference batch directory for comparison"),
):
    """
    Analyze a single imputation batch for errors, consistency, and artifacts.
    """
    console.print(Panel(f"Analyzing Batch: [bold blue]{batch_dir}[/bold blue]", title="HLA Analyst"))

    try:
        analyzer = BatchAnalyzer(batch_dir)
        metrics = analyzer.analyze()

        # Display Summary
        status_color = {
            ImputationStatus.SUCCESS: "green",
            ImputationStatus.FAILURE: "red",
            ImputationStatus.WARNING: "yellow",
            ImputationStatus.UNKNOWN: "white",
        }[metrics.status]

        console.print(f"Status: [bold {status_color}]{metrics.status.value}[/bold {status_color}]")
        
        if metrics.errors:
            console.print("\n[bold red]Errors Found:[/bold red]")
            for err in metrics.errors:
                console.print(f"  ❌ {err}")

        if metrics.warnings:
            console.print("\n[bold yellow]Warnings:[/bold yellow]")
            for warn in metrics.warnings:
                console.print(f"  ⚠️ {warn}")

        if metrics.command:
            console.print("\n[bold]Reconstructed Command:[/bold]")
            console.print(f"  [dim]{metrics.command.raw_command}[/dim]")

        # Comparison Logic
        if compare:
            console.print(f"\n[bold]Comparing with reference:[/bold] {compare}")
            comparison = analyzer.compare_with(compare)
            if comparison.identical_scripts:
                console.print("  ✅ SNP2HLA Scripts are identical")
            else:
                console.print("  ❌ SNP2HLA Scripts differ")

        # Output Generation
        if output:
            if format.lower() == "json":
                ReportGenerator.generate_json(metrics, output)
                console.print(f"\nJSON report saved to: {output}")
            elif format.lower() == "html":
                ReportGenerator.generate_html(metrics, output)
                console.print(f"\nHTML report saved to: {output}")
            else:
                # Text output is already printed to console, maybe save to file?
                pass

    except Exception as e:
        console.print(f"[bold red]Fatal Error:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def validate(
    batch_dir: Path = typer.Argument(..., help="Directory to validate"),
):
    """
    Quick validation check (exit code 0 for success, 1 for failure).
    """
    try:
        analyzer = BatchAnalyzer(batch_dir)
        metrics = analyzer.analyze()
        if metrics.status == ImputationStatus.FAILURE:
            raise typer.Exit(code=1)
        typer.Exit(code=0)
    except Exception:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
