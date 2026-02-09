# Survey Platform MVP

AI-powered ad hoc survey platform for partnership demo.

**Full end-to-end flow:** Brief → Generate → Edit → Preview → Launch → Reporting

## Project Structure

```
SurveyPlatform/
├── backend/           # FastAPI server + Python survey engine
│   ├── api/          # REST API endpoints
│   ├── core/         # Integration with Basics scripts
│   └── requirements.txt
├── frontend/          # React application
│   ├── src/
│   │   ├── pages/    # Dashboard, Setup, Editor, Preview, Report, Launch
│   │   ├── components/
│   │   └── api/      # API client
│   └── package.json
├── skills/            # Survey methodology skills (copied from Basics)
├── docs/              # Build plan and specifications
└── README.md
```

## Quick Start

### Backend Setup
```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python api/main.py
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

## Architecture

The platform leverages existing proven Python scripts from `Basics/`:
- `extract_brief.py` - Brief extraction (764 lines)
- `generate_survey.py` - Survey generation (761 lines)
- `validate_survey.py` - Validation engine (4486 lines!)
- `render_survey.py` - Survey rendering (1282 lines)

The backend API wraps these scripts, and the frontend provides the UI.

## Development Phases

See [docs/BUILD_PLAN.md](docs/BUILD_PLAN.md) for detailed implementation plan:

- **Phase 0:** Foundation (2-3 days) - Navigation + Dashboard
- **Phase 1a:** Setup Page (4-5 days) - Brief entry + extraction
- **Phase 1b:** Skills Update (5-6 days) - Add LOI priority tags
- **Phase 2:** LOI Slider (9-10 days) - Dynamic survey length control
- **Phase 3:** Editor (7-8 days) - Survey editing interface
- **Phase 4:** Preview (10-12 days) - Test + comment + AI edit loop
- **Phase 5:** Reporting (12-14 days) - Charts + insights + export
- **Phase 6:** Launch (4-5 days) - Launch wizard + status page

**Total estimate:** 66-76 working days

## Key Features

- ✨ AI-powered brief extraction and survey generation
- 📏 Dynamic LOI slider (adjust survey length after generation)
- ✏️ Full survey editor with drag-and-drop
- 👁️ Respondent preview with commenting
- 🔄 AI-powered targeted edits from comments
- 📊 Professional reporting with specialty charts
- 🚀 Launch configuration (stubbed for demo)

## Tech Stack

- **Backend:** Python 3.11+, FastAPI, LangChain, Pydantic
- **Frontend:** React 18+, TypeScript, TailwindCSS
- **LLM:** OpenAI GPT-4 (via LangChain)
- **Observability:** LangSmith tracing

## Documentation

- [BUILD_PLAN.md](docs/BUILD_PLAN.md) - Complete implementation specification
- [API_SPEC.md](docs/API_SPEC.md) - Backend API documentation
- [INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md) - How to integrate with Basics scripts

## Status

🚧 **Project Setup Phase** - Building initial structure

Next steps: 
1. Set up backend API wrapper for Basics scripts
2. Initialize React frontend with routing
3. Begin Phase 0: Navigation + Dashboard
