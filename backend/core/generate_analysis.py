"""
Generate methodology-specific analysis code for survey data.
Matches existing skill system architecture.
"""

import json
import os
from typing import Dict, Any

# Configure LangSmith tracing if API key is available
if os.environ.get('LANGCHAIN_API_KEY'):
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_PROJECT'] = 'survey-platform-analysis-generation'

try:
    from langchain_anthropic import ChatAnthropic
    client = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        anthropic_api_key=os.environ.get('ANTHROPIC_API_KEY'),
        max_tokens=16000
    )
    USE_LANGCHAIN = True
except ImportError:
    # Fallback to direct Anthropic SDK if LangChain not available
    from anthropic import Anthropic
    client = Anthropic(api_key=os.environ.get('ANTHROPIC_API_KEY'))
    USE_LANGCHAIN = False

# Methodology → Analysis skill mapping
ANALYSIS_SKILL_MAP = {
    'market_measurement': 'brand-tracking-analysis',
    'pricing': 'pricing-analysis',
    'concept_testing': 'concept-testing-analysis',
    'message_testing': 'message-testing-analysis',
    'conjoint': 'conjoint-analysis',
    'maxdiff': 'maxdiff-analysis',
    'segmentation': 'segmentation-analysis',
    'nps': 'nps-analysis',
    'brand_tracking': 'brand-tracking-analysis',
    'usage_attitudes': 'usage-attitudes-analysis',
    'awareness_trial_usage': 'awareness-trial-usage-analysis',
}

def generate_analysis(project_id: str, survey_schema: Dict[str, Any], data_path: str) -> Dict[str, Any]:
    """
    Generate Python analysis code tailored to survey methodology.
    
    Args:
        project_id: UUID of the project
        survey_schema: Survey structure from generate_survey.py
        data_path: Path to CSV data file
    
    Returns:
        {
            "script_path": "storage/analysis_scripts/{project_id}_analysis.py",
            "results_path": "storage/datasets/{project_id}_results.json",
            "status": "generated"
        }
    """
    
    # Determine methodology
    study_type = survey_schema.get('brief_data', {}).get('study_type', 'general')
    methodology = survey_schema.get('brief_data', {}).get('primary_methodology', 'descriptive')
    
    # Load appropriate analysis skill
    skill_name = ANALYSIS_SKILL_MAP.get(study_type, 'general-analysis')
    skill_path = f'../skills/analysis/{skill_name}.md'
    
    if not os.path.exists(skill_path):
        skill_path = '../skills/analysis/brand-tracking-analysis.md'  # Fallback
    
    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    
    # Extract analysis requirements from schema
    analysis_plan = survey_schema.get('ANALYSIS_PLAN', {})
    primary_analyses = analysis_plan.get('primary_analyses', [])
    deliverables = analysis_plan.get('deliverables', [])
    
    # Build prompt
    prompt = f"""
{skill_content}

Generate complete Python analysis code for this survey study.

SURVEY SCHEMA:
{json.dumps(survey_schema, indent=2)}

DATA FILE: {data_path}

REQUIRED ANALYSES:
{json.dumps(primary_analyses, indent=2)}

REQUIRED DELIVERABLES:
{json.dumps(deliverables, indent=2)}

GENERATE:
1. Complete Python script that:
   - Loads data from CSV
   - Performs all analyses from ANALYSIS_PLAN
   - Generates all deliverables
   - Saves results to JSON for frontend consumption

2. Output structure:
   {{
       "executive_summary": ["insight 1", "insight 2", ...],
       "demographics": {{"age": {{"18-24": 150, ...}}, ...}},
       "questions": [
           {{
               "question_id": "MS7_Q1",
               "question_text": "...",
               "type": "nps",
               "results": {{"promoters": 30, "passives": 50, "detractors": 20}},
               "crosstabs": {{...}}
           }},
           ...
       ],
       "specialty_analyses": [...]  # Van Westendorp, conjoint utilities, etc.
   }}

3. Use pandas, numpy, scipy.stats, scikit-learn
4. Include statistical significance testing
5. Add error handling
6. Save to: storage/datasets/{project_id}_results.json

Return ONLY executable Python code with no markdown fences.
"""

    # Call Claude
    print(f"Calling Claude to generate analysis script for project {project_id}...")
    
    if USE_LANGCHAIN:
        response = client.invoke(prompt)
        code = response.content
    else:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=16000,
            messages=[{"role": "user", "content": prompt}]
        )
        code = response.content[0].text
    
    print(f"Received response from Claude ({len(code)} chars)")
    
    # Extract code

    # Remove markdown fences
    if code.startswith('```python'):
        code = code.split('```python')[1].split('```')[0].strip()
    elif code.startswith('```'):
        code = code.split('```')[1].split('```')[0].strip()
    
    # Save script
    script_dir = 'storage/analysis_scripts'
    os.makedirs(script_dir, exist_ok=True)
    script_path = f'{script_dir}/{project_id}_analysis.py'
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return {
        'script_path': script_path,
        'results_path': f'storage/datasets/{project_id}_results.json',
        'status': 'generated'
    }


def execute_analysis(script_path: str) -> Dict[str, Any]:
    """
    Execute the generated analysis script safely.
    
    Returns:
        {
            "status": "success" | "error",
            "message": "Analysis completed",
            "results_file": "path/to/results.json"
        }
    """
    import subprocess
    import sys
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            return {
                'status': 'success',
                'message': result.stdout,
                'results_file': result.stdout.split('Results saved to: ')[-1].strip() if 'Results saved to:' in result.stdout else None
            }
        else:
            return {
                'status': 'error',
                'message': result.stderr
            }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': 'Analysis timed out after 5 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
