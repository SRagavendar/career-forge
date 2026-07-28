"""Tests for core CV parser"""

import pytest
from pathlib import Path
from src.core.cv_parser import load_cv, parse_role_company, parse_dates


def test_load_cv():
    """Test loading CV from markdown file"""
    cv = load_cv("data/cv.md")
    
    assert cv.name == "Senthil Ragavendar"
    assert cv.email == "ragajks@gmail.com"
    assert len(cv.experience) > 0
    assert cv.experience[0].company == "Anthropic"


def test_parse_role_company():
    """Test parsing role and company from string"""
    title, company = parse_role_company("Senior AI Engineer @ Anthropic")
    assert title == "Senior AI Engineer"
    assert company == "Anthropic"


def test_parse_dates():
    """Test parsing date ranges"""
    start, end = parse_dates("*2023-01 - Present*")
    assert start == "2023-01"
    assert end is None
    
    start, end = parse_dates("*2022-06 - 2024-01*")
    assert start == "2022-06"
    assert end == "2024-01"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
