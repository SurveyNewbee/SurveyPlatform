# Backend API

FastAPI wrapper around the existing Python survey generation scripts.

## Setup

1. **Create virtual environment:**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Copy core scripts from Basics:**
   ```bash
   # From backend/ directory
   mkdir -p core
   cp ../../Basics/extract_brief.py core/
   cp ../../Basics/generate_survey.py core/
   cp ../../Basics/validate_survey.py core/
   cp ../../Basics/render_survey.py core/
   ```

## Run Development Server

```bash
python api/main.py
```

Or with uvicorn directly:
```bash
uvicorn api.main:app --reload --port 8000
```

API will be available at: http://localhost:8000

## API Documentation

Once running, view auto-generated docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/
│   ├── main.py          # FastAPI app entry point
│   ├── routes/          # API endpoints
│   │   ├── brief.py
│   │   ├── survey.py
│   │   └── project.py
│   └── models.py        # Pydantic models
├── core/                 # Copied from Basics
│   ├── extract_brief.py
│   ├── generate_survey.py
│   ├── validate_survey.py
│   └── render_survey.py
├── storage/              # File-based storage (Phase 0)
│   └── projects/
├── .env                  # Environment variables
└── requirements.txt
```

## Key Endpoints

### Brief Management
- `POST /api/extract-brief` - Extract structured data from raw brief text
- `GET /api/skills` - List available survey methodologies

### Survey Generation
- `POST /api/generate-survey` - Generate survey from brief
- `POST /api/validate-survey` - Run validators on survey JSON

### Project Management
- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `POST /api/projects` - Create new project
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Preview
- `POST /api/render-preview` - Render survey for respondent preview

## Next Steps

1. Create `api/main.py` with FastAPI setup
2. Implement route handlers
3. Test integration with existing scripts
4. Add project storage layer
