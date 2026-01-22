# Demo Guide - Customer Language Mining System

## Quick Demo Commands

### 1. View Interactive Demo
```bash
python demo_runner.py
```
Shows the complete system overview with examples.

### 2. View Visual Data Flow
```bash
python visual_demo.py
```
Shows what the system produces with metrics and examples.

### 3. View Sample Output
```bash
cat sample_output_example.md
```
See an example of the actual message map output.

### 4. View Example Scripts
```bash
cat examples/fitness_research.sh
cat examples/saas_research.sh
cat examples/ecommerce_research.sh
cat examples/app_research.sh
```

## What This System Does

**Problem It Solves:**
Creative strategists spend 90% of time making ads, 10% researching. This reverses that.

**Solution:**
- 🔍 Scrapes Reddit, Amazon, YouTube for customer language
- 🧠 Claude AI analyzes emotional patterns & pain points
- 📊 Organizes by stage of awareness
- 📝 Outputs ad-ready hooks and copy frameworks

## Sample Output Structure

```
output/
├── message_map_20240122.json      # Machine-readable
├── message_map_20240122.md        # Human-readable report
└── message_map_20240122.html      # Beautiful web report
```

Each contains:
- Executive summary (top pain points, emotions, desires)
- Detailed pain point analysis with customer quotes
- Emotional pattern identification
- Desire triggers and aspirational identities
- Customer language by awareness stage
- 15+ ad-ready hooks
- 4+ body copy frameworks with examples
- Call-to-action suggestions
- Objection handlers

## Real-World Example

### Input:
```bash
python main.py "weight loss" \
  --reddit "loseit,fitness,keto" \
  --amazon \
  --context "Busy professionals aged 30-45"
```

### Output You Get:

**Top Pain Point:**
"I work 60 hours a week, when am I supposed to cook?"

**Ad Hook Generated:**
"Working 60 hours? Here's how to lose weight without meal prepping every Sunday"

**Body Copy Framework:**
```
Problem: "Working 60 hours a week, when am I supposed to cook?"

Agitate: Every diet tells you to meal prep on Sundays, hit the gym 5x
per week, and track every calorie. But you barely have time to sleep...

Solution: Our 15-minute system is designed for people who actually work
for a living...
```

## Processing Time

- Scraping: ~2-3 minutes
- Claude Analysis: ~2 minutes
- Output Generation: ~30 seconds

**Total: ~5 minutes** for comprehensive customer research!

## What You Get vs Traditional Research

### Traditional Manual Research (8-10 hours):
- Read hundreds of Reddit posts
- Scroll through Amazon reviews
- Watch YouTube videos and read comments
- Take notes manually
- Try to identify patterns
- Write ad copy from scratch

### With This System (5 minutes):
- ✓ Automatic scraping from all sources
- ✓ AI-powered pattern identification
- ✓ Organized by awareness stage
- ✓ Ad-ready hooks generated
- ✓ Body copy frameworks with examples
- ✓ Customer quotes extracted and organized

## Value Proposition

**For E-commerce Owners:**
Research product categories to write better descriptions and ads

**For Ad Agencies:**
Quick customer research for new client campaigns

**For SaaS Startups:**
Understand customer pain points for landing pages

**For Copywriters:**
Research customer language for any niche in minutes

**For Content Creators:**
Find what customers actually care about

## Next Steps to Use the System

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up API Keys:**
   ```bash
   cp .env.example .env
   # Edit .env and add your keys
   ```

3. **Run Your First Analysis:**
   ```bash
   python main.py "your product" --reddit "relevant_subreddit"
   ```

4. **Check Output:**
   ```bash
   ls -la output/
   cat output/message_map_*.md
   ```

## Example Use Cases

### Fitness Product
```bash
./examples/fitness_research.sh
```

### SaaS Product
```bash
./examples/saas_research.sh
```

### E-commerce Product
```bash
./examples/ecommerce_research.sh
```

### Mobile App
```bash
./examples/app_research.sh
```

## Files in This Demo

- `demo_runner.py` - Interactive demo with examples
- `visual_demo.py` - Visual data flow demonstration
- `sample_output_example.md` - Example message map output
- `verify_structure.py` - Verify installation
- `examples/*.sh` - Ready-to-use example scripts

## Questions?

Check the full documentation:
- `README.md` - Complete documentation
- `QUICKSTART.md` - 5-minute getting started guide
- `.env.example` - API key setup template
- `config.yaml` - Configuration options

---

**Ready to reverse the 90/10 problem?**
**90% research, 10% making ads - the way it should be!**
