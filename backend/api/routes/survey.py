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

from api.models import (
    GenerateSurveyRequest,
    GenerateSurveyResponse,
    ValidateSurveyRequest,
    ValidateSurveyResponse
)

router = APIRouter()


@router.post("/generate-survey", response_model=GenerateSurveyResponse)
async def generate_survey(request: GenerateSurveyRequest) -> Dict[str, Any]:
    """
    Generate survey from brief using AI.
    
    Calls generate_survey.py -> validate_survey.py pipeline.
    """
    try:
        import generate_survey as gs
        import validate_survey as vs
        
        # Call the generation function
        # Note: Adapt this based on actual function signature in generate_survey.py
        survey_output = gs.generate_and_save(
            brief=request.brief,
            output_file=None  # Return dict instead of saving
        )
        
        # Validate the generated survey
        validator = vs.SurveyValidator(survey_output, request.brief)
        validated_survey, validation_results = validator.validate()
        
        # Package validation log
        validation_log = {
            "results": [r.to_dict() for r in validation_results],
            "error_count": sum(1 for r in validation_results if r.severity == "error"),
            "warning_count": sum(1 for r in validation_results if r.severity == "warning"),
            "auto_fix_count": sum(1 for r in validation_results if r.severity == "auto_fix")
        }
        
        return GenerateSurveyResponse(
            success=True,
            data=validated_survey,
            validation_log=validation_log
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "generation_failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@router.post("/validate-survey", response_model=ValidateSurveyResponse)
async def validate_survey(request: ValidateSurveyRequest) -> Dict[str, Any]:
    """
    Validate survey against rules.
    
    Runs validate_survey.py on provided survey JSON.
    """
    try:
        import validate_survey as vs
        
        validator = vs.SurveyValidator(request.survey, request.brief)
        validated_survey, validation_results = validator.validate()
        
        error_count = sum(1 for r in validation_results if r.severity == "error")
        warning_count = sum(1 for r in validation_results if r.severity == "warning")
        
        validation_log = {
            "results": [r.to_dict() for r in validation_results],
            "error_count": error_count,
            "warning_count": warning_count,
            "auto_fix_count": sum(1 for r in validation_results if r.severity == "auto_fix")
        }
        
        return ValidateSurveyResponse(
            success=True,
            data=validated_survey,
            validation_log=validation_log,
            has_errors=error_count > 0,
            error_count=error_count,
            warning_count=warning_count
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "validation_failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


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
