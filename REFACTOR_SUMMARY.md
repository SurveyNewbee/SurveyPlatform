# Survey Platform Two-Agent Pipeline Refactor - Summary

## Overview
Successfully refactored the SurveyPlatform to implement a two-agent pipeline with human review step, replacing the single-pass architecture with skills-based generation.

**Date**: February 10, 2026  
**Status**: ✅ Complete

---

## Architecture Changes

### Before (Single-Pass)
```
User Brief → Agent 1 (Brief Extraction) → Agent 2 (Survey Design with Skills) → Survey
                    ↓
              Selects Skills
```

### After (Two-Agent with Human Review)
```
User Brief → Agent 1 (Brief Extraction + Blueprint Design) → Human Review → Agent 2 (Survey Execution from Blueprint) → Survey
                            ↓
                   Survey Blueprint
```

---

## Model Configuration

| Agent | Old Model | New Model | Purpose |
|-------|-----------|-----------|---------|
| Agent 1 | `claude-sonnet-4-20250514` | `claude-opus-4-6` | Strategic planning - brief interpretation, methodology classification, survey architecture design |
| Agent 2 | `claude-opus-4-5-20251101` | `claude-sonnet-4-5-20250929` | Execution - question writing, flow logic, implementation-ready JSON |

---

## Files Modified

### 1. `backend/core/extract_brief.py` (Agent 1)

#### Removed:
- ❌ `load_skills_metadata()` function
- ❌ `add_foundational_and_dependencies()` function
- ❌ `FOUNDATIONAL_SKILLS` constant
- ❌ `self.available_skills` loading in `__init__`
- ❌ `_format_skills_for_prompt()` method
- ❌ `skills` field from `BriefExtraction` model
- ❌ Skill validation and post-processing logic in `extract()` method
- ❌ `{available_skills}` template variable from prompt

#### Added:
- ✅ `BlueprintSection` model - Defines survey sections with purpose, question types, estimates
- ✅ `ExperimentalDesign` model - Captures experimental design configuration
- ✅ `PipingChain` model - Documents data flow and piping logic
- ✅ `SurveyBlueprint` model - Complete blueprint with LOI assessment
- ✅ `survey_blueprint` field in `BriefExtraction` model (replaces `skills`)
- ✅ Blueprint rendering in `format_markdown()` function
- ✅ `survey_blueprint` in `get_survey_template_vars()` return value

#### Changed:
- 🔄 Default model: `claude-sonnet-4-20250514` → `claude-opus-4-6`
- 🔄 Class docstring: "with skills integration" → "with blueprint generation (Agent 1)"
- 🔄 `extract()` method now reports blueprint stats instead of skills
- 🔄 Removed `yaml` import (no longer parsing skill .md files)

---

### 2. `backend/core/generate_survey.py` (Agent 2)

#### Removed:
- ❌ `skills_dir` parameter from `__init__`
- ❌ `self.skills_dir` instance variable
- ❌ `_load_skill_content()` method (entire skills loading infrastructure)
- ❌ `skills_content` variable in `_prepare_vars()`
- ❌ Skill loading/formatting logic

#### Added:
- ✅ `survey_blueprint` formatted as JSON string in `_prepare_vars()`
- ✅ `survey_blueprint` added to template variables dict

#### Changed:
- 🔄 Default model: `claude-opus-4-5-20251101` → `claude-sonnet-4-5-20250929`
- 🔄 Class docstring: "with skills integration" → "that executes approved blueprint (Agent 2)"
- 🔄 `_load_prompt()` simplified - no longer configures dynamic skill loading
- 🔄 Template variable `skills_content` → `survey_blueprint`

---

### 3. `backend/api/models.py` (Data Models)

#### Added:
- ✅ `BlueprintSection` - Survey section in blueprint
- ✅ `ExperimentalDesign` - Experimental design configuration
- ✅ `PipingChain` - Piping chain definition
- ✅ `SurveyBlueprint` - Complete blueprint structure with LOI assessment

#### Changed:
- 🔄 `GenerateSurveyRequest`:
  - Removed: `selected_skills: List[str]`
  - Docstring updated: Now expects `brief_data` with embedded `survey_blueprint`
  - Added comment: "selected_skills field removed - blueprint replaces skills"

