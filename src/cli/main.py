"""Main CLI entry point"""

import asyncio
from pathlib import Path
from datetime import datetime
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from dotenv import load_dotenv

from ..core.cv_parser import load_cv
from ..core.jd_parser import parse_jd_text
from ..evaluators.gemini_evaluator import GeminiEvaluator

load_dotenv()

app = typer.Typer(
    name="career-forge",
    help="AI-powered job search pipeline with Gemini"
)
console = Console()


@app.command()
def eval(
    jd: str = typer.Argument(
        ...,
        help="Job description (text, URL, or file path)"
    ),
    cv: str = typer.Option(
        "data/cv.md",
        help="Path to CV file"
    ),
    company: str = typer.Option(
        "Unknown",
        help="Company name"
    ),
):
    """Evaluate a job match against your CV"""
    
    console.print(Panel.fit(
        "[bold cyan]🚀 Career-Forge Job Evaluation[/bold cyan]",
        border_style="blue"
    ))
    
    # Load CV
    console.print("[cyan]📄 Loading CV...[/cyan]")
    try:
        cv_obj = load_cv(cv)
        cv_text = cv_obj.to_markdown()
        console.print(f"[green]✓[/green] Loaded CV for {cv_obj.name}")
    except FileNotFoundError:
        console.print(f"[red]✗ CV file not found: {cv}[/red]")
        raise typer.Exit(1)
    
    # Parse JD
    console.print("[cyan]🔍 Parsing job description...[/cyan]")
    
    try:
        if jd.startswith('http'):
            # URL provided (Playwright coming soon)
            console.print(f"[yellow]⚠️ URL support coming soon; using text parsing[/yellow]")
            jd_obj = parse_jd_text(jd, company=company)
        elif Path(jd).exists():
            # File path
            with open(jd, 'r') as f:
                jd_text = f.read()
            jd_obj = parse_jd_text(jd_text, company=company)
        else:
            # Plain text
            jd_obj = parse_jd_text(jd, company=company)
        
        console.print(f"[green]✓[/green] Parsed: {jd_obj.title} @ {jd_obj.company}")
    except Exception as e:
        console.print(f"[red]✗ Error parsing JD: {e}[/red]")
        raise typer.Exit(1)
    
    # Evaluate
    console.print("[cyan]🤖 Evaluating with Gemini...[/cyan]")
    
    try:
        async def run_eval():
            evaluator = GeminiEvaluator()
            return await evaluator.evaluate(
                cv_text,
                jd_obj.description,
                jd_obj.company,
                jd_obj.title,
                jd_obj.url
            )
        
        evaluation = asyncio.run(run_eval())
        
    except Exception as e:
        console.print(f"[red]✗ Evaluation failed: {e}[/red]")
        raise typer.Exit(1)
    
    # Display results
    console.print()
    console.print(Panel.fit(
        f"[bold green]✅ Evaluation Complete[/bold green]\n"
        f"[bold]{jd_obj.company}[/bold] • {jd_obj.title}",
        border_style="green"
    ))
    
    # Scores table
    console.print("\n[bold cyan]📊 Dimension Scores:[/bold cyan]")
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Dimension", style="cyan")
    table.add_column("Score", style="magenta")
    table.add_column("Rating", style="yellow")
    
    scores_list = [
        ("Role Match", evaluation.scores.role_match),
        ("CV Match", evaluation.scores.cv_match),
        ("Level Fit", evaluation.scores.level_fit),
        ("Comp Research", evaluation.scores.comp_research),
        ("Personalization", evaluation.scores.personalization),
        ("Interview Prep", evaluation.scores.interview_prep),
    ]
    
    for dimension, score in scores_list:
        rating = get_rating(score)
        table.add_row(dimension, f"{score}/5.0", rating)
    
    console.print(table)
    
    # Composite score
    composite = evaluation.scores.composite
    composite_rating = get_rating(composite)
    console.print()
    console.print(f"[bold]Composite Score: {composite}/5.0[/bold] {composite_rating}")
    console.print(f"[bold]Recommendation: {evaluation.recommendation}[/bold]")
    
    # Save report
    console.print("\n[cyan]💾 Saving report...[/cyan]")
    report_path = Path("reports") / format_filename(
        f"{jd_obj.company}-{jd_obj.title}"
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    report_content = format_report(evaluation, jd_obj)
    report_path.write_text(report_content)
    
    console.print(f"[green]✓[/green] Report saved to: [bold]{report_path}[/bold]")
    console.print()


@app.command()
def version():
    """Show version and info"""
    console.print("career-forge v0.1.0")
    console.print("AI job search pipeline with Gemini API")


def get_rating(score: float) -> str:
    """Convert score to emoji rating"""
    if score >= 4.5:
        return "⭐⭐⭐⭐⭐"
    elif score >= 4.0:
        return "⭐⭐⭐⭐"
    elif score >= 3.0:
        return "⭐⭐⭐"
    elif score >= 2.0:
        return "⭐⭐"
    else:
        return "⭐"


def format_filename(text: str) -> str:
    """Convert text to safe filename"""
    return text.replace(" ", "-").replace("@", "at").lower() + ".md"


def format_report(evaluation, jd_obj) -> str:
    """Format evaluation as markdown report"""
    
    report_lines = [
        f"# {jd_obj.company} - {jd_obj.title}",
        "",
        f"**URL:** {jd_obj.url or 'N/A'}",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Score:** {evaluation.scores.composite} / 5.0",
        f"**Recommendation:** {evaluation.recommendation}",
        "",
        "## Dimension Scores",
        "",
        f"- Role Match: {evaluation.scores.role_match} / 5",
        f"- CV Match: {evaluation.scores.cv_match} / 5",
        f"- Level Fit: {evaluation.scores.level_fit} / 5",
        f"- Comp Research: {evaluation.scores.comp_research} / 5",
        f"- Personalization: {evaluation.scores.personalization} / 5",
        f"- Interview Prep: {evaluation.scores.interview_prep} / 5",
        "",
        "## Analysis",
        "",
        "### Role Summary",
        evaluation.role_summary,
        "",
        "### CV Match",
        evaluation.cv_match_analysis,
        "",
        "### Level Strategy",
        evaluation.level_strategy,
        "",
        "### Compensation Insights",
        evaluation.comp_insights,
        "",
        "### Tailoring Suggestions",
        evaluation.tailoring_suggestions,
        "",
        "### Interview Preparation",
        evaluation.interview_tips,
        "",
    ]
    
    return "\n".join(report_lines)


if __name__ == "__main__":
    app()
