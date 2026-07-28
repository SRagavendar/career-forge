"""Gemini API integration for job evaluation"""

import os
import json
import asyncio
from typing import Optional
import google.generativeai as genai
from ..core.models import Evaluation, EvaluationScore


class GeminiEvaluator:
    """Evaluate job matches using Google Gemini API"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3.6-flash"):
        """Initialize Gemini evaluator with API key"""
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment. "
                "Set it in .env or pass api_key parameter."
            )
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
    
    async def evaluate(
        self,
        cv_text: str,
        jd_text: str,
        company: str,
        title: str,
        url: Optional[str] = None
    ) -> Evaluation:
        """
        Evaluate job match across 6 dimensions using Gemini.
        
        Returns structured evaluation with scores (1-5) for:
        - Role Match: Is this a real opportunity?
        - CV Match: How well does experience fit requirements?
        - Level Fit: Seniority alignment?
        - Comp Research: Salary/benefits competitive?
        - Personalization: How to tailor CV?
        - Interview Prep: What STAR stories help?
        """
        
        prompt = f"""You are an expert career coach and technical recruiter with 15+ years experience.

Evaluate this job match against the candidate's profile.

USER CV:
{cv_text}

JOB DESCRIPTION:
{jd_text}

Evaluate across exactly 6 dimensions (score each 1-5):

1. **Role Match** (1-5): Is this a genuine opportunity aligned with their profile? Are there any red flags?
2. **CV Match** (1-5): How well does their actual experience match the stated requirements?
3. **Level Fit** (1-5): Is the seniority level appropriate? Risk of overqualified/underqualified?
4. **Comp Research** (1-5): Are the salary/benefits competitive for this role, location, and level?
5. **Personalization** (1-5): How easy/important would tailoring their CV be for this role?
6. **Interview Prep** (1-5): How well can they articulate fit using STAR framework?

Return ONLY valid JSON (no markdown, no extra text):
{{
    "role_match": 4.0,
    "cv_match": 4.2,
    "level_fit": 4.0,
    "comp_research": 3.8,
    "personalization": 4.3,
    "interview_prep": 4.1,
    "role_summary": "...",
    "cv_match_analysis": "...",
    "level_strategy": "...",
    "comp_insights": "...",
    "tailoring_suggestions": "...",
    "interview_tips": "...",
    "recommendation": "Strong Fit"
}}

Rules:
- All scores must be between 1.0 and 5.0
- recommendation must be one of: "Strong Fit", "Good Fit", "Consider", "Pass"
- Be realistic and fair, not overly optimistic or pessimistic
- Focus on concrete evidence from CV and JD
"""
        
        # Run async evaluation
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            self.model.generate_content,
            prompt
        )
        
        # Parse response
        try:
            # Try direct JSON parse
            data = json.loads(response.text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\n(.*?)\n```', response.text, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                # Last resort: use response text as fallback
                raise ValueError(f"Could not parse Gemini response: {response.text}")
        
        # Create score object
        scores = EvaluationScore(
            role_match=float(data.get('role_match', 3.0)),
            cv_match=float(data.get('cv_match', 3.0)),
            level_fit=float(data.get('level_fit', 3.0)),
            comp_research=float(data.get('comp_research', 3.0)),
            personalization=float(data.get('personalization', 3.0)),
            interview_prep=float(data.get('interview_prep', 3.0))
        )
        
        # Create evaluation object
        evaluation = Evaluation(
            company=company,
            title=title,
            url=url,
            scores=scores,
            role_summary=data.get('role_summary', ''),
            cv_match_analysis=data.get('cv_match_analysis', ''),
            level_strategy=data.get('level_strategy', ''),
            comp_insights=data.get('comp_insights', ''),
            tailoring_suggestions=data.get('tailoring_suggestions', ''),
            interview_tips=data.get('interview_tips', ''),
            recommendation=data.get('recommendation', 'Consider')
        )
        
        return evaluation
