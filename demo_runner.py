#!/usr/bin/env python3
"""
Demo runner for Customer Language Mining System
Shows how the system works with sample data
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
import json

console = Console()

def show_system_overview():
    """Show system overview."""
    console.print(Panel.fit(
        "[bold cyan]Customer Language Mining System - Demo[/bold cyan]\n\n"
        "This system automates customer research by:\n"
        "1. 🔍 Scraping customer language from Reddit, Amazon, YouTube\n"
        "2. 🧠 Analyzing with Claude AI for emotional patterns & pain points\n"
        "3. 📊 Organizing by stage of awareness\n"
        "4. 📝 Generating ad-ready hooks and copy frameworks",
        title="Welcome",
        border_style="green"
    ))

def show_cli_usage():
    """Show CLI usage examples."""
    console.print("\n[bold]Command-Line Usage Examples:[/bold]\n")

    examples = [
        ("Basic Reddit Search", 'python main.py "weight loss" --reddit "loseit,fitness"'),
        ("Amazon Reviews", 'python main.py "protein powder" --amazon'),
        ("Multiple Sources", 'python main.py "fitness tracker" --reddit "fitness" --amazon --youtube'),
        ("With Context", 'python main.py "project management" --reddit "productivity" --context "B2B SaaS"'),
    ]

    for title, cmd in examples:
        console.print(f"[cyan]• {title}:[/cyan]")
        console.print(f"  [dim]{cmd}[/dim]\n")

def show_sample_data():
    """Show sample scraped data structure."""
    console.print("\n[bold]Sample Scraped Data Structure:[/bold]\n")

    sample_reddit = {
        "source": "reddit",
        "subreddit": "loseit",
        "title": "Lost 50 pounds but struggling with the last 10",
        "text": "I've been on this journey for 6 months and the progress has been amazing...",
        "score": 342,
        "num_comments": 45,
        "comments": [
            {
                "text": "The last 10 pounds are always the hardest! Don't give up!",
                "score": 56
            }
        ]
    }

    syntax = Syntax(json.dumps(sample_reddit, indent=2), "json", theme="monokai")
    console.print(syntax)

def show_analysis_output():
    """Show sample Claude analysis output."""
    console.print("\n[bold]Sample Claude AI Analysis Output:[/bold]\n")

    sample_analysis = {
        "emotional_patterns": [
            {
                "emotion": "frustration",
                "frequency": "high",
                "example_quotes": [
                    "I've tried everything and nothing works",
                    "So tired of failing at this",
                    "Why is this so hard for me?"
                ],
                "advertising_angle": "Acknowledge frustration and offer hope with proven system"
            }
        ],
        "pain_points": [
            {
                "pain_point": "Lack of time for meal prep and exercise",
                "severity": "critical",
                "customer_quotes": [
                    "I work 60 hours a week, when am I supposed to cook?",
                    "No time for the gym between work and kids"
                ],
                "desired_outcome": "Quick, effective solutions that fit into busy schedule"
            }
        ],
        "awareness_stages": {
            "problem_aware": {
                "indicators": ["I know I need to lose weight", "My health is suffering"],
                "quotes": ["I can't fit in my clothes anymore", "My doctor says I'm pre-diabetic"]
            }
        }
    }

    syntax = Syntax(json.dumps(sample_analysis, indent=2), "json", theme="monokai")
    console.print(syntax)

def show_ad_frameworks():
    """Show sample ad-ready output."""
    console.print("\n[bold]Sample Ad-Ready Hooks & Frameworks:[/bold]\n")

    hooks_table = Table(title="Ad Hooks by Awareness Stage", show_header=True)
    hooks_table.add_column("Stage", style="cyan")
    hooks_table.add_column("Hook Example", style="green")

    hooks_table.add_row(
        "Problem Aware",
        '"Tired of diets that don\'t fit your 60-hour work week?"'
    )
    hooks_table.add_row(
        "Solution Aware",
        '"What if you could lose weight without spending hours meal prepping?"'
    )
    hooks_table.add_row(
        "Product Aware",
        '"Unlike other programs, we designed this for people who work 60+ hours"'
    )

    console.print(hooks_table)

    console.print("\n[bold]Body Copy Framework Example:[/bold]\n")
    console.print(Panel(
        "[yellow]Problem-Agitate-Solution Framework:[/yellow]\n\n"
        "[bold]Problem:[/bold] 'Working 60 hours a week, when am I supposed to cook?'\n\n"
        "[bold]Agitate:[/bold] Every diet tells you to meal prep on Sundays, hit the gym 5x per week, "
        "and track every calorie. But you barely have time to sleep, let alone spend 3 hours chopping vegetables.\n\n"
        "[bold]Solution:[/bold] Our 15-minute meal system is designed for people who actually work for a living...",
        border_style="yellow"
    ))

def show_output_formats():
    """Show available output formats."""
    console.print("\n[bold]Output Formats Available:[/bold]\n")

    formats = [
        ("📄 JSON", "Machine-readable data for integrations", "message_map_20240122.json"),
        ("📝 Markdown", "Human-readable reports for sharing", "message_map_20240122.md"),
        ("🌐 HTML", "Beautiful web-based reports", "message_map_20240122.html"),
    ]

    for emoji_name, desc, example in formats:
        console.print(f"{emoji_name}: {desc}")
        console.print(f"  [dim]Example: output/{example}[/dim]\n")

def show_workflow():
    """Show the complete workflow."""
    console.print("\n[bold]Complete Workflow:[/bold]\n")

    workflow = """
