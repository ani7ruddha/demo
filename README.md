# Customer Language Mining System

Automated scraper and analyzer for customer language from Reddit, Amazon, YouTube, and other sources. Uses Claude AI to identify emotional patterns, pain points, and desire triggers, outputting a comprehensive "message map" with ad-ready hooks and body copy frameworks.

## The Problem

Creative strategists spend 90% of their time making ads and only 10% researching. It should be the opposite. They need the exact phrases customers use when describing problems, desires, and outcomes.

## The Solution

This system automatically:
- Scrapes customer language from Reddit threads, Amazon reviews, YouTube comments
- Uses Claude AI to analyze emotional language patterns, pain points, and desire triggers
- Organizes insights by stage of awareness (Eugene Schwartz framework)
- Outputs ad-ready hooks and body copy frameworks using actual customer quotes

## Features

- **Multi-Source Scraping**: Reddit, Amazon, YouTube (extensible to other sources)
- **Claude AI Analysis**: Deep analysis of emotional patterns and customer psychology
- **Stage of Awareness Categorization**: Organizes insights by customer awareness level
- **Ad-Ready Output**: Generates hooks, frameworks, and copy templates
- **Multiple Output Formats**: JSON, Markdown, HTML
- **Configurable**: Easy-to-customize settings for your use case

## Installation

### Prerequisites

- Python 3.8 or higher
- API keys for the services you want to use

### Setup

1. Clone this repository:
```bash
git clone <repository-url>
cd demo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file from the example:
```bash
cp .env.example .env
```

4. Add your API keys to `.env`:
```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=CustomerLanguageMiner/1.0
YOUTUBE_API_KEY=your_youtube_api_key_here
```

### Getting API Keys

#### Anthropic (Claude) API Key (Required)
1. Sign up at https://console.anthropic.com
2. Navigate to API Keys section
3. Create a new API key
4. Add credits to your account

#### Reddit API (Optional)
1. Go to https://www.reddit.com/prefs/apps
2. Click "Create App" or "Create Another App"
3. Select "script" as the app type
4. Note your client ID and secret

#### YouTube API (Optional)
1. Go to https://console.cloud.google.com
2. Create a new project
3. Enable YouTube Data API v3
4. Create credentials (API key)

#### Amazon Scraping
- No API key required
- Uses web scraping (be mindful of rate limits)

## Usage

### Basic Usage

Scrape and analyze customer language from Reddit:

```bash
python main.py "weight loss" --reddit "loseit,fitness,keto"
```

Scrape from Amazon reviews:

```bash
python main.py "protein powder" --amazon
```

Scrape from YouTube comments:

```bash
python main.py "meditation app" --youtube
```

Scrape from multiple sources:

```bash
python main.py "fitness tracker" --reddit "fitness,running" --amazon --youtube
```

### Advanced Usage

Add context for better analysis:

```bash
python main.py "project management software" \
  --reddit "projectmanagement,productivity" \
  --context "B2B SaaS targeting small business owners"
```

Specify output format:

```bash
python main.py "meal planning" --reddit "mealprep" --format markdown
python main.py "meal planning" --reddit "mealprep" --format html
python main.py "meal planning" --reddit "mealprep" --format all
```

Use custom config file:

```bash
python main.py "sleep app" --reddit "sleep" --config custom_config.yaml
```

### Command-Line Options

```
positional arguments:
  query                 Search query or product category to research

options:
  -h, --help            Show help message
  --reddit SUBREDDITS   Comma-separated list of subreddit names
  --amazon              Enable Amazon reviews scraping
  --youtube             Enable YouTube comments scraping
  --context TEXT        Additional context for better analysis
  --format FORMAT       Output format: json, markdown, html, all
  --config FILE         Path to config file (default: config.yaml)
```

## Output

The system generates a comprehensive "Message Map" containing:

### 1. Executive Summary
- Top pain point
- Dominant emotion
- Primary desire
- Count of patterns identified

### 2. Pain Points
- Description of each pain point
- Severity level (critical/major/minor)
- Customer quotes demonstrating the pain
- Before state and desired outcome

### 3. Emotional Patterns
- Identified emotions (frustration, hope, fear, desire, etc.)
- Frequency of each emotion
- Example quotes
- Advertising angles

### 4. Desire Triggers
- What customers want to achieve
- Intensity levels
- Language patterns
- Aspirational identity

### 5. Awareness Stages
Customer language organized by Eugene Schwartz's 5 stages:
- **Unaware**: No awareness of problem
- **Problem Aware**: Know the problem, not the solution
- **Solution Aware**: Know solutions exist
- **Product Aware**: Know specific products
- **Most Aware**: Ready to buy

### 6. Ad-Ready Hooks
Pre-written hooks for each awareness stage using customer language

### 7. Body Copy Frameworks
- Problem-Agitate-Solution
- Before-After-Bridge
- And more, with examples using customer quotes

### 8. Call-to-Actions
Suggested CTAs based on customer desires and pain points

### 9. Objection Handlers
Common objections and how to address them

## Project Structure

```
customer_language_miner/
├── scrapers/
│   ├── reddit_scraper.py       # Reddit API integration
│   ├── amazon_scraper.py       # Amazon reviews scraper
│   └── youtube_scraper.py      # YouTube API integration
├── analysis/
│   └── claude_analyzer.py      # Claude AI analysis engine
├── output_generator/
│   └── message_map.py          # Message map generation
└── utils/
    └── config.py               # Configuration utilities

