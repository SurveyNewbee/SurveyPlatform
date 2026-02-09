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
        from loi_calculator import LOICalculator
        
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
        print(f"Survey generation result: {type(survey_json)}, has data: {survey_json is not None}")
        
        if not survey_json:
            raise ValueError("Survey generation returned no result")
        
        print(f"Survey has {len(survey_json.get('sections', []))} sections")
        
        # Add LOI configuration with default slider position at Standard tier
        print("Adding LOI configuration...")
        loi_calc = LOICalculator(survey_json)
        survey_json = loi_calc.add_loi_config(initial_position=50)
        print(f"LOI config added: {survey_json.get('loi_config', {})}")
        
        # For now, return without validation
        # TODO: Add validation step
        result = {
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
        print(f"Returning result: success={result['success']}, has survey: {'survey' in result.get('data', {})}")
        return result
        
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


@router.post("/update-loi")
async def update_loi(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update LOI configuration based on slider position.
    
    Request body:
    {
        "survey": {...},
        "slider_position": 50
    }
    
    Returns updated survey with new loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        slider_position = request.get("slider_position", 50)
        
        if not survey:
            raise ValueError("Survey data required")
        
        # Update LOI configuration
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.update_loi_config(slider_position)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/pin-question")
async def pin_question(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pin a question to always show it regardless of LOI setting.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Pin question
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.pin_question(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/exclude-question")
async def exclude_question(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exclude a question to always hide it regardless of LOI setting.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Exclude question
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.exclude_question(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reset-question-override")
async def reset_question_override(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reset a question's override to default LOI-based visibility.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Reset override
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.reset_question_override(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
