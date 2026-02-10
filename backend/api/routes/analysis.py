"""
API endpoints for analysis generation and execution.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import json
import os

from core.generate_analysis import generate_analysis, execute_analysis

router = APIRouter()

class AnalysisGenerationRequest(BaseModel):
    project_id: str

class AnalysisGenerationResponse(BaseModel):
    status: str
    script_path: str
    results_path: str
    message: str = ""

@router.post('/generate-analysis', response_model=AnalysisGenerationResponse)
async def generate_analysis_endpoint(request: AnalysisGenerationRequest):
    """
    Generate and execute analysis code for survey data.
    
    Flow:
    1. Load project and check for dummy data
    2. Generate Python analysis script using Claude
    3. Execute script to create results JSON
    4. Return paths and status
    """
    try:
        # Load project
        project_path = f'storage/projects/{request.project_id}.json'
        if not os.path.exists(project_path):
            raise HTTPException(status_code=404, detail="Project not found")
        
        with open(project_path, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        # Check for survey and data
        if 'survey_json' not in project:
            raise HTTPException(status_code=400, detail="Survey not generated yet")
        
        data_path = project.get('dummy_data_path')
        if not data_path or not os.path.exists(data_path):
            raise HTTPException(status_code=400, detail="Dummy data not generated yet")
        
        survey_schema = project['survey_json']
        
        # Generate analysis script
        gen_result = generate_analysis(request.project_id, survey_schema, data_path)
        
        # Execute script
        exec_result = execute_analysis(gen_result['script_path'])
        
        if exec_result['status'] == 'error':
            raise HTTPException(status_code=500, detail=exec_result['message'])
        
        # Update project with results path
        project['analysis_results_path'] = gen_result['results_path']
        project['analysis_generated_at'] = exec_result.get('message', '')
        
        with open(project_path, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2)
        
        return AnalysisGenerationResponse(
            status='success',
            script_path=gen_result['script_path'],
            results_path=gen_result['results_path'],
            message=exec_result['message']
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/results/{project_id}')
async def get_analysis_results(project_id: str):
    """
    Retrieve analysis results JSON for frontend consumption.
    """
    project_path = f'storage/projects/{project_id}.json'
    if not os.path.exists(project_path):
        raise HTTPException(status_code=404, detail="Project not found")
    
    with open(project_path, 'r', encoding='utf-8') as f:
        project = json.load(f)
    
    results_path = project.get('analysis_results_path')
    
    if not results_path or not os.path.exists(results_path):
        raise HTTPException(status_code=404, detail="Analysis results not found")
    
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results
