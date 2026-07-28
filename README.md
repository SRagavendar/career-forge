# Career-Forge

**AI-powered job search pipeline with Python & Google Gemini**

Evaluate job offers automatically, generate tailored CVs, and track applications - all locally, for free.

## Features ✨

- **AI Job Evaluation** - 6-dimension scoring (role match, CV fit, seniority, compensation, tailoring, interview prep)
- **Smart CV Parsing** - Load your CV from markdown with YAML metadata
- **Job Parsing** - Extract requirements, salary, location, seniority from job postings
- **Structured Reports** - Markdown reports with detailed analysis
- **Free Tier Optimized** - Use Google's free Gemini API (no credit card required)
- **Fast & Simple** - Python-based, minimal dependencies, runs locally
- **Privacy First** - Your data stays on your machine

## Quick Start

### 1. Prerequisites
- Python 3.10+
- Poetry
- Free Gemini API key from [aistudio.google.com/apikey](https://aistudio.google.com/apikey)

### 2. Setup

```bash
cd career-forge
./setup.sh
# Edit .env and add your GEMINI_API_KEY
```

### 3. First Evaluation

```bash
poetry run python -m src.cli.main eval data/sample-jd.txt --company TechCorp
```

## Project Structure

```
career-forge/
├── src/
│   ├── cli/              # CLI interface (Typer)
│   ├── core/             # CV/JD parsing, models
│   ├── evaluators/       # Gemini evaluator
│   ├── scanners/         # Job portal scanning (future)
│   └── generators/       # PDF, cover letter (future)
├── data/                 # Your CV and JDs
├── reports/              # Generated reports
├── config/               # Configuration
└── tests/                # Unit tests
```

## What's Implemented (Phase 1) ✅

- [X] CV parser (markdown + YAML)
- [X] JD parser (text extraction, seniority, salary, location)
- [X] Pydantic data models
- [X] Gemini evaluator (6-block scoring)
- [X] CLI interface
- [X] Report generation

## What's Coming (Phase 2-3) 🔜

- [ ] PDF generation (ATS-optimized)
- [ ] Cover letter generator
- [ ] Job portal scanning (45+ companies)
- [ ] Application tracker (SQLite)
- [ ] Batch evaluation
- [ ] Dashboard UI

## Usage

```bash
# Evaluate a job
poetry run python -m src.cli.main eval data/sample-jd.txt --company TechCorp

# Show version
poetry run python -m src.cli.main version
```

## Configuration

Edit `.env` with your Gemini API key:
```
GEMINI_API_KEY=your_key_here
```

## Development

```bash
# Run tests
poetry run pytest tests/ -v

# Format code
poetry run black src/ tests/

# Lint
poetry run flake8 src/ tests/
```

## License

MIT - See LICENSE for details

## Next Steps

1. Get Gemini API key: https://aistudio.google.com/apikey
2. Add key to .env
3. Edit data/cv.md with your CV
4. Run first evaluation
5. Check reports/ folder for output