---

### 4. `backend/api/routes/brief.py` (Brief Extraction Route)

#### Changed:
- 🔄 Import statement: Removed `load_skills_metadata` import
- 🔄 `/extract-brief` endpoint:
  - Response field: `identified_skills` → `survey_blueprint`
  - Returns blueprint from Agent 1 instead of selected skills list
- 🔄 `/skills` endpoint:
  - Marked as **DEPRECATED**
  - Returns empty list with deprecation message
  - Kept for backward compatibility only

---

### 5. `backend/api/routes/survey.py` (Survey Generation Route)

#### Changed:
- 🔄 `/generate-survey` endpoint:
  - Removed `skills_dir` path resolution
  - Removed frontend-to-backend data transformation (objectives → objective, topics → key_dimensions)
  - Now directly passes `request.brief_data` to generator (contains full Agent 1 output)
  - Removed `skills` field from `brief_for_generator`
  - Generator instantiation: `SurveyGenerator(skills_dir=skills_dir)` → `SurveyGenerator()`
  - Updated docstring to reflect blueprint-based workflow

---

## What Was NOT Changed

✅ **Prompt Templates**
- `prompt_template.txt` - Not modified (as per user instruction)
- `survey_prompt_template.txt` - Not modified (as per user instruction)

✅ **Survey Output Schema**
- Agent 2 JSON structure unchanged
- Question format unchanged
- All existing fields preserved (STUDY_METADATA, SAMPLE_REQUIREMENTS, SCREENER, etc.)

✅ **Skill Files**
- `.md` files in `skills/` directory remain intact
- Not deleted (may be repurposed as study-type configs later)

✅ **Downstream Processing**
- Survey validation unchanged
- Rendering/export unchanged
- LOI calculator unchanged
- Frontend consumption unchanged (except for blueprint review step)

---

## Template Variable Changes

### Agent 1 (Brief Extraction)
| Variable | Before | After |
|----------|--------|-------|
| `{brief}` | ✅ Injected | ✅ Injected |
| `{available_skills}` | ✅ Injected | ❌ Removed |
| `{format_instructions}` | ✅ Injected | ✅ Injected |

### Agent 2 (Survey Design)
| Variable | Before | After |
|----------|--------|-------|
| `{skills_content}` | ✅ Injected | ❌ Removed |
| `{survey_blueprint}` | ❌ N/A | ✅ Injected |
| All other variables | ✅ Injected | ✅ Injected |

---

## New Workflow

### 1. Brief Submission
```http
POST /api/extract-brief
{
  "brief_text": "..."
}
```

### 2. Agent 1 Response (Includes Blueprint)
```json
{
  "success": true,
  "data": {
    "objective": "...",
    "target_audience": "...",
    "topics": [...],
    "survey_blueprint": {
      "sections": [
        {
          "section_id": "awareness",
          "section_title": "Brand Awareness",
          "purpose": "Measure aided and unaided awareness",
          "question_types": ["single_choice", "multiple_choice"],
          "estimated_question_count": 4,
          "estimated_minutes": 2.5,
          "key_constructs": ["top_of_mind", "aided_recall"],
          "notes": null
        }
      ],
      "experimental_design": null,
      "piping_chains": [
        {
          "chain_name": "brand_funnel",
          "description": "Pipe aware brands to consideration question"
        }
      ],
      "estimated_total_loi_minutes": 12.5,
      "loi_assessment": "within_target"
    },
    ...
  }
}
```

### 3. Human Review
Frontend displays:
- Extracted parameters
- Blueprint (sections, LOI, experimental design)
- Approve/Reject buttons

### 4. Survey Generation (After Approval)
```http
POST /api/generate-survey
{
  "brief_data": {
    // Full Agent 1 output (including survey_blueprint)
  }
}
```

### 5. Agent 2 Response (Complete Survey)
Returns full survey JSON with questions, flow logic, etc.

---

## Blueprint Schema

