"""
Survey generation and validation endpoints.
"""

import sys
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
import traceback

# Add core to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR / "core"))

from api.models import GenerateSurveyRequest

router = APIRouter()


@router.post("/generate-survey/stream")
async def generate_survey_stream(request: GenerateSurveyRequest):
    """
    Generate survey from approved brief with streaming.
    Returns Server-Sent Events (SSE) stream of LLM tokens.
    """
    try:
        from generate_survey import SurveyGenerator
        
        brief_for_generator = request.brief_data
        generator = SurveyGenerator()
        
        return StreamingResponse(
            generator.generate_async_stream(brief_for_generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        # Return error as SSE
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")


@router.post("/generate-survey")
async def generate_survey(request: GenerateSurveyRequest) -> Dict[str, Any]:
    """
    Generate survey from approved brief using AI.
    
    Takes approved brief_data (which includes survey_blueprint from Agent 1) and
    generates the complete survey using Agent 2.
    
    The brief_data should be the full result from Agent 1 (extract-brief endpoint),
    which has been reviewed and approved by the user.
    """
    try:
        from generate_survey import SurveyGenerator
        from loi_calculator import LOICalculator
        
        # brief_data now contains the full Agent 1 output including survey_blueprint
        # No need to transform or select skills - just pass through to generator
        brief_for_generator = request.brief_data
        
        # Create generator (no skills_dir needed anymore)
        print(f"Creating SurveyGenerator...")
        generator = SurveyGenerator()
        
        # Generate survey
        print(f"Generating survey from approved brief with blueprint...")
        survey_json = generator.generate(brief_for_generator, stream_output=False)
        print(f"Survey generation result: {type(survey_json)}, has data: {survey_json is not None}")
        
        if not survey_json:
            raise ValueError("Survey generation returned no result")
        
        # Check if survey has required top-level structure
        has_main_section = 'MAIN_SECTION' in survey_json
        subsection_count = len(survey_json.get('MAIN_SECTION', {}).get('sub_sections', [])) if has_main_section else 0
        print(f"Survey has MAIN_SECTION: {has_main_section}, subsections: {subsection_count}")
        
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
