"""Command-line interface (``hla-analyst``)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from .core import BatchAnalyzer
from .models import ImputationStatus
from .report import ReportGenerator

app = typer.Typer(
    name="hla-analyst",
    help="Health checks for SNP2HLA / Beagle HLA imputation run directories.",
    add_completion=False,
)
console = Console()

STATUS_STYLE = {
    ImputationStatus.SUCCESS: "green",
    ImputationStatus.FAILURE: "red",
    ImputationStatus.WARNING: "yellow",
    ImputationStatus.UNKNOWN: "white",
}


@app.command()
def analyze(
    batch_dir: Annotated[Path, typer.Argument(help="Directory containing one run")],
    output: Annotated[
        Path | None, typer.Option("--output", "-o", help="Report path")
    ] = None,
    fmt: Annotated[
        str, typer.Option("--format", "-f", help="Report format: text, json or html")
    ] = "text",
    compare: Annotated[
        Path | None,
        typer.Option("--compare", "-c", help="Reference run directory to compare with"),
    ] = None,
) -> None:
    """Analyse one run directory and optionally compare it with a reference."""
    try:
        analyzer = BatchAnalyzer(batch_dir)
        metrics = analyzer.analyze()
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=2) from exc

    style = STATUS_STYLE[metrics.status]
    console.print(f"Batch: {metrics.batch_id}")
    console.print(f"Status: [bold {style}]{metrics.status.value}[/bold {style}]")
    console.print(
        f"Required outputs found: "
        f"{len(BatchAnalyzer.REQUIRED_ARTIFACTS) - len(metrics.missing_artifacts)}"
        f"/{len(BatchAnalyzer.REQUIRED_ARTIFACTS)}"
    )
    for err in metrics.errors:
        console.print(f"  [red]error[/red]   {err}", highlight=False)
    for warn in metrics.warnings:
        console.print(f"  [yellow]warning[/yellow] {warn}", highlight=False)
    if metrics.command:
        console.print(f"Beagle command: {metrics.command.raw_command}", highlight=False)

    if compare:
        result = analyzer.compare_with(compare)
        console.print(f"\nCompared with reference: {result.target_batch}")
        same = "identical" if result.identical_scripts else "different"
        console.print(f"  SNP2HLA.csh: {same}")
        for key, values in result.parameter_diffs.items():
            console.print(
                f"  set {key}: this={values['this']} reference={values['reference']}",
                highlight=False,
            )
        for missing in result.missing_vs_reference:
            console.print(f"  missing here but present in reference: {missing}")

    if output:
        writers = {
            "text": ReportGenerator.generate_text,
            "json": ReportGenerator.generate_json,
            "html": ReportGenerator.generate_html,
        }
        if fmt.lower() not in writers:
            console.print(f"[red]Unknown format:[/red] {fmt}")
            raise typer.Exit(code=2)
        writers[fmt.lower()](metrics, output)
        console.print(f"Report written to {output}")


@app.command()
def validate(
    batch_dir: Annotated[Path, typer.Argument(help="Directory to validate")],
) -> None:
    """Exit 0 unless the run has errors (for use in scripts and CI)."""
    try:
        metrics = BatchAnalyzer(batch_dir).analyze()
    except FileNotFoundError as exc:
        raise typer.Exit(code=2) from exc
    if metrics.status == ImputationStatus.FAILURE:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
