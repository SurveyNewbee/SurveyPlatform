# Integration Guide - Using Basics Scripts

This guide explains how to integrate the existing Python scripts from `Basics/` into the new platform.

## Overview

The `Basics/` folder contains working, tested Python scripts:
- Brief extraction with LLM
- Survey generation using skills
- Comprehensive validation (39+ rules)
- Survey rendering

We'll **wrap** these scripts with a FastAPI layer, not rewrite them.

## Setup Steps

### 1. Copy Core Scripts to Backend

```bash
# From SurveyPlatform root
cp ../Basics/extract_brief.py backend/core/
cp ../Basics/generate_survey.py backend/core/
cp ../Basics/validate_survey.py backend/core/
cp ../Basics/render_survey.py backend/core/
```

### 2. Copy Skills Directory

```bash
cp -r ../Basics/Skills/* skills/
```

### 3. Install Dependencies

The scripts use:
- `langchain` - LLM orchestration
- `pydantic` - Data validation
- `python-dotenv` - Environment variables
- `openai` - LLM provider
- `pyyaml` - Skills metadata parsing

```bash
cd backend
pip install fastapi uvicorn langchain langchain-openai pydantic python-dotenv pyyaml
```

### 4. Environment Variables

Create `backend/.env`:
```bash
OPENAI_API_KEY=your_key_here
LANGCHAIN_API_KEY=your_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=SurveyPlatform
```

## API Wrapper Pattern

### Example: Extract Brief Endpoint

```python
# backend/api/main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sys
sys.path.append('../core')

from extract_brief import extract_brief_from_text  # Import existing function

app = FastAPI()

class BriefRequest(BaseModel):
    brief_text: str

@app.post("/api/extract-brief")
async def extract_brief(request: BriefRequest):
    try:
        result = extract_brief_from_text(request.brief_text)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Data Flow

```
1. Frontend sends brief text
   ↓
2. POST /api/extract-brief
   ↓
3. extract_brief.py runs LLM call
   ↓
4. Returns structured JSON
   ↓
5. Frontend displays in form fields
   ↓
6. User refines, clicks Generate
   ↓
7. POST /api/generate-survey
   ↓
8. generate_survey.py creates survey
   ↓
9. validate_survey.py checks rules
   ↓
10. Survey JSON returned to frontend
```

## File Structure in Backend

```
backend/
├── api/
│   ├── main.py              # FastAPI app
│   ├── routes/
│   │   ├── brief.py         # Brief extraction endpoints
│   │   ├── survey.py        # Survey generation endpoints
│   │   └── project.py       # Project CRUD endpoints
│   └── models.py            # Pydantic request/response models
├── core/                     # Copied from Basics
│   ├── extract_brief.py
│   ├── generate_survey.py
│   ├── validate_survey.py
│   └── render_survey.py
├── storage/                  # JSON file storage (Phase 0)
│   └── projects/
└── requirements.txt
```

## Key Modifications Needed

### 1. Skills Updates (Phase 1b)
Add to each skill .md file:
```yaml
questions:
  - id: q1
    priority: required        # NEW
    priority_rank: 1          # NEW
    estimated_seconds: 15     # NEW
```

### 2. API Response Format
Wrap all responses in standard format:
```json
{
  "success": true,
  "data": { ... },
  "error": null
}
```

### 3. Error Handling
Frontend needs clear error messages:
```python
try:
    result = generate_survey(brief)
except ValidationError as e:
    return {
        "success": false, 
        "error": {
            "type": "validation",
            "issues": e.errors()
        }
    }
```

## Testing Integration

Test each endpoint works:

```bash
# Start backend
cd backend
python api/main.py

# Test in another terminal
curl -X POST http://localhost:8000/api/extract-brief \
  -H "Content-Type: application/json" \
  -d '{"brief_text": "We need to test pricing..."}'
```

## Next Steps

1. Create `backend/api/main.py` with FastAPI setup
2. Create route handlers for each endpoint
3. Test extract → generate flow end-to-end
4. Add project storage (JSON files initially)
5. Build frontend API client to consume endpoints
