# MVP Build Plan — AI Survey Platform

**Source:** Original plan from `Basics/MVP Build Plan`  
**Date:** February 9, 2026  
**Purpose:** Partnership demo build

This is a complete end-to-end implementation plan for building an AI-powered survey platform.

## Quick Reference

The complete detailed specification is in the original `../Basics/MPV Build Plan` file (2243 lines).

## Revised Architecture (Integrating Existing Scripts)

### What We're Building On

We have substantial working Python infrastructure in `Basics/`:
- `extract_brief.py` (764 lines) - LLM-powered brief extraction
- `generate_survey.py` (761 lines) - Survey generation with skills
- `validate_survey.py` (4486 lines) - Comprehensive validation rules
- `render_survey.py` (1282 lines) - Survey rendering
- `Skills/` directory - Methodology-specific generation rules

### Integration Strategy

```
Frontend (React)
    ↓ REST API
Backend (FastAPI wrapper)
    ↓ Python imports & subprocess
Existing Scripts (from Basics)
    ↓ Uses
Skills (copied to this project)
```

## Revised Timeline

| Phase | Description | Days | Notes |
|-------|-------------|------|-------|
| **API Layer** | FastAPI wrapper for existing scripts | 3-4 | NEW |
| **Phase 0** | Navigation shell + Dashboard | 2-3 | Frontend |
| **Phase 1a** | Setup page (wire to scripts) | 4-5 | Faster with existing backend |
| **Phase 1b** | Update Skills with LOI tags | 5-6 | Just add metadata |
| **Phase 2** | LOI Slider | 9-10 | Frontend |
| **Phase 3** | Editor | 7-8 | Frontend |
| **Phase 4** | Preview + Comments + AI Edit | 10-12 | Frontend + 2 new API endpoints |
| **Phase 5** | Reporting | 12-14 | Frontend + seed data |
| **Phase 6** | Launch | 4-5 | Frontend (mostly stubbed) |
| **Total** | | **66-76** | |

## Implementation Sequence

### Step 1: Backend API Layer (Week 1)
Create `backend/api/main.py` with FastAPI endpoints:
- `POST /api/extract-brief` → calls `extract_brief.py`
- `POST /api/generate-survey` → calls `generate_survey.py` → `validate_survey.py`
- `GET /api/skills` → returns skills metadata
- `POST /api/render-preview` → calls `render_survey.py`

### Step 2: Frontend Foundation (Week 1-2)
- Set up React + TypeScript + TailwindCSS
- Create routing structure
- Build global navigation header
- Build Dashboard with project cards

### Step 3: Core Flow (Week 2-4)
- Setup page (paste brief → extract → refine → generate)
- Wire to backend API
- Display generated survey (read-only first)

### Step 4: LOI + Editor (Week 4-6)
- Update Skills with priority tags
- Build LOI slider
- Build survey editor

### Step 5: Preview + Reporting (Week 7-10)
- Build preview mode with comment system
- Build AI edit loop
- Build reporting UI with charts
- Create seed datasets

### Step 6: Launch (Week 10-11)
- Build launch wizard
- Build status page (stubbed)

## Key Design Decisions

1. **Keep Basics/ intact** - All new work in SurveyPlatform/
2. **Import, don't rewrite** - Backend imports existing Python modules
3. **Skills copied** - Copy Skills/ to this project and enhance with LOI metadata
4. **API-first** - Backend exposes REST API, frontend consumes it
5. **Demo-focused** - Some features stubbed (launch, live fielding)

## Next Actions

- [ ] Copy necessary files from Basics to backend/core
- [ ] Set up Python virtual environment
- [ ] Create FastAPI skeleton
- [ ] Initialize React project
- [ ] Test end-to-end: brief → survey generation
