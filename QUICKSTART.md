# Quick Start Guide

Get started with Customer Language Mining System in 5 minutes.

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 2: Set Up API Keys

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key (required):

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

Optional: Add Reddit and YouTube API keys for those sources.

## Step 3: Run Your First Analysis

Try this simple example using Amazon reviews:

```bash
python main.py "protein powder" --amazon --format markdown
```

Or if you have Reddit API credentials:

```bash
python main.py "weight loss" --reddit "loseit,fitness" --format markdown
```

## Step 4: View Results

Check the `output/` directory for your message map. Open the `.md` file to see:

- Customer pain points
- Emotional patterns
- Ad-ready hooks
- Body copy frameworks
- And more!

## Step 5: Explore Examples

Check the `examples/` directory for more use cases:

```bash
# Fitness products
./examples/fitness_research.sh

# SaaS products
./examples/saas_research.sh

# E-commerce
./examples/ecommerce_research.sh

# Mobile apps
./examples/app_research.sh
```

## Tips for Best Results

1. **Be Specific**: Use specific product names/categories
2. **Add Context**: Use `--context` flag to guide the analysis
3. **Multiple Sources**: Combine Reddit, Amazon, and YouTube for comprehensive insights
4. **Review Output**: Check the message map for actionable insights

## Common Commands

### Reddit Research
```bash
python main.py "your query" --reddit "subreddit1,subreddit2"
```

### Amazon Research
```bash
python main.py "your query" --amazon
```

### YouTube Research
```bash
python main.py "your query" --youtube
```

### All Sources Combined
```bash
python main.py "your query" --reddit "sub1,sub2" --amazon --youtube
```

### With Context
```bash
python main.py "your query" --reddit "sub1" --context "B2B SaaS targeting small businesses"
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Customize [config.yaml](config.yaml) for your needs
- Explore the message map outputs in the `output/` directory
- Use the insights to create better ads!

## Need Help?

- Check [README.md](README.md) for troubleshooting
- Review example scripts in `examples/`
- Ensure API keys are correctly set in `.env`
