"""
Pydantic models for API requests and responses.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== STANDARD API RESPONSE ====================

class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    message: Optional[str] = None


# ==================== BRIEF EXTRACTION ====================

class ExtractBriefRequest(BaseModel):
    """Request to extract structured data from raw brief text."""
    brief_text: str = Field(..., min_length=50, description="Raw research brief text")
    

class BriefData(BaseModel):
    """Extracted brief data."""
    name: Optional[str] = None
    objective: Optional[str] = None
    category: Optional[str] = None
    target_audience: Optional[str] = None
    market: Optional[str] = None
    stimulus_description: Optional[str] = None
    competitors: List[str] = []
    specific_questions: Optional[str] = None
    suggested_methodologies: List[str] = []
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ExtractBriefResponse(BaseModel):
    """Response from brief extraction."""
    success: bool = True
    data: BriefData
    raw_brief: str


# ==================== SURVEY GENERATION ====================

class GenerateSurveyRequest(BaseModel):
    """Request to generate survey from brief."""
    brief_data: Dict[str, Any]
    selected_skills: List[str]


class GenerateSurveyResponse(BaseModel):
    """Response from survey generation."""
    success: bool = True
    data: Dict[str, Any]  # Full survey JSON
    validation_log: Optional[Dict[str, Any]] = None


# ==================== PROJECT MANAGEMENT ====================

class ProjectStatus(str):
    """Project status enum."""
    DRAFT_BRIEF = "draft_brief"
    DRAFT_SURVEY = "draft_survey"
    LIVE = "live"
    COMPLETED = "completed"


class CreateProjectRequest(BaseModel):
    """Request to create a new project."""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    brief_text: Optional[str] = None
    brief_data: Optional[Dict[str, Any]] = None


class UpdateProjectRequest(BaseModel):
    """Request to update a project."""
    name: Optional[str] = None
    description: Optional[str] = None
    brief_text: Optional[str] = None
    brief_data: Optional[Dict[str, Any]] = None
    survey_json: Optional[Dict[str, Any]] = None
    validation_log: Optional[Dict[str, Any]] = None


class Project(BaseModel):
    """Project data model."""
    id: str
    name: str
    description: Optional[str] = None
    brief_text: Optional[str] = None
    brief_data: Optional[Dict[str, Any]] = None
    survey_json: Optional[Dict[str, Any]] = None
    validation_log: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ProjectListResponse(BaseModel):
    """Response listing all projects."""
    success: bool = True
    data: List[Project]


# ==================== SKILLS ====================

class Skill(BaseModel):
    """Survey methodology skill."""
    name: str
    description: str
    path: str


class SkillsListResponse(BaseModel):
    """Response listing available skills."""
    success: bool = True
    data: List[Skill]


# ==================== VALIDATION ====================

class ValidateSurveyRequest(BaseModel):
    """Request to validate survey."""
    survey: Dict[str, Any]
    brief: Dict[str, Any]


class ValidateSurveyResponse(BaseModel):
    """Response from survey validation."""
    success: bool = True
    data: Dict[str, Any]  # Validated survey JSON
    validation_log: Dict[str, Any]
    has_errors: bool = False
    error_count: int = 0
    warning_count: int = 0
