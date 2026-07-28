"""Parse CV from markdown with YAML frontmatter"""

from pathlib import Path
from typing import Optional
import frontmatter
from .models import CV, Experience, Skills


def load_cv(file_path: str | Path) -> CV:
    """
    Load CV from markdown file with YAML frontmatter.
    
    Expected format:
    ---
    name: John Doe
    email: john@example.com
    phone: +1-234-567-8900
    location: San Francisco, CA
    education:
      - BS Computer Science, UC Berkeley (2019)
    certifications:
      - AWS Certified Solutions Architect
    ---
    
    ## Summary
    AI Engineer with 5+ years experience...
    
    ## Experience
    ### Senior AI Engineer @ Anthropic
    *2023-01 - Present*
    - Led Claude feature development
    - 40% latency improvement
    
    ## Skills
    **Technical:** Python, PyTorch, Transformers
    **Soft Skills:** Leadership, Communication
    """
    
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CV file not found: {file_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        post = frontmatter.load(f)
    
    metadata = post.metadata
    content = post.content
    
    # Parse experience section
    experiences = parse_experience_section(content)
    
    # Parse skills
    skills = parse_skills_section(content)
    
    # Parse education and certifications from metadata
    education = metadata.get('education', [])
    certifications = metadata.get('certifications', [])
    
    # Create CV object
    cv = CV(
        name=metadata.get('name', 'Unknown'),
        email=metadata.get('email', ''),
        phone=metadata.get('phone'),
        location=metadata.get('location'),
        summary=metadata.get('summary'),
        experience=experiences,
        skills=skills,
        education=education,
        certifications=certifications
    )
    
    return cv


def parse_experience_section(content: str) -> list[Experience]:
    """Extract experience entries from markdown content"""
    experiences = []
    
    # Split by main sections
    sections = content.split("## ")
    
    for section in sections:
        if section.strip().startswith("Experience"):
            # Split by subsections (###)
            subsections = section.split("### ")[1:]  # Skip header
            
            for sub in subsections:
                lines = sub.strip().split('\n')
                if len(lines) >= 1:
                    # First line: "Title @ Company"
                    role_company = lines[0]
                    title, company = parse_role_company(role_company)
                    
                    # Second line: "*start_date - end_date*"
                    dates = lines[1] if len(lines) > 1 else ""
                    start_date, end_date = parse_dates(dates)
                    
                    # Rest: achievements (lines starting with -)
                    achievements = [
                        l.strip('- ').strip() 
                        for l in lines[2:] 
                        if l.strip().startswith('-') or l.strip().startswith('*')
                    ]
                    
                    experience = Experience(
                        company=company,
                        title=title,
                        start_date=start_date,
                        end_date=end_date,
                        current=end_date is None or 'present' in str(end_date).lower(),
                        achievements=achievements
                    )
                    experiences.append(experience)
    
    return experiences


def parse_skills_section(content: str) -> Skills:
    """Extract skills from markdown content"""
    technical = []
    soft = []
    
    sections = content.split("## ")
    
    for section in sections:
        if "Skill" in section:
            lines = section.split('\n')[1:]  # Skip header
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("**Technical:"):
                    # Parse "**Technical:** Python, PyTorch, Transformers"
                    skills_str = line.split(':')[1].strip().rstrip('**')
                    technical = [s.strip() for s in skills_str.split(',')]
                
                elif "Soft" in line or (line.startswith("**") and "Skill" in line):
                    # Parse "**Soft Skills:** Leadership, Communication"
                    skills_str = line.split(':')[1].strip().rstrip('**')
                    soft = [s.strip() for s in skills_str.split(',')]
    
    return Skills(technical=technical, soft=soft)


def parse_role_company(text: str) -> tuple[str, str]:
    """Parse 'Title @ Company' format"""
    if ' @ ' in text:
        parts = text.split(' @ ', 1)
        return parts[0].strip(), parts[1].strip()
    elif ' at ' in text.lower():
        parts = text.split(' at ', 1)
        return parts[0].strip(), parts[1].strip()
    return text.strip(), "Unknown"


def parse_dates(text: str) -> tuple[str, Optional[str]]:
    """
    Parse date range from markdown italics format.
    Expected: "*2023-01 - 2024-01*" or "*2023-01 - Present*"
    """
    if not text.strip():
        return "Unknown", None
    
    # Remove markdown formatting
    text = text.strip('*').strip()
    
    # Split by dash
    parts = text.split('-')
    
    start = parts[0].strip() if parts else "Unknown"
    end = parts[1].strip() if len(parts) > 1 else None
    
    # Normalize "Present" to None (current position)
    if end and end.lower() in ['present', 'now']:
        end = None
    
    return start, end
