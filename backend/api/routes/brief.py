"""
Brief extraction endpoints.
"""

import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import traceback

# Add core to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR / "core"))

from api.models import APIResponse

# Import from existing scripts
from extract_brief import BriefExtractor


router = APIRouter()


@router.post("/extract-brief")
async def extract_brief(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract structured fields from raw research brief text.
    
    Uses LLM to parse unstructured brief into structured fields.
    """
    try:
        brief_text = request.get("brief_text", "")
        if not brief_text or len(brief_text) < 50:
            raise ValueError("Brief text must be at least 50 characters")
        
        # Create extractor and run
        print(f"Creating BriefExtractor...")
        extractor = BriefExtractor()
        print(f"Calling extract with brief_text length: {len(brief_text)}")
        result = extractor.extract(brief_text, stream_output=False)
        print(f"Extract result: {result}")
        
        if not result:
            raise ValueError("Failed to extract brief - no result returned")
        
        # Map BriefExtraction to frontend ExtractedBrief format
        extracted_brief = {
            "objectives": [result.get("objective", "")],  # Convert single to array
            "target_audience": result.get("target_audience", ""),
            "topics": result.get("key_dimensions", []),
            "survey_blueprint": result.get("survey_blueprint"),  # NEW: Blueprint replaces skills
        }
        
        # Add sample design fields
        if result.get("total_sample_size"):
            extracted_brief["total_sample_size"] = result["total_sample_size"]
        if result.get("quotas"):
            extracted_brief["quotas"] = result["quotas"]
        
        # Add market context if present
        if result.get("market_context"):
            extracted_brief["market_context"] = result["market_context"]
        
        # Add study classification fields
        if result.get("study_type"):
            extracted_brief["study_type"] = result["study_type"]
        if result.get("primary_methodology"):
            extracted_brief["primary_methodology"] = result["primary_methodology"]
        if result.get("secondary_objectives"):
            extracted_brief["secondary_objectives"] = result["secondary_objectives"]
        
        # Add operational fields if present
        if result.get("operational"):
            operational = result["operational"]
            operational_dict = {}
            if operational.get("target_loi_minutes"):
                operational_dict["target_loi_minutes"] = operational["target_loi_minutes"]
            if operational.get("fieldwork_mode"):
                operational_dict["fieldwork_mode"] = operational["fieldwork_mode"]
            if operational.get("market_specifics"):
                operational_dict["market_specifics"] = operational["market_specifics"]
            if operational.get("quality_controls"):
                operational_dict["quality_controls"] = operational["quality_controls"]
            if operational.get("constraints"):
                operational_dict["constraints"] = operational["constraints"]
            if operational_dict:
                extracted_brief["operational"] = operational_dict
        
        # Add study design if present
        if result.get("study_design"):
            extracted_brief["study_design"] = result["study_design"]
        
        # Add measurement guidance if present
        if result.get("measurement_guidance"):
            extracted_brief["measurement_guidance"] = result["measurement_guidance"]
        
        # Add problem frame if present
        if result.get("problem_frame"):
            extracted_brief["problem_frame"] = result["problem_frame"]
        
        return {
            "success": True,
            "data": extracted_brief
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.get("/skills")
async def list_skills() -> Dict[str, Any]:
    """
    Get list of available survey methodology skills.
    
    DEPRECATED: Skills are no longer used in the two-agent pipeline.
    This endpoint is kept for backward compatibility but returns an empty list.
    """
    try:
        # Return empty list - skills are no longer loaded or used
        return {
            "success": True,
            "data": [],
            "message": "Skills endpoint deprecated - blueprint-based generation is now used"
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
