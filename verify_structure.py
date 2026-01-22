#!/usr/bin/env python3
"""Verify project structure without requiring dependencies."""

import os
import sys

def check_file(path, description):
    """Check if a file exists."""
    if os.path.exists(path):
        print(f"✓ {description}")
        return True
    else:
        print(f"✗ {description} - MISSING")
        return False

def main():
    """Verify all required files exist."""
    print("Verifying Customer Language Mining System structure...\n")

    all_good = True

    # Core files
    all_good &= check_file("main.py", "Main CLI interface")
    all_good &= check_file("requirements.txt", "Requirements file")
    all_good &= check_file("config.yaml", "Configuration file")
    all_good &= check_file(".env.example", "Environment template")
    all_good &= check_file("README.md", "README documentation")
    all_good &= check_file("QUICKSTART.md", "Quick start guide")
    all_good &= check_file(".gitignore", "Git ignore file")

    print()

    # Package structure
    all_good &= check_file("customer_language_miner/__init__.py", "Package init")

    # Scrapers
    all_good &= check_file("customer_language_miner/scrapers/__init__.py", "Scrapers init")
    all_good &= check_file("customer_language_miner/scrapers/reddit_scraper.py", "Reddit scraper")
    all_good &= check_file("customer_language_miner/scrapers/amazon_scraper.py", "Amazon scraper")
    all_good &= check_file("customer_language_miner/scrapers/youtube_scraper.py", "YouTube scraper")

    # Analysis
    all_good &= check_file("customer_language_miner/analysis/__init__.py", "Analysis init")
    all_good &= check_file("customer_language_miner/analysis/claude_analyzer.py", "Claude analyzer")

    # Output
    all_good &= check_file("customer_language_miner/output_generator/__init__.py", "Output init")
    all_good &= check_file("customer_language_miner/output_generator/message_map.py", "Message map generator")

    # Utils
    all_good &= check_file("customer_language_miner/utils/__init__.py", "Utils init")
    all_good &= check_file("customer_language_miner/utils/config.py", "Config utilities")

    # Examples
    all_good &= check_file("examples/fitness_research.sh", "Fitness example")
    all_good &= check_file("examples/saas_research.sh", "SaaS example")
    all_good &= check_file("examples/ecommerce_research.sh", "E-commerce example")
    all_good &= check_file("examples/app_research.sh", "App example")

    print()

    if all_good:
        print("✓✓✓ All files present! Project structure is complete.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up API keys: cp .env.example .env (then edit .env)")
        print("3. Run analysis: python main.py 'your query' --reddit 'subreddit'")
        return 0
    else:
        print("✗✗✗ Some files are missing. Please check the structure.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