```typescript
interface SurveyBlueprint {
  sections: BlueprintSection[];
  experimental_design: ExperimentalDesign | null;
  piping_chains: PipingChain[];
  estimated_total_loi_minutes: number;
  loi_assessment: "within_target" | "at_risk" | "over_target" | "no_target_specified";
}

interface BlueprintSection {
  section_id: string;
  section_title: string;
  purpose: string;
  question_types: string[];
  estimated_question_count: number;
  estimated_minutes: number;
  key_constructs: string[];
  notes: string | null;
}

interface ExperimentalDesign {
  design_type: string;
  rotation_scheme: string | null;
  cells: number | null;
  stimulus_evaluation_battery: string[];
}

interface PipingChain {
  chain_name: string;
  description: string;
}
```

---

## Testing Recommendations

### 1. Concept Test
- Should produce blueprint with:
  - `experimental_design` (sequential monadic)
  - Multiple stimulus subsections
  - Comparison/ranking section
  - `stimulus_evaluation_battery` in experimental_design

### 2. Brand Tracking
- Should produce blueprint with:
  - No `experimental_design`
  - Awareness → consideration → usage funnel
  - `piping_chains` array with brand funnel logic

### 3. Pricing Study
- Should produce blueprint with:
  - Price sensitivity constructs (Van Westendorp)
  - Sequential question flow
  - No experimental design

### 4. Descriptive Study
- Should produce blueprint with:
  - Simple section structure
  - No experimental design
  - No piping chains

### 5. Rejection Flow
- User rejects Agent 1 output
- Returns to brief input
- Agent 2 is never called

---

## Benefits of New Architecture

1. **Strategic Planning by Expert Model**
   - Opus 4.6 handles complex brief interpretation
   - Better methodology classification
   - More thoughtful survey architecture

2. **Human in the Loop**
   - User reviews and approves blueprint before execution
   - Catches design issues early
   - Ensures alignment with research objectives

3. **Cost Optimization**
   - Expensive model (Opus) only for planning
   - Fast, cheaper model (Sonnet) for execution
   - Better cost/quality tradeoff

4. **Better Traceability**
   - Blueprint explicitly documents design decisions
   - Clear separation of strategy vs execution
   - Easier to debug and iterate

5. **Simpler System**
   - Removed complex skill loading/injection logic
   - No more skill selection or dependency resolution
   - Fewer moving parts, easier to maintain

---

## Backward Compatibility

- `/skills` endpoint returns empty list (deprecated but not breaking)
- Frontend must be updated to:
  - Display blueprint for review
  - Send approved brief_data (not selected_skills) to generate-survey
- Old integrations that call `/generate-survey` with `selected_skills` will need updates

---

## Next Steps (Future Enhancements)

1. **Blueprint Editing**
   - Allow user to modify blueprint before approval
   - Add/remove sections
   - Adjust LOI estimates

2. **Blueprint Templates**
   - Predefined blueprints for common study types
   - User can start from template and edit

3. **Cost Estimation**
   - Show estimated cost based on sample size and LOI
   - Model costs (Opus vs Sonnet)

4. **Blueprint History**
   - Save approved blueprints for reuse
   - Learn from past successes

---

## Completion Checklist

- [x] Update Agent 1 (extract_brief.py) - Model, schema, remove skills
- [x] Update Agent 2 (generate_survey.py) - Model, template variables, remove skills
- [x] Add blueprint models to api/models.py
- [x] Update /extract-brief endpoint to return blueprint
- [x] Update /generate-survey endpoint to accept approved brief
- [x] Deprecate /skills endpoint
- [x] Test for syntax/import errors
- [x] Create refactor summary documentation

---

## Files Changed Summary

| File | Lines Changed | Key Changes |
|------|---------------|-------------|
| `extract_brief.py` | ~150 | Model change, blueprint schema, removed skills |
| `generate_survey.py` | ~70 | Model change, blueprint variable, removed skills |
| `api/models.py` | ~30 | Added blueprint models, updated request model |
| `api/routes/brief.py` | ~20 | Return blueprint, deprecate skills endpoint |
| `api/routes/survey.py` | ~25 | Simplified to use approved brief directly |

**Total Lines Modified**: ~295

---

## Status: ✅ COMPLETE

All changes successfully implemented. The SurveyPlatform now uses a two-agent pipeline with human review between brief extraction and survey generation. Skills infrastructure has been removed and replaced with an explicit survey blueprint that users can review and approve before proceeding to survey execution.