1. **Setup**
   - Install: `pip install -r requirements.txt`
   - Configure: Add API keys to `.env` file

2. **Run Scraping**
   - System scrapes Reddit, Amazon, YouTube based on your query
   - Collects posts, reviews, comments with metadata

3. **AI Analysis**
   - Claude analyzes all text for emotional patterns
   - Identifies pain points, desires, objections
   - Categorizes by awareness stage

4. **Generate Output**
   - Creates comprehensive message map
   - Outputs ad-ready hooks and frameworks
   - Saves in your chosen format(s)

5. **Use Insights**
   - Copy hooks directly into ad campaigns
   - Use frameworks to write body copy
   - Address objections proactively
    """

    console.print(Markdown(workflow))

def show_example_commands():
    """Show example commands from the examples directory."""
    console.print("\n[bold]Pre-built Example Scripts:[/bold]\n")

    console.print("[cyan]Fitness Product Research:[/cyan]")
    console.print('[dim]./examples/fitness_research.sh[/dim]\n')

    console.print("[cyan]SaaS Product Research:[/cyan]")
    console.print('[dim]./examples/saas_research.sh[/dim]\n')

    console.print("[cyan]E-commerce Research:[/cyan]")
    console.print('[dim]./examples/ecommerce_research.sh[/dim]\n')

def main():
    """Run the demo."""
    show_system_overview()

    console.print("\n" + "="*80 + "\n")
    show_cli_usage()

    console.print("\n" + "="*80 + "\n")
    show_sample_data()

    console.print("\n" + "="*80 + "\n")
    show_analysis_output()

    console.print("\n" + "="*80 + "\n")
    show_ad_frameworks()

    console.print("\n" + "="*80 + "\n")
    show_output_formats()

    console.print("\n" + "="*80 + "\n")
    show_workflow()

    console.print("\n" + "="*80 + "\n")
    show_example_commands()

    console.print("\n" + "="*80 + "\n")

    console.print(Panel.fit(
        "[bold green]✓ Demo Complete![/bold green]\n\n"
        "To use the system:\n"
        "1. Add your API keys to `.env`\n"
        "2. Run: [cyan]python main.py 'your query' --reddit 'subreddit'[/cyan]\n"
        "3. Check the [yellow]output/[/yellow] directory for results\n\n"
        "For help: [cyan]python main.py --help[/cyan]",
        title="Next Steps",
        border_style="green"
    ))

if __name__ == '__main__':
    main()
