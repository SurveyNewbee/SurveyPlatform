"""
Generate realistic dummy survey data matching quotas, skip logic, and market patterns.
Integrates with existing survey schema from generate_survey.py output.
"""

import json
import os
from typing import Dict, Any

# Configure LangSmith tracing if API key is available
if os.environ.get('LANGCHAIN_API_KEY'):
    os.environ['LANGCHAIN_TRACING_V2'] = 'true'
    os.environ['LANGCHAIN_PROJECT'] = 'survey-platform-data-generation'

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

def generate_dummy_data(project_id: str, survey_schema: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Python script that creates dummy data for a survey.
    
    Args:
        project_id: UUID of the project
        survey_schema: Output from generate_survey.py (contains SAMPLE_REQUIREMENTS, FLOW, etc.)
    
    Returns:
        {
            "script_path": "storage/analysis_scripts/{project_id}_data_gen.py",
            "output_path": "storage/datasets/{project_id}_dummy_data.csv",
            "status": "generated"
        }
    """
    
    # Load data generation skill
    skill_path = '../skills/data-generation/dummy-data-skill.md'
    with open(skill_path, 'r', encoding='utf-8') as f:
        skill_content = f.read()
    
    # Extract key requirements from survey schema
    sample_size = survey_schema.get('SAMPLE_REQUIREMENTS', {}).get('total_sample', 1000)
    hard_quotas = survey_schema.get('SAMPLE_REQUIREMENTS', {}).get('hard_quotas', {})
    soft_quotas = survey_schema.get('SAMPLE_REQUIREMENTS', {}).get('soft_quotas', {})
    methodology = survey_schema.get('STUDY_METADATA', {}).get('study_type', 'general')
    
    # Build prompt
    prompt = f"""
{skill_content}

Generate a complete Python script that creates realistic dummy survey data.

SURVEY SCHEMA:
{json.dumps(survey_schema, indent=2)}

REQUIREMENTS:
1. Generate exactly {sample_size} responses
2. Respect hard quotas: {json.dumps(hard_quotas, indent=2)}
3. Approximate soft quotas: {json.dumps(soft_quotas, indent=2)}
4. Apply all routing rules from FLOW section
5. Create realistic response patterns for {methodology} methodology
6. Include:
   - Brand funnel attrition (if applicable)
   - Correlated responses (quality → NPS, etc.)
   - Market-realistic distributions
   - Verbatim text matching rating patterns
   - Quality flags (speeders, straightliners)

OUTPUT FORMAT:
- Complete Python script using pandas, numpy, faker
- Set random seed for reproducibility (seed=42)
- Save to CSV: storage/datasets/{project_id}_dummy_data.csv
- Print summary statistics
- Include data validation checks

Return ONLY executable Python code with no markdown fences.
"""

    # Call Claude
    print(f"Calling Claude to generate data script for project {project_id}...")
    
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

    # Remove markdown fences if present
    if code.startswith('```python'):
        code = code.split('```python')[1].split('```')[0].strip()
    elif code.startswith('```'):
        code = code.split('```')[1].split('```')[0].strip()
    
    # Save script
    script_dir = 'storage/analysis_scripts'
    os.makedirs(script_dir, exist_ok=True)
    script_path = f'{script_dir}/{project_id}_data_gen.py'
    
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(code)
    
    return {
        'script_path': script_path,
        'output_path': f'storage/datasets/{project_id}_dummy_data.csv',
        'status': 'generated'
    }


def execute_data_generation(script_path: str) -> Dict[str, Any]:
    """
    Execute the generated data generation script safely.
    
    Args:
        script_path: Path to the generated Python script
    
    Returns:
        {
            "status": "success" | "error",
            "message": "Summary statistics",
            "rows_generated": 1500,
            "output_file": "path/to/csv"
        }
    """
    import subprocess
    import sys
    
    try:
        # Execute in subprocess for safety
        print(f"Executing script: {script_path}")
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=120  # 2 minute timeout
        )
        print(f"Script execution completed with return code: {result.returncode}")
        
        if result.returncode == 0:
            return {
                'status': 'success',
                'message': result.stdout or 'Data generated successfully',
                'output_file': result.stdout.split('Saved to: ')[-1].strip() if 'Saved to:' in result.stdout else None
            }
        else:
            error_msg = result.stderr or result.stdout or 'Unknown error during data generation'
            return {
                'status': 'error',
                'message': error_msg
            }
    
    except subprocess.TimeoutExpired:
        return {
            'status': 'error',
            'message': 'Data generation timed out after 2 minutes'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e)
        }
