#!/bin/bash

# Career-Forge Quick Setup Script

echo "🚀 Career-Forge Setup"
echo "===================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
echo "✅ Python $python_version detected"

# Check Poetry
if ! command -v poetry &> /dev/null; then
    echo "❌ Poetry not found. Install from https://python-poetry.org/"
    exit 1
fi
echo "✅ Poetry installed"

# Install dependencies
echo ""
echo "📦 Installing dependencies..."
poetry install --no-root

# Setup .env
echo ""
echo "🔑 Setting up .env file..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "⚠️  Created .env file - edit with your Gemini API key"
    echo "   Get free key at: https://aistudio.google.com/apikey"
else
    echo "✅ .env already exists"
fi

# Test CV loading
echo ""
echo "📄 Testing CV loader..."
poetry run python -c "
from src.core.cv_parser import load_cv
try:
    cv = load_cv('data/cv.md')
    print(f'✅ CV loaded: {cv.name}')
except Exception as e:
    print(f'⚠️  CV load test: {e}')
"

# Test JD parsing
echo ""
echo "🔍 Testing JD parser..."
poetry run python -c "
from src.core.jd_parser import parse_jd_text
with open('data/sample-jd.txt') as f:
    jd = parse_jd_text(f.read(), company='TechCorp')
print(f'✅ JD parsed: {jd.title} @ {jd.company}')
"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Edit data/cv.md with your actual CV"
echo "3. Run: poetry run python -m src.cli.main eval data/sample-jd.txt"
echo ""