main.py                         # Main CLI interface
config.yaml                     # Configuration file
requirements.txt                # Python dependencies
.env.example                    # Environment variables template
```

## Configuration

Edit `config.yaml` to customize:

- Scraping limits
- Rate limiting
- Claude model and parameters
- Output preferences
- Awareness stage definitions

Example:

```yaml
scraping:
  max_items_per_source: 100
  request_timeout: 30
  rate_limit_delay: 2

analysis:
  model: claude-sonnet-4-5-20250929
  max_tokens: 4000
  temperature: 0.3

output:
  format: markdown
  directory: ./output
  include_raw_data: true
```

## Examples

### Example 1: Fitness Product Research

```bash
python main.py "home workout equipment" \
  --reddit "homegym,bodyweightfitness,fitness" \
  --amazon \
  --context "Targeting busy professionals who want to workout at home"
```

Output includes:
- Pain points: "No time for gym", "Expensive memberships", "Intimidating gym environment"
- Emotions: Frustration with lack of progress, hope for change
- Ad hooks: "Tired of paying $100/month for a gym you never visit?"

### Example 2: SaaS Product Research

```bash
python main.py "team collaboration tools" \
  --reddit "projectmanagement,smallbusiness" \
  --youtube \
  --context "B2B SaaS for remote teams"
```

Output includes:
- Pain points: "Communication breakdowns", "Lost messages", "Too many tools"
- Desires: "Single source of truth", "Better team alignment"
- Frameworks: Problem-Agitate-Solution using exact customer quotes

## Best Practices

1. **Be Specific**: Use specific product categories rather than generic terms
2. **Choose Relevant Sources**: Select subreddits/sources where your target audience hangs out
3. **Add Context**: Provide business context for more relevant analysis
4. **Review Raw Data**: Check the scraped data to ensure quality
5. **Iterate**: Try different queries and sources to get comprehensive insights
6. **Respect Rate Limits**: Don't scrape too aggressively to avoid being blocked

## Limitations

- **API Quotas**: Each API has rate limits and quotas
- **Scraping Risks**: Web scraping can be blocked by anti-bot measures
- **Data Quality**: Analysis quality depends on scraped data quality
- **Cost**: Claude API usage incurs costs based on tokens processed

## Troubleshooting

### "No data was scraped"
- Check your API keys in `.env`
- Verify your query returns results on the platforms
- Check rate limiting settings

### "Error during Claude analysis"
- Verify your Anthropic API key
- Check you have sufficient credits
- Review the error message for details

### "Rate limited" or "403 Forbidden"
- Reduce scraping frequency
- Increase `rate_limit_delay` in config
- Check if your IP is blocked

## Extending the System

### Adding New Data Sources

1. Create a new scraper in `customer_language_miner/scrapers/`
2. Implement the scraper class with consistent output format
3. Add it to `scrapers/__init__.py`
4. Update `main.py` to integrate the new source

### Customizing Analysis

Edit `customer_language_miner/analysis/claude_analyzer.py` to:
- Modify analysis prompts
- Add new analysis dimensions
- Change output structure

### Custom Output Formats

Add new output methods in `customer_language_miner/output_generator/message_map.py`

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

See LICENSE file for details.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check existing issues for solutions

## Roadmap

- [ ] Facebook Groups integration
- [ ] Twitter/X scraping
- [ ] Quora scraping
- [ ] Automated sentiment analysis
- [ ] Competitor analysis features
- [ ] Export to popular ad platforms
- [ ] Web UI dashboard
- [ ] Scheduled automated research

## Credits

Built with:
- [Anthropic Claude](https://www.anthropic.com) - AI analysis
- [PRAW](https://praw.readthedocs.io/) - Reddit API
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) - Web scraping
- [Google API Client](https://github.com/googleapis/google-api-python-client) - YouTube API

## Disclaimer

This tool is for research and educational purposes. Always respect platform terms of service and rate limits. Be mindful of privacy and data protection regulations when collecting and analyzing user-generated content.
