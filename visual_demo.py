#!/usr/bin/env python3
"""Visual demonstration of what the system produces."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich import box

console = Console()

def show_system_flow():
    """Show the data flow through the system."""
    console.print("\n[bold cyan]System Data Flow:[/bold cyan]\n")

    tree = Tree("🎯 [bold]Customer Language Mining System[/bold]")

    # Input
    input_branch = tree.add("📥 [yellow]INPUT[/yellow]")
    input_branch.add("Query: 'weight loss'")
    input_branch.add("Sources: Reddit, Amazon, YouTube")
    input_branch.add("Context: 'Busy professionals aged 30-45'")

    # Scraping
    scrape_branch = tree.add("🔍 [blue]SCRAPING PHASE[/blue]")
    reddit = scrape_branch.add("Reddit: 150 posts + 450 comments")
    reddit.add("r/loseit: 60 posts")
    reddit.add("r/fitness: 45 posts")
    reddit.add("r/keto: 45 posts")

    amazon = scrape_branch.add("Amazon: 200 reviews")
    amazon.add("Protein powders: 100 reviews")
    amazon.add("Fitness trackers: 50 reviews")
    amazon.add("Diet books: 50 reviews")

    youtube = scrape_branch.add("YouTube: 180 comments")
    youtube.add("Workout videos: 100 comments")
    youtube.add("Diet tips: 80 comments")

    # Analysis
    analysis_branch = tree.add("🧠 [magenta]CLAUDE AI ANALYSIS[/magenta]")
    analysis_branch.add("Emotional Patterns: 8 identified")
    analysis_branch.add("Pain Points: 12 identified")
    analysis_branch.add("Desire Triggers: 6 identified")
    analysis_branch.add("Awareness Stages: All 5 mapped")

    # Output
    output_branch = tree.add("📊 [green]OUTPUT[/green]")

    message_map = output_branch.add("Message Map Generated")
    message_map.add("Ad-Ready Hooks: 15 hooks")
    message_map.add("Body Copy Frameworks: 4 frameworks")
    message_map.add("Customer Quotes: 80+ quotes")
    message_map.add("Objection Handlers: 8 objections")

    files = output_branch.add("Files Created")
    files.add("message_map_20240122.json")
    files.add("message_map_20240122.md")
    files.add("message_map_20240122.html")

    console.print(tree)

def show_metrics():
    """Show sample metrics from a run."""
    console.print("\n[bold cyan]Sample Run Metrics:[/bold cyan]\n")

    metrics = Table(title="Processing Statistics", box=box.ROUNDED)
    metrics.add_column("Metric", style="cyan", justify="left")
    metrics.add_column("Value", style="green", justify="right")

    metrics.add_row("Total Items Scraped", "530")
    metrics.add_row("Text Samples Analyzed", "1,247")
    metrics.add_row("Claude API Calls", "3")
    metrics.add_row("Processing Time", "~5 minutes")
    metrics.add_row("Emotional Patterns Found", "8")
    metrics.add_row("Pain Points Identified", "12")
    metrics.add_row("Ad Hooks Generated", "15")
    metrics.add_row("Customer Quotes Extracted", "80+")

    console.print(metrics)

def show_actual_output_value():
    """Show what you actually get."""
    console.print("\n[bold cyan]What You Actually Get:[/bold cyan]\n")

    console.print(Panel(
        "[bold white]1. Emotional Intelligence[/bold white]\n"
        "   • Frustration (high frequency)\n"
        "   • Hope (medium frequency)\n"
        "   • Fear of failure (high frequency)\n"
        "   • Each with real customer quotes\n\n"

        "[bold white]2. Pain Points with Severity[/bold white]\n"
        "   • 'No time for meal prep' (CRITICAL)\n"
        "   • 'Conflicting diet advice' (MAJOR)\n"
        "   • 'Expensive gym memberships' (MINOR)\n"
        "   • All with customer quotes proving the pain\n\n"

        "[bold white]3. Desire Triggers[/bold white]\n"
        "   • 'Lose weight without sacrificing work-life balance'\n"
        "   • 'Feel confident again'\n"
        "   • 'Have energy to play with kids'\n\n"

        "[bold white]4. Stage of Awareness Mapping[/bold white]\n"
        "   • Unaware → Most Aware\n"
        "   • Customer language for each stage\n"
        "   • Specific quotes you can use\n\n"

        "[bold white]5. Ad-Ready Hooks (Copy & Paste)[/bold white]\n"
        "   • 'Working 60 hours? Lose weight without meal prep'\n"
        "   • 'Tired of diets that don't fit your real life?'\n"
        "   • 'Your doctor says lose weight, but who has time?'\n\n"

        "[bold white]6. Body Copy Frameworks[/bold white]\n"
        "   • Problem-Agitate-Solution (with customer words)\n"
        "   • Before-After-Bridge (with real quotes)\n"
        "   • Feature-Advantage-Benefit\n\n"

        "[bold white]7. Objection Handlers[/bold white]\n"
        "   • 'I've tried everything' → How to respond\n"
        "   • 'I don't have time' → How to respond\n"
        "   • 'Too expensive' → How to respond",
        title="Deliverables",
        border_style="green",
        box=box.DOUBLE
    ))

def show_use_cases():
    """Show real-world use cases."""
    console.print("\n[bold cyan]Real-World Use Cases:[/bold cyan]\n")

    use_cases = [
        ("E-commerce Store Owner", "Research product categories to write better product descriptions and ads"),
        ("Ad Agency", "Quick customer research for new client campaigns"),
        ("SaaS Startup", "Understand customer pain points for landing page copy"),
        ("Content Creator", "Find what customers actually care about for content topics"),
        ("Email Marketer", "Get subject lines and hooks that resonate"),
        ("Copywriter", "Research customer language for any niche in minutes"),
    ]

    for role, use_case in use_cases:
        console.print(f"[green]•[/green] [bold]{role}:[/bold] {use_case}")

def main():
    """Run visual demo."""
    console.print(Panel.fit(
        "[bold]Customer Language Mining System[/bold]\n"
        "[dim]Visual Overview of What You Get[/dim]",
        border_style="cyan"
    ))

    show_system_flow()
    show_metrics()
    show_actual_output_value()
    show_use_cases()

    console.print("\n" + "="*80 + "\n")

    console.print(Panel.fit(
        "[bold yellow]The Value:[/bold yellow]\n\n"
        "Instead of spending HOURS manually reading Reddit threads,\n"
        "Amazon reviews, and YouTube comments...\n\n"
        "This system does it in [bold green]5 minutes[/bold green] and gives you:\n"
        "• Exact customer quotes to use in ads\n"
        "• Emotional triggers that drive purchases\n"
        "• Pain points ranked by severity\n"
        "• Ad hooks ready to test\n"
        "• Body copy frameworks with examples\n\n"
        "[bold green]90% research, 10% making ads[/bold green] ← The way it should be!",
        border_style="yellow"
    ))

if __name__ == '__main__':
    main()
