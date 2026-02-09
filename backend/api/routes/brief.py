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

from api.models import (
    ExtractBriefRequest, 
    ExtractBriefResponse,
    BriefData,
    Skill,
    SkillsListResponse
)

# Import from existing scripts
try:
    from extract_brief import load_skills_metadata, extract_brief_from_text
except ImportError:
    # Fallback if function name is different
    import extract_brief as eb_module
    load_skills_metadata = getattr(eb_module, 'load_skills_metadata', None)


router = APIRouter()


@router.post("/extract-brief", response_model=ExtractBriefResponse)
async def extract_brief(request: ExtractBriefRequest) -> Dict[str, Any]:
    """
    Extract structured fields from raw research brief text.
    
    Uses LLM to parse unstructured brief into structured fields.
    """
    try:
        # Set up skills path
        skills_dir = BACKEND_DIR.parent / "skills"
        
        # Call the existing extract_brief module
        # Note: We'll need to adapt the function call based on actual implementation
        import extract_brief as eb
        
        # Create a temporary text file or pass directly
        result = eb.extract_and_save(request.brief_text, output_file=None)
        
        # Map result to our response model
        brief_data = BriefData(
            name=result.get("study_name", ""),
            objective=result.get("objective", ""),
            category=result.get("category", ""),
            target_audience=result.get("target_audience", ""),
            market=result.get("market", "US"),
            stimulus_description=result.get("stimulus", {}).get("description", ""),
            competitors=result.get("competitors", []),
            specific_questions=result.get("specific_questions", ""),
            suggested_methodologies=result.get("skills", []),
            confidence=result.get("extraction_confidence", 0.8)
        )
        
        return ExtractBriefResponse(
            success=True,
            data=brief_data,
            raw_brief=request.brief_text
        )
        
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": "extraction_failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@router.get("/skills", response_model=SkillsListResponse)
async def list_skills() -> Dict[str, Any]:
    """
    Get list of available survey methodology skills.
    
    Returns all skills from the skills/ directory.
    """
    try:
        skills_dir = BACKEND_DIR.parent / "skills"
        
        if load_skills_metadata is None:
            # Fallback: list files directly
            skills = []
            for skill_file in skills_dir.glob("*.md"):
                skills.append(Skill(
                    name=skill_file.stem.replace("-", " ").title(),
                    description="",
                    path=str(skill_file)
                ))
        else:
            # Use the existing function
            skills_data = load_skills_metadata(skills_dir)
            skills = [Skill(**s) for s in skills_data]
        
        return SkillsListResponse(
            success=True,
            data=skills
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "skills_load_failed",
                "message": str(e)
            }
        )
