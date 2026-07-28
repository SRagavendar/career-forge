"""Parse job descriptions from text or URL"""

import re
from .models import JobDescription, SeniorityLevel


def parse_jd_text(
    text: str,
    company: str = "Unknown",
    url: str | None = None
) -> JobDescription:
    """
    Parse job description from plain text.
    Extracts title, seniority, location, salary, requirements, etc.
    """
    
    # Extract title
    title = extract_title(text) or "Unnamed Role"
    
    # Detect seniority level
    level = detect_seniority(text)
    
    # Extract location
    location = extract_location(text) or "Unknown"
    
    # Check if remote
    remote = bool(re.search(r'remote|work from home|anywhere|wfh|distributed', text, re.I))
    
    # Extract salary
    salary_min, salary_max = extract_salary(text)
    
    # Detect visa sponsorship
    sponsor_visa = detect_visa_sponsorship(text)
    
    # Extract requirements
    requirements = extract_requirements(text)
    
    jd = JobDescription(
        title=title,
        company=company,
        url=url,
        description=text,
        requirements=requirements,
        level=level,
        salary_min=salary_min,
        salary_max=salary_max,
        location=location,
        remote=remote,
        sponsor_visa=sponsor_visa
    )
    
    return jd


def extract_title(text: str) -> str | None:
    """Extract job title from text - look in first few lines"""
    lines = text.split('\n')[:10]
    
    # Common title keywords
    title_keywords = [
        'engineer', 'manager', 'lead', 'architect', 'specialist',
        'researcher', 'scientist', 'director', 'staff', 'principal',
        'developer', 'designer', 'analyst', 'strategist', 'officer'
    ]
    
    for line in lines:
        line_lower = line.lower()
        if any(keyword in line_lower for keyword in title_keywords):
            # Extract up to reasonable length
            title = line.strip()
            if len(title) > 10 and len(title) < 150:
                return title
    
    return None


def detect_seniority(text: str) -> SeniorityLevel:
    """Detect seniority level from keywords"""
    text_lower = text.lower()
    
    # Check in order of seniority (most specific first)
    if any(word in text_lower for word in ['director', 'vp ', 'vice president', 'chief', 'head of', 'cto', 'cfo', 'ceo']):
        return SeniorityLevel.DIRECTOR
    
    elif any(word in text_lower for word in ['staff ', 'principal ', 'distinguished', 'architect']):
        return SeniorityLevel.STAFF
    
    elif any(word in text_lower for word in ['senior', 'sr. ', 'sr ', '5+ years', '5+years', '6+ years', '7+ years', '8+ years', '10+ years']):
        return SeniorityLevel.SENIOR
    
    elif any(word in text_lower for word in ['lead', 'team lead', 'tech lead', 'tech-lead', 'team-lead']):
        return SeniorityLevel.LEAD
    
    elif any(word in text_lower for word in ['junior', 'entry', 'entry-level', 'entry level', 'graduate', '0-2 years', 'fresh']):
        return SeniorityLevel.JUNIOR
    
    else:
        return SeniorityLevel.MID


def extract_location(text: str) -> str | None:
    """Extract location from text - look for city, state pattern"""
    # Pattern: "City, ST" or "City, Country"
    pattern = r'([\w\s]+),\s*([A-Z]{2}|[A-Za-z\s]{2,})'
    match = re.search(pattern, text[:500])  # Search in first 500 chars
    
    if match:
        return f"{match.group(1).strip()}, {match.group(2).strip()}"
    
    return None


def extract_salary(text: str) -> tuple[float | None, float | None]:
    """
    Extract salary range from text.
    Looks for patterns like: $180k-$220k, $180000-220000, 180k-220k
    """
    
    # Pattern 1: $180k-$220k or $180,000-$220,000
    pattern1 = r'\$?([\d,]+)k?\s*-\s*\$?([\d,]+)k?'
    matches = re.findall(pattern1, text, re.I)
    
    if matches:
        try:
            min_str = matches[0][0].replace(',', '')
            max_str = matches[0][1].replace(',', '')
            
            # Convert to annual if in thousands
            min_sal = int(min_str) * (1000 if 'k' in text[matches[0][0].__len__():(matches[0][0].__len__() + 10)].lower() else 1)
            max_sal = int(max_str) * (1000 if 'k' in text[matches[0][1].__len__():(matches[0][1].__len__() + 10)].lower() else 1)
            
            return float(min_sal), float(max_sal)
        except (ValueError, IndexError):
            pass
    
    return None, None


def detect_visa_sponsorship(text: str) -> bool | None:
    """Detect if visa sponsorship is mentioned"""
    text_lower = text.lower()
    
    # Positive indicators
    if any(phrase in text_lower for phrase in [
        'visa sponsorship', 'sponsor visa', 'h1b sponsorship',
        'sponsorship available', 'we sponsor', 'visa support',
        'work visa', 'immigration support'
    ]):
        return True
    
    # Negative indicators
    if any(phrase in text_lower for phrase in [
        'no sponsorship', 'no visa', 'us citizen required',
        'us citizens only', 'cannot sponsor', 'no immigration'
    ]):
        return False
    
    return None


def extract_requirements(text: str) -> list[str]:
    """
    Extract requirements from text.
    Looks for "Requirements:", "Must have:", "Qualifications:", etc.
    """
    requirements = []
    
    # Split by common section headers
    sections = re.split(
        r'(requirements?|qualifications?|must have|skills?|experience|what we.re looking for):\s*',
        text,
        flags=re.I
    )
    
    if len(sections) > 2:
        req_text = sections[2]
        
        # Split by bullet points or newlines
        lines = re.split(r'[-•*]\s+|\n\s*', req_text)
        
        for line in lines[:20]:  # Limit to first 20 items
            line = line.strip()
            
            # Filter out empty lines and very short lines
            if line and len(line) > 5 and not line.startswith('#'):
                # Clean up common artifacts
                line = re.sub(r'<[^>]+>', '', line)  # Remove HTML tags
                line = re.sub(r'\*\*', '', line)  # Remove markdown bold
                line = re.sub(r'__', '', line)  # Remove markdown underscore
                
                requirements.append(line)
    
    return requirements
