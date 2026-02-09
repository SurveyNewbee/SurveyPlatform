"""
Project management endpoints.

Handles CRUD operations for survey projects.
Phase 0: Simple file-based storage
Phase 1+: Can be upgraded to database
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any

from api.models import (
    CreateProjectRequest,
    UpdateProjectRequest,
    Project,
    ProjectListResponse
)

router = APIRouter()

# Storage directory
BACKEND_DIR = Path(__file__).parent.parent.parent
STORAGE_DIR = BACKEND_DIR / "storage" / "projects"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_project_path(project_id: str) -> Path:
    """Get file path for a project."""
    return STORAGE_DIR / f"{project_id}.json"


def load_project(project_id: str) -> Dict[str, Any]:
    """Load project from storage."""
    path = get_project_path(project_id)
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_project(project: Dict[str, Any]) -> None:
    """Save project to storage."""
    project_id = project['id']
    path = get_project_path(project_id)
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(project, f, indent=2, ensure_ascii=False)


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects() -> Dict[str, Any]:
    """
    List all projects.
    
    Returns all projects from storage directory.
    """
    projects = []
    
    for project_file in STORAGE_DIR.glob("*.json"):
        try:
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
                projects.append(Project(**project_data))
        except Exception as e:
            print(f"Warning: Could not load project {project_file}: {e}")
            continue
    
    # Sort by updated_at descending
    projects.sort(key=lambda p: p.updated_at, reverse=True)
    
    return ProjectListResponse(
        success=True,
        data=projects
    )


@router.get("/projects/{project_id}")
async def get_project(project_id: str) -> Dict[str, Any]:
    """
    Get a specific project by ID.
    """
    project = load_project(project_id)
    
    return {
        "success": True,
        "data": project
    }


@router.post("/projects")
async def create_project(request: CreateProjectRequest) -> Dict[str, Any]:
    """
    Create a new project.
    
    Initializes a project with draft_brief status.
    """
    now = datetime.utcnow()
    project_id = str(uuid.uuid4())
    
    project = {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "brief_text": request.brief_text,
        "brief_data": request.brief_data,
        "survey_json": None,
        "validation_log": None,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat()
    }
    
    save_project(project)
    
    return {
        "success": True,
        "data": project
    }


@router.put("/projects/{project_id}")
async def update_project(project_id: str, request: UpdateProjectRequest) -> Dict[str, Any]:
    """
    Update an existing project.
    
    Can update name, description, brief_data, survey_json, or validation_log.
    """
    project = load_project(project_id)
    
    # Update fields
    if request.name is not None:
        project["name"] = request.name
    if request.description is not None:
        project["description"] = request.description
    if request.brief_text is not None:
        project["brief_text"] = request.brief_text
    if request.brief_data is not None:
        project["brief_data"] = request.brief_data
    if request.survey_json is not None:
        project["survey_json"] = request.survey_json
    if request.validation_log is not None:
        project["validation_log"] = request.validation_log
    
    project["updated_at"] = datetime.utcnow().isoformat()
    
    save_project(project)
    
    return {
        "success": True,
        "data": project
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str) -> Dict[str, Any]:
    """
    Delete a project.
    
    Permanently removes project from storage.
    """
    path = get_project_path(project_id)
    
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Project {project_id} not found")
    
    path.unlink()
    
    return {
        "success": True,
        "message": f"Project {project_id} deleted"
    }
