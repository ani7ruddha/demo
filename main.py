#!/usr/bin/env python3
"""
Customer Language Mining System - Main CLI Interface

Automated scraper and analyzer for customer language from multiple sources.
Uses Claude AI to identify emotional patterns, pain points, and desire triggers.
"""

import argparse
import sys
import os
from typing import List, Dict
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from customer_language_miner.scrapers import RedditScraper, AmazonScraper, YouTubeScraper
from customer_language_miner.analysis import ClaudeAnalyzer
from customer_language_miner.output_generator import MessageMapGenerator
from customer_language_miner.utils.config import load_config, load_env, get_api_keys


console = Console()


def scrape_data(args, api_keys: Dict, config: Dict) -> List[Dict]:
    """Scrape data from specified sources."""
    all_data = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:

        # Reddit scraping
        if args.reddit and api_keys['reddit_client_id']:
            task = progress.add_task("Scraping Reddit...", total=None)
            try:
                reddit_scraper = RedditScraper(
                    client_id=api_keys['reddit_client_id'],
                    client_secret=api_keys['reddit_client_secret'],
                    user_agent=api_keys['reddit_user_agent']
                )

                subreddits = args.reddit.split(',')
                reddit_data = reddit_scraper.scrape_multiple_subreddits(
                    subreddits=subreddits,
                    query=args.query,
                    limit_per_subreddit=config['scraping']['max_items_per_source']
                )
                all_data.extend(reddit_data)
                console.print(f"[green]✓[/green] Scraped {len(reddit_data)} items from Reddit")
            except Exception as e:
                console.print(f"[red]✗[/red] Reddit scraping failed: {str(e)}")
            finally:
                progress.remove_task(task)

        # Amazon scraping
        if args.amazon:
            task = progress.add_task("Scraping Amazon...", total=None)
            try:
                amazon_scraper = AmazonScraper()
                amazon_data = amazon_scraper.scrape_category_reviews(
                    search_query=args.query,
                    max_products=5,
                    reviews_per_product=config['scraping']['max_items_per_source']
                )
                all_data.extend(amazon_data)
                console.print(f"[green]✓[/green] Scraped {len(amazon_data)} items from Amazon")
            except Exception as e:
                console.print(f"[red]✗[/red] Amazon scraping failed: {str(e)}")
            finally:
                progress.remove_task(task)

        # YouTube scraping
        if args.youtube and api_keys['youtube']:
            task = progress.add_task("Scraping YouTube...", total=None)
            try:
                youtube_scraper = YouTubeScraper(api_key=api_keys['youtube'])
                youtube_data = youtube_scraper.scrape_search_comments(
                    query=args.query,
                    max_videos=5,
                    comments_per_video=config['scraping']['max_items_per_source']
                )
                all_data.extend(youtube_data)
                console.print(f"[green]✓[/green] Scraped {len(youtube_data)} items from YouTube")
            except Exception as e:
                console.print(f"[red]✗[/red] YouTube scraping failed: {str(e)}")
            finally:
                progress.remove_task(task)

    return all_data


def analyze_data(data: List[Dict], api_keys: Dict, config: Dict, context: str) -> tuple:
    """Analyze scraped data using Claude."""
    console.print("\n[bold blue]Analyzing customer language with Claude AI...[/bold blue]")

    analyzer = ClaudeAnalyzer(
        api_key=api_keys['anthropic'],
        model=config['analysis']['model']
    )

    # Extract text from data
    texts = []
    for item in data:
        if 'text' in item and item['text']:
            texts.append(item['text'])
        if 'title' in item and item['title']:
            texts.append(item['title'])
        # Extract comments from nested structures
        if 'comments' in item:
            for comment in item['comments']:
                if isinstance(comment, dict) and 'text' in comment:
                    texts.append(comment['text'])
        if 'replies' in item:
            for reply in item['replies']:
                if isinstance(reply, dict) and 'text' in reply:
                    texts.append(reply['text'])

    console.print(f"Analyzing {len(texts)} text samples...")

    # Perform analysis
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task1 = progress.add_task("Analyzing patterns and pain points...", total=None)
        analysis = analyzer.analyze_batch(
            texts=texts,
            context=context,
            max_tokens=config['analysis']['max_tokens']
        )
        progress.remove_task(task1)

        task2 = progress.add_task("Generating ad copy frameworks...", total=None)
        ad_framework = analyzer.generate_ad_copy_framework(analysis)
        progress.remove_task(task2)

    console.print("[green]✓[/green] Analysis complete!")

    return analysis, ad_framework


