"""
Survey generation and validation endpoints.
"""

import sys
import json
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any, Optional, List
import traceback

# Add core to path
BACKEND_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_DIR / "core"))

from api.models import (
    GenerateSurveyRequest,
    EditQuestionRequest,
    AddQuestionRequest,
    DeleteQuestionRequest,
    ReorderQuestionRequest,
    EditSectionRequest,
    SaveCommentRequest,
    GetCommentsRequest,
    SummarizeCommentsRequest,
    ApplyCommentEditsRequest
)

router = APIRouter()


@router.post("/generate-survey/stream")
async def generate_survey_stream(request: GenerateSurveyRequest):
    """
    Generate survey from approved brief with streaming.
    Returns Server-Sent Events (SSE) stream of LLM tokens.
    """
    try:
        from generate_survey import SurveyGenerator
        
        brief_for_generator = request.brief_data
        generator = SurveyGenerator()
        
        return StreamingResponse(
            generator.generate_async_stream(brief_for_generator),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except Exception as e:
        traceback.print_exc()
        # Return error as SSE
        async def error_stream():
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")


@router.post("/generate-survey")
async def generate_survey(request: GenerateSurveyRequest) -> Dict[str, Any]:
    """
    Generate survey from approved brief using AI.
    
    Takes approved brief_data (which includes survey_blueprint from Agent 1) and
    generates the complete survey using Agent 2.
    
    The brief_data should be the full result from Agent 1 (extract-brief endpoint),
    which has been reviewed and approved by the user.
    """
    try:
        from generate_survey import SurveyGenerator
        from loi_calculator import LOICalculator
        
        # brief_data now contains the full Agent 1 output including survey_blueprint
        # No need to transform or select skills - just pass through to generator
        brief_for_generator = request.brief_data
        
        # Create generator (no skills_dir needed anymore)
        print(f"Creating SurveyGenerator...")
        generator = SurveyGenerator()
        
        # Generate survey
        print(f"Generating survey from approved brief with blueprint...")
        survey_json = generator.generate(brief_for_generator, stream_output=False)
        print(f"Survey generation result: {type(survey_json)}, has data: {survey_json is not None}")
        
        if not survey_json:
            raise ValueError("Survey generation returned no result")
        
        # Check if survey has required top-level structure
        has_main_section = 'MAIN_SECTION' in survey_json
        subsection_count = len(survey_json.get('MAIN_SECTION', {}).get('sub_sections', [])) if has_main_section else 0
        print(f"Survey has MAIN_SECTION: {has_main_section}, subsections: {subsection_count}")
        
        # Add LOI configuration with default slider position at Standard tier
        print("Adding LOI configuration...")
        loi_calc = LOICalculator(survey_json)
        survey_json = loi_calc.add_loi_config(initial_position=50)
        print(f"LOI config added: {survey_json.get('loi_config', {})}")
        
        # For now, return without validation
        # TODO: Add validation step
        result = {
            "success": True,
            "data": {
                "survey": survey_json,
                "validation_log": {
                    "is_valid": True,
                    "error_count": 0,
                    "warning_count": 0,
                    "entries": []
                }
            }
        }
        print(f"Returning result: success={result['success']}, has survey: {'survey' in result.get('data', {})}")
        return result
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/validate-survey")
async def validate_survey(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate survey against rules.
    
    TODO: Implement validation pipeline.
    For now, returns placeholder response.
    """
    try:
        # TODO: Implement actual validation
        return {
            "success": True,
            "data": {
                "is_valid": True,
                "error_count": 0,
                "warning_count": 0,
                "entries": []
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


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


@router.post("/update-loi")
async def update_loi(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update LOI configuration based on slider position.
    
    Request body:
    {
        "survey": {...},
        "slider_position": 50
    }
    
    Returns updated survey with new loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        slider_position = request.get("slider_position", 50)
        
        if not survey:
            raise ValueError("Survey data required")
        
        # Update LOI configuration
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.update_loi_config(slider_position)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/pin-question")
async def pin_question(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pin a question to always show it regardless of LOI setting.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Pin question
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.pin_question(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/exclude-question")
async def exclude_question(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Exclude a question to always hide it regardless of LOI setting.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Exclude question
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.exclude_question(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reset-question-override")
async def reset_question_override(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reset a question's override to default LOI-based visibility.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1"
    }
    
    Returns updated survey and loi_config.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.get("survey")
        question_id = request.get("question_id")
        
        if not survey or not question_id:
            raise ValueError("Survey and question_id required")
        
        # Reset override
        loi_calc = LOICalculator(survey)
        loi_config = loi_calc.reset_question_override(question_id)
        
        return {
            "success": True,
            "data": {
                "survey": survey,
                "loi_config": loi_config
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/edit-question")
async def edit_question(request: EditQuestionRequest) -> Dict[str, Any]:
    """
    Edit a question's text, options, or other properties.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q1",
        "updates": {
            "question_text": "New text",
            "response_options": [...],
            "skip_logic": {...}
        }
    }
    
    Returns updated survey with recalculated LOI.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.survey
        question_id = request.question_id
        updates = request.updates
        
        # Find and update the question
        question = _find_question(survey, question_id)
        if not question:
            return {
                "success": False,
                "error": f"Question {question_id} not found"
            }
        
        # Apply updates
        for key, value in updates.items():
            question[key] = value
        
        # Recalculate LOI if question text or options changed
        if "question_text" in updates or "response_options" in updates or "options" in updates:
            loi_calc = LOICalculator(survey)
            current_position = survey.get("loi_config", {}).get("slider_position", 50)
            loi_config = loi_calc.update_loi_config(current_position)
            survey["loi_config"] = loi_config
        
        return {
            "success": True,
            "data": {
                "survey": survey
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/add-question")
async def add_question(request: AddQuestionRequest) -> Dict[str, Any]:
    """
    Add a new question to a section.
    
    Request body:
    {
        "survey": {...},
        "section_id": "MAIN_SECTION",
        "subsection_id": "MS1",
        "question": {
            "question_id": "MS1_Q5_NEW",
            "question_text": "...",
            "question_type": "single_select",
            ...
        },
        "position": 2  // Optional: insert at position, else append
    }
    
    Returns updated survey with new question.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.survey
        section_id = request.section_id
        subsection_id = request.subsection_id
        question = request.question
        position = request.position
        
        # Find the target section
        questions = _get_section_questions(survey, section_id, subsection_id)
        if questions is None:
            return {
                "success": False,
                "error": f"Section {section_id}/{subsection_id} not found"
            }
        
        # Add question at position or append
        if position is not None and 0 <= position <= len(questions):
            questions.insert(position, question)
        else:
            questions.append(question)
        
        # Recalculate LOI
        loi_calc = LOICalculator(survey)
        current_position = survey.get("loi_config", {}).get("slider_position", 50)
        loi_config = loi_calc.update_loi_config(current_position)
        survey["loi_config"] = loi_config
        
        return {
            "success": True,
            "data": {
                "survey": survey
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/delete-question")
async def delete_question(request: DeleteQuestionRequest) -> Dict[str, Any]:
    """
    Delete a question from the survey.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q3"
    }
    
    Returns updated survey.
    """
    try:
        from loi_calculator import LOICalculator
        
        survey = request.survey
        question_id = request.question_id
        
        # Find and remove the question
        removed = _remove_question(survey, question_id)
        if not removed:
            return {
                "success": False,
                "error": f"Question {question_id} not found"
            }
        
        # Recalculate LOI
        loi_calc = LOICalculator(survey)
        current_position = survey.get("loi_config", {}).get("slider_position", 50)
        loi_config = loi_calc.update_loi_config(current_position)
        survey["loi_config"] = loi_config
        
        return {
            "success": True,
            "data": {
                "survey": survey
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/reorder-question")
async def reorder_question(request: ReorderQuestionRequest) -> Dict[str, Any]:
    """
    Move a question up or down within its section.
    
    Request body:
    {
        "survey": {...},
        "question_id": "MS1_Q3",
        "direction": "up" | "down"
    }
    
    Returns updated survey.
    """
    try:
        survey = request.survey
        question_id = request.question_id
        direction = request.direction
        
        # Find and reorder the question
        reordered = _reorder_question(survey, question_id, direction)
        if not reordered:
            return {
                "success": False,
                "error": f"Could not reorder question {question_id}"
            }
        
        return {
            "success": True,
            "data": {
                "survey": survey
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


@router.post("/edit-section")
async def edit_section(request: EditSectionRequest) -> Dict[str, Any]:
    """
    Edit a section title.
    
    Request body:
    {
        "survey": {...},
        "section_id": "MAIN_SECTION",
        "subsection_id": "MS1",
        "title": "New Section Title"
    }
    
    Returns updated survey.
    """
    try:
        survey = request.survey
        section_id = request.section_id
        subsection_id = request.subsection_id
        title = request.title
        
        # Find and update section title
        updated = _update_section_title(survey, section_id, subsection_id, title)
        if not updated:
            return {
                "success": False,
                "error": f"Section {section_id}/{subsection_id} not found"
            }
        
        return {
            "success": True,
            "data": {
                "survey": survey
            }
        }
        
    except Exception as e:
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


# Helper functions for survey manipulation

def _find_question(survey: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
    """Find a question by ID in the survey."""
    # Check SCREENER
    if "SCREENER" in survey and "questions" in survey["SCREENER"]:
        for q in survey["SCREENER"]["questions"]:
            if q.get("question_id") == question_id:
                return q
    
    # Check MAIN_SECTION subsections
    if "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
        for subsection in survey["MAIN_SECTION"]["sub_sections"]:
            if "questions" in subsection:
                for q in subsection["questions"]:
                    if q.get("question_id") == question_id:
                        return q
    
    # Check DEMOGRAPHICS
    if "DEMOGRAPHICS" in survey and "questions" in survey["DEMOGRAPHICS"]:
        for q in survey["DEMOGRAPHICS"]["questions"]:
            if q.get("question_id") == question_id:
                return q
    
    return None


def _get_section_questions(survey: Dict[str, Any], section_id: str, subsection_id: Optional[str]) -> Optional[List]:
    """Get the questions list for a section."""
    if section_id == "SCREENER":
        return survey.get("SCREENER", {}).get("questions")
    elif section_id == "DEMOGRAPHICS":
        return survey.get("DEMOGRAPHICS", {}).get("questions")
    elif section_id == "MAIN_SECTION" and subsection_id:
        if "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
            for subsection in survey["MAIN_SECTION"]["sub_sections"]:
                if subsection.get("sub_section_id") == subsection_id:
                    return subsection.get("questions")
    return None


def _remove_question(survey: Dict[str, Any], question_id: str) -> bool:
    """Remove a question from the survey."""
    # Check SCREENER
    if "SCREENER" in survey and "questions" in survey["SCREENER"]:
        questions = survey["SCREENER"]["questions"]
        for i, q in enumerate(questions):
            if q.get("question_id") == question_id:
                questions.pop(i)
                return True
    
    # Check MAIN_SECTION subsections
    if "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
        for subsection in survey["MAIN_SECTION"]["sub_sections"]:
            if "questions" in subsection:
                questions = subsection["questions"]
                for i, q in enumerate(questions):
                    if q.get("question_id") == question_id:
                        questions.pop(i)
                        return True
    
    # Check DEMOGRAPHICS
    if "DEMOGRAPHICS" in survey and "questions" in survey["DEMOGRAPHICS"]:
        questions = survey["DEMOGRAPHICS"]["questions"]
        for i, q in enumerate(questions):
            if q.get("question_id") == question_id:
                questions.pop(i)
                return True
    
    return False


def _reorder_question(survey: Dict[str, Any], question_id: str, direction: str) -> bool:
    """Reorder a question within its section."""
    # Find the question and its containing list
    questions_list = None
    question_index = -1
    
    # Check SCREENER
    if "SCREENER" in survey and "questions" in survey["SCREENER"]:
        questions = survey["SCREENER"]["questions"]
        for i, q in enumerate(questions):
            if q.get("question_id") == question_id:
                questions_list = questions
                question_index = i
                break
    
    # Check MAIN_SECTION subsections
    if questions_list is None and "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
        for subsection in survey["MAIN_SECTION"]["sub_sections"]:
            if "questions" in subsection:
                questions = subsection["questions"]
                for i, q in enumerate(questions):
                    if q.get("question_id") == question_id:
                        questions_list = questions
                        question_index = i
                        break
                if questions_list:
                    break
    
    # Check DEMOGRAPHICS
    if questions_list is None and "DEMOGRAPHICS" in survey and "questions" in survey["DEMOGRAPHICS"]:
        questions = survey["DEMOGRAPHICS"]["questions"]
        for i, q in enumerate(questions):
            if q.get("question_id") == question_id:
                questions_list = questions
                question_index = i
                break
    
    if questions_list is None or question_index == -1:
        return False
    
    # Perform the reorder
    if direction == "up" and question_index > 0:
        questions_list[question_index], questions_list[question_index - 1] = \
            questions_list[question_index - 1], questions_list[question_index]
        return True
    elif direction == "down" and question_index < len(questions_list) - 1:
        questions_list[question_index], questions_list[question_index + 1] = \
            questions_list[question_index + 1], questions_list[question_index]
        return True
    
    return False


def _update_section_title(survey: Dict[str, Any], section_id: str, subsection_id: Optional[str], title: str) -> bool:
    """Update a section's title."""
    if section_id == "SCREENER" and "SCREENER" in survey:
        survey["SCREENER"]["section_title"] = title
        return True
    elif section_id == "DEMOGRAPHICS" and "DEMOGRAPHICS" in survey:
        survey["DEMOGRAPHICS"]["section_title"] = title
        return True
    elif section_id == "MAIN_SECTION" and subsection_id:
        if "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
            for subsection in survey["MAIN_SECTION"]["sub_sections"]:
                if subsection.get("sub_section_id") == subsection_id:
                    subsection["sub_section_title"] = title
                    return True
    return False


# ==================== COMMENT ENDPOINTS ====================

@router.post("/save-comment")
async def save_comment(request: SaveCommentRequest):
    """
    Save a comment on a question in preview mode.
    """
    try:
        from pathlib import Path
        import json
        import time
        
        storage_dir = BACKEND_DIR / "storage" / "projects"
        project_file = storage_dir / f"{request.project_id}.json"
        
        if not project_file.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load project
        with open(project_file, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        # Initialize comments array if not exists
        if "comments" not in project:
            project["comments"] = []
        
        # Create comment
        comment = {
            "id": f"comment_{int(time.time() * 1000)}",
            "question_id": request.question_id,
            "text": request.text,
            "timestamp": int(time.time() * 1000)
        }
        
        project["comments"].append(comment)
        
        # Save project
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2)
        
        return {
            "success": True,
            "data": {
                "comment": comment,
                "total_comments": len(project["comments"])
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error saving comment: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/get-comments")
async def get_comments(request: GetCommentsRequest):
    """
    Get all comments for a project.
    """
    try:
        from pathlib import Path
        import json
        
        storage_dir = BACKEND_DIR / "storage" / "projects"
        project_file = storage_dir / f"{request.project_id}.json"
        
        if not project_file.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load project
        with open(project_file, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        comments = project.get("comments", [])
        
        return {
            "success": True,
            "data": {
                "comments": comments,
                "total_comments": len(comments)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting comments: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/summarize-comments")
async def summarize_comments(request: SummarizeCommentsRequest):
    """
    Generate targeted improvements for each commented question using AI.
    """
    try:
        from pathlib import Path
        import json
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        storage_dir = BACKEND_DIR / "storage" / "projects"
        project_file = storage_dir / f"{request.project_id}.json"
        
        if not project_file.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load project
        with open(project_file, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        comments = project.get("comments", [])
        
        if not comments:
            return {
                "success": True,
                "data": {
                    "improvements": []
                }
            }
        
        # Get survey for context
        survey = project.get("survey_json", {})
        
        # Generate improvements for each commented question
        improvements = []
        llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
        
        for comment in comments:
            question = _find_question_for_comment(survey, comment["question_id"])
            if not question:
                continue
            
            # Create prompt for this specific question
            prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a survey design expert. Your task is to improve a survey question based on user feedback.

Given a question and user feedback, generate an improved version of the question.

Rules:
- Maintain the question type and structure
- Address the specific feedback provided
- Keep the question clear and professional
- Preserve any options/scales unless feedback suggests changes
- Be conservative - only change what's needed

Output as JSON:
{{
  "improved_question": {{
    "question_text": "improved text here",
    "options": ["option1", "option2"] (if applicable),
    "explanation": "brief explanation of what changed and why"
  }}
}}

If the question has options/scale items, include them in the improved version."""),
                ("human", """Current Question:
Type: {question_type}
Text: {question_text}
Options: {options}

User Feedback: {feedback}

Generate an improved version of this question.""")
            ])
            
            # Format question data
            question_type = question.get("question_type", "unknown")
            question_text = question.get("question_text", "")
            options = question.get("options", question.get("scale_items", []))
            
            # Call LLM
            chain = prompt | llm
            response = chain.invoke({
                "question_type": question_type,
                "question_text": question_text,
                "options": json.dumps(options) if options else "N/A",
                "feedback": comment["text"]
            })
            
            # Parse response
            content = response.content
            print(f"LLM response for {comment['question_id']}: {content[:200]}")
            
            # Extract JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            try:
                result = json.loads(content)
                improved = result.get("improved_question", {})
                
                improvements.append({
                    "question_id": comment["question_id"],
                    "original": {
                        "question_text": question_text,
                        "options": options
                    },
                    "improved": {
                        "question_text": improved.get("question_text", question_text),
                        "options": improved.get("options", options)
                    },
                    "explanation": improved.get("explanation", ""),
                    "feedback": comment["text"]
                })
            except json.JSONDecodeError as e:
                print(f"Failed to parse improvement for {comment['question_id']}: {e}")
                # Skip this improvement if parsing fails
                continue
        
        # Clear comments after successfully generating improvements
        project["comments"] = []
        with open(project_file, 'w', encoding='utf-8') as f:
            json.dump(project, f, indent=2, ensure_ascii=False)
        print(f"Cleared {len(comments)} comments after generating improvements")
        
        return {
            "success": True,
            "data": {
                "improvements": improvements
            }
        }
        
    except Exception as e:
        print(f"Error generating improvements: {str(e)}")
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "detail": f"Error: {str(e)}"
        }


def _find_question_for_comment(survey: Dict[str, Any], question_id: str) -> Optional[Dict[str, Any]]:
    """Find a question by ID in the survey structure."""
    # Check SCREENER
    if "SCREENER" in survey and "questions" in survey["SCREENER"]:
        for q in survey["SCREENER"]["questions"]:
            if q.get("question_id") == question_id:
                return q
    
    # Check MAIN_SECTION subsections
    if "MAIN_SECTION" in survey and "sub_sections" in survey["MAIN_SECTION"]:
        for subsection in survey["MAIN_SECTION"]["sub_sections"]:
            if "questions" in subsection:
                for q in subsection["questions"]:
                    if q.get("question_id") == question_id:
                        return q
    
    # Check DEMOGRAPHICS
    if "DEMOGRAPHICS" in survey and "questions" in survey["DEMOGRAPHICS"]:
        for q in survey["DEMOGRAPHICS"]["questions"]:
            if q.get("question_id") == question_id:
                return q
    
    return None


@router.post("/apply-comment-edits/stream")
async def apply_comment_edits_stream(request: ApplyCommentEditsRequest):
    """
    Generate and stream AI edits based on selected comment themes.
    Returns Server-Sent Events (SSE) stream with proposed changes.
    """
    try:
        from pathlib import Path
        import json
        from langchain_openai import ChatOpenAI
        from langchain_core.prompts import ChatPromptTemplate
        
        storage_dir = BACKEND_DIR / "storage" / "projects"
        project_file = storage_dir / f"{request.project_id}.json"
        
        if not project_file.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Load project
        with open(project_file, 'r', encoding='utf-8') as f:
            project = json.load(f)
        
        survey = project.get("survey_json", {})
        comments = project.get("comments", [])
        
        # Get themes from previous summarization (stored in memory or re-summarize)
        # For now, we'll need to re-run summarization to get theme details
        # In production, you might cache this
        
        # Build comment context
        comment_context = []
        for comment in comments:
            question = _find_question_for_comment(survey, comment["question_id"])
            comment_context.append({
                "question_id": comment["question_id"],
                "question_text": question.get("question_text", "Unknown") if question else "Unknown",
                "question_type": question.get("question_type", "unknown") if question else "unknown",
                "options": question.get("options", []) if question else [],
                "comment": comment["text"]
            })
        
        # Create LLM prompt for generating edits
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a survey design expert generating specific edits to improve a survey based on user feedback.

Your task: Generate a list of specific, actionable edits to questions based on the selected feedback themes.

For each edit, provide:
1. question_id: The ID of the question to modify
2. field: What field to change ("question_text", "options", "scale", etc.)
3. old_value: Current value (for options, provide full array)
4. new_value: Proposed new value
5. reason: Brief explanation referencing the feedback

Output as JSON array:
[
  {{
    "question_id": "SCREEN_1",
    "field": "options",
    "old_value": ["Yes", "No"],
    "new_value": ["Yes", "No", "Not sure"],
    "reason": "Added neutral option per user feedback"
  }}
]

Guidelines:
- Be conservative: only make edits directly supported by feedback
- Maintain question intent and flow
- For option changes, include the FULL new options array
- For text changes, preserve the question structure
- Each edit should be independently applicable

Available question types: single_choice, multiple_choice, open_ended, numeric_input, scale, matrix"""),
            ("human", """Survey context:

{comment_list}

Selected theme IDs to address: {theme_ids}

Generate specific edits to address the feedback in these themes.""")
        ])
        
        # Format comments
        comment_list = "\n\n".join([
            f"Question: {c['question_text']}\nID: {c['question_id']}\nType: {c['question_type']}\nCurrent options: {c.get('options', 'N/A')}\nFeedback: {c['comment']}"
            for c in comment_context
        ])
        
        async def generate_edits():
            try:
                # Call LLM
                llm = ChatOpenAI(model="gpt-4o", temperature=0.3)
                chain = prompt | llm
                
                # Stream the response
                yield f"data: {json.dumps({'type': 'status', 'message': 'Analyzing feedback...'})}\n\n"
                
                response = chain.invoke({
                    "comment_list": comment_list,
                    "theme_ids": ", ".join(request.theme_ids)
                })
                
                yield f"data: {json.dumps({'type': 'status', 'message': 'Generating edits...'})}\n\n"
                
                # Parse edits
                content = response.content
                # Try to extract JSON from markdown code blocks if present
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                
                edits = json.loads(content)
                
                # Stream each edit
                for idx, edit in enumerate(edits):
                    yield f"data: {json.dumps({'type': 'edit', 'edit': edit, 'index': idx})}\n\n"
                
                yield f"data: {json.dumps({'type': 'complete', 'total': len(edits)})}\n\n"
                
            except json.JSONDecodeError as e:
                error_msg = f"Failed to parse LLM response: {str(e)}"
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
            except Exception as e:
                error_msg = f"Error generating edits: {str(e)}"
                yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
        
        return StreamingResponse(
            generate_edits(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in apply-comment-edits: {str(e)}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
