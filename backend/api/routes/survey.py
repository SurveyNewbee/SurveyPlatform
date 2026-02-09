"""
Survey generation and validation endpoints.
"""

import sys
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import traceback

# Add core to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR / "core"))

from api.models import GenerateSurveyRequest

router = APIRouter()


@router.post("/generate-survey")
async def generate_survey(request: GenerateSurveyRequest) -> Dict[str, Any]:
    """
    Generate survey from brief using AI.
    
    Takes extracted brief_data and selected_skills, generates survey using SurveyGenerator.
    """
    try:
        from generate_survey import SurveyGenerator
        
        # Transform frontend brief_data into format expected by SurveyGenerator
        # Frontend sends: {objectives, target_audience, topics, identified_skills, timeline, budget}
        # SurveyGenerator expects: {objective, target_audience, key_dimensions, skills, operational, ...}
        brief_for_generator = {
            "objective": request.brief_data.get("objectives", [""])[0] if request.brief_data.get("objectives") else "",
            "target_audience": request.brief_data.get("target_audience", ""),
            "key_dimensions": request.brief_data.get("topics", []),
            "skills": request.selected_skills,
        }
        
        # Add optional operational fields if present
        operational = {}
        if request.brief_data.get("timeline"):
            operational["timeline"] = request.brief_data["timeline"]
        if request.brief_data.get("budget"):
            operational["budget"] = request.brief_data["budget"]
        if operational:
            brief_for_generator["operational"] = operational
        
        # Get skills directory path
        skills_dir = BACKEND_DIR.parent / "skills"
        
        # Create generator
        print(f"Creating SurveyGenerator with skills_dir: {skills_dir}")
        generator = SurveyGenerator(skills_dir=skills_dir)
        
        # Generate survey
        print(f"Generating survey with brief: {brief_for_generator}")
        survey_json = generator.generate(brief_for_generator, stream_output=False)
        
        if not survey_json:
            raise ValueError("Survey generation returned no result")
        
        # For now, return without validation
        # TODO: Add validation step
        return {
            "success": True,
            "data": {
                "survey": survey_json,
                "validation_log": {
                    "is_valid": True,
                    "error_count": 0,
                    "warning_count": 0,
                    "entries": []
                }
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/validate-survey")
async def validate_survey(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate survey against rules.
    
    TODO: Implement validation pipeline.
    For now, returns placeholder response.
    """
    try:
        # TODO: Implement actual validation
        return {
            "success": True,
            "data": {
                "is_valid": True,
                "error_count": 0,
                "warning_count": 0,
                "entries": []
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/render-preview")
async def render_preview(survey: Dict[str, Any]) -> Dict[str, Any]:
    """
    Render survey for respondent preview.
    
    Calls render_survey.py to generate preview-ready format.
    """
    try:
        import render_survey as rs
        
        # Call rendering function
        # Note: Adapt based on actual implementation
        rendered = rs.render_to_preview(survey)
        
        return {
            "success": True,
            "data": rendered
        }
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "render_failed",
                "message": str(e)
            }
        )