def generate_output(analysis: Dict, ad_framework: Dict, raw_data: List[Dict], args, config: Dict):
    """Generate and save message map."""
    console.print("\n[bold blue]Generating message map...[/bold blue]")

    generator = MessageMapGenerator(output_dir=config['output']['directory'])

    metadata = {
        'query': args.query,
        'context': args.context,
        'sources': {
            'reddit': bool(args.reddit),
            'amazon': bool(args.amazon),
            'youtube': bool(args.youtube)
        }
    }

    message_map = generator.generate_message_map(
        analysis=analysis,
        ad_framework=ad_framework,
        raw_data=raw_data if config['output']['include_raw_data'] else None,
        metadata=metadata
    )

    # Save in specified format(s)
    output_format = args.format or config['output']['format']

    files_saved = []
    if 'json' in output_format:
        filepath = generator.save_as_json(message_map)
        files_saved.append(filepath)

    if 'markdown' in output_format:
        filepath = generator.save_as_markdown(message_map)
        files_saved.append(filepath)

    if 'html' in output_format:
        filepath = generator.save_as_html(message_map)
        files_saved.append(filepath)

    # Display summary
    console.print("\n[bold green]Message Map Generated Successfully![/bold green]")
    console.print(f"\nFiles saved:")
    for filepath in files_saved:
        console.print(f"  • {filepath}")

    # Display key insights
    display_summary(message_map)


def display_summary(message_map: Dict):
    """Display key insights summary."""
    console.print("\n[bold cyan]Key Insights:[/bold cyan]")

    summary = message_map.get('executive_summary', {})
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Top Pain Point", summary.get('top_pain_point', 'N/A'))
    table.add_row("Dominant Emotion", summary.get('dominant_emotion', 'N/A'))
    table.add_row("Primary Desire", summary.get('primary_desire', 'N/A'))
    table.add_row("Emotional Patterns", str(summary.get('total_emotional_patterns', 0)))
    table.add_row("Pain Points", str(summary.get('total_pain_points', 0)))
    table.add_row("Desire Triggers", str(summary.get('total_desire_triggers', 0)))

    console.print(table)

    # Display top insights
    console.print("\n[bold cyan]Top Insights:[/bold cyan]")
    for i, insight in enumerate(message_map.get('key_insights', [])[:5], 1):
        console.print(f"  {i}. {insight}")


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description='Customer Language Mining System - Extract and analyze customer language for advertising'
    )

    parser.add_argument(
        'query',
        type=str,
        help='Search query or product category to research'
    )

    parser.add_argument(
        '--reddit',
        type=str,
        help='Comma-separated list of subreddit names (e.g., "Fitness,running,weightloss")'
    )

    parser.add_argument(
        '--amazon',
        action='store_true',
        help='Enable Amazon reviews scraping'
    )

    parser.add_argument(
        '--youtube',
        action='store_true',
        help='Enable YouTube comments scraping'
    )

    parser.add_argument(
        '--context',
        type=str,
        default='',
        help='Additional context about the product/category for better analysis'
    )

    parser.add_argument(
        '--format',
        type=str,
        choices=['json', 'markdown', 'html', 'all'],
        help='Output format (default: from config.yaml)'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to config file (default: config.yaml)'
    )

    args = parser.parse_args()

    # Validate sources
    if not (args.reddit or args.amazon or args.youtube):
        console.print("[red]Error:[/red] At least one data source must be specified (--reddit, --amazon, or --youtube)")
        sys.exit(1)

    # Load configuration
    console.print("[bold]Customer Language Mining System[/bold]\n")
    load_env()
    config = load_config(args.config)
    api_keys = get_api_keys()

    # Validate API keys
    if not api_keys['anthropic']:
        console.print("[red]Error:[/red] ANTHROPIC_API_KEY not found in environment variables")
        sys.exit(1)

    if args.reddit and not api_keys['reddit_client_id']:
        console.print("[yellow]Warning:[/yellow] Reddit API credentials not found. Skipping Reddit scraping.")
        args.reddit = None

    if args.youtube and not api_keys['youtube']:
        console.print("[yellow]Warning:[/yellow] YouTube API key not found. Skipping YouTube scraping.")
        args.youtube = False

    # Execute pipeline
    console.print(f"[bold]Query:[/bold] {args.query}")
    console.print(f"[bold]Sources:[/bold] Reddit: {bool(args.reddit)}, Amazon: {args.amazon}, YouTube: {args.youtube}\n")

    # Step 1: Scrape data
    data = scrape_data(args, api_keys, config)

    if not data:
        console.print("[red]Error:[/red] No data was scraped. Please check your inputs and API keys.")
        sys.exit(1)

    console.print(f"\n[bold green]Total items scraped:[/bold green] {len(data)}")

    # Step 2: Analyze data
    analysis, ad_framework = analyze_data(data, api_keys, config, args.context)

    # Step 3: Generate output
    generate_output(analysis, ad_framework, data, args, config)

    console.print("\n[bold green]✓ Process complete![/bold green]")


if __name__ == '__main__':
    main()
