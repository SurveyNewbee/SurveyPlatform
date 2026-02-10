"""
API endpoints for dummy data generation.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

from core.generate_dummy_data import generate_dummy_data, execute_data_generation

router = APIRouter()

class DataGenerationRequest(BaseModel):
    project_id: str

class DataGenerationResponse(BaseModel):
    status: str
    script_path: str
    output_path: str
    message: str = ""

@router.post('/generate-data', response_model=DataGenerationResponse)
async def generate_data_endpoint(request: DataGenerationRequest):
    """
    Generate dummy data for a survey project.
    
    Flow:
    1. Load project from storage
    2. Generate Python script using Claude
    3. Execute script to create CSV
    4. Return paths and status
    """
    try:
        # Load project
        project_path = f'storage/projects/{request.project_id}.json'
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        with open(project_path, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        # Check if survey exists
        if 'survey_json' not in project:
            raise HTTPException(status_code=400, detail="Survey not generated yet")
        
        survey_schema = project['survey_json']
        
        # Generate data script
        print(f"Starting data generation for project {request.project_id}")
        gen_result = generate_dummy_data(request.project_id, survey_schema)
        print(f"Script generated at: {gen_result['script_path']}")
        
        # Execute script
        print(f"Executing data generation script...")
        exec_result = execute_data_generation(gen_result['script_path'])
        print(f"Execution completed with status: {exec_result['status']}")
        
        if exec_result['status'] == 'error':
            raise HTTPException(status_code=500, detail=exec_result['message'])
        
        # Update project with data path
        project['dummy_data_path'] = gen_result['output_path']
        project['data_generated_at'] = exec_result.get('message', '')
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2)
        
        return DataGenerationResponse(
            status='success',
            script_path=gen_result['script_path'],
            output_path=gen_result['output_path'],
            message=exec_result.get('message', 'Data generated successfully')[:500]  # Truncate long messages
        )
    
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(f"Error in generate_data_endpoint: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/data/{project_id}')
async def get_data_status(project_id: str):
    """
    Check if dummy data exists for a project.
    """
    project_path = f'storage/projects/{project_id}.json'
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    with open(project_path, 'r', encoding='utf-8') as f:
        project = json.load(f)
    
    data_path = project.get('dummy_data_path')
    
    return {
        'has_data': data_path is not None and os.path.exists(data_path),
        'data_path': data_path,
        'generated_at': project.get('data_generated_at')
    }
