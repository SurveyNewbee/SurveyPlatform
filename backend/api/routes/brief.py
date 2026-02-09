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
from extract_brief import load_skills_metadata, BriefExtractor


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
            "identified_skills": result.get("skills", []),
        }
        
        # Add optional fields if present
        if result.get("operational"):
            operational = result["operational"]
            if operational.get("timeline"):
                extracted_brief["timeline"] = operational["timeline"]
            if operational.get("budget"):
                extracted_brief["budget"] = operational["budget"]
        
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
    
    Returns all skills from the skills/ directory.
    """
    try:
        skills_dir = BACKEND_DIR.parent / "skills"
        
        # Use the existing function
        skills_data = load_skills_metadata(skills_dir)
        
        # Map to frontend Skill format with id extracted from path
        skills = [
            {
                "id": Path(skill["path"]).stem,  # Use filename without .md as id
                "name": skill["name"],
                "description": skill["description"]
            }
            for skill in skills_data
        ]
        
        return {
            "success": True,
            "data": skills
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }
