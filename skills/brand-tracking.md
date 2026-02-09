---
name: brand-tracking
description: |
  Measures brand health metrics (awareness, consideration, preference, usage) consistently over time to track performance trends and marketing impact. Use when you need ongoing brand performance monitoring with quarterly, monthly, or annual measurement cycles. Also use when a study includes brand health measurement as a secondary objective alongside concept testing, segmentation, or other methodologies. Requires strict methodological discipline - questionnaire wording, competitive set, and scales must remain identical across waves to preserve trend comparability. Not suitable for one-time exploratory brand research or campaign-specific creative testing.
category: brand_strategy
foundational: false
primary_use_case: Monitor brand health trends over time to diagnose performance changes and measure marketing effectiveness
secondary_applications:
  - Brand health measurement module within larger studies (concept tests, segmentation, etc.)
  - Early warning detection of brand decline or competitive threats
  - ROI measurement for sustained marketing investments
  - Brand portfolio performance comparison across time periods
  - Market share movement correlation with brand funnel metrics
commonly_combined_with:
  - concept-test
  - brand-positioning
  - campaign-effectiveness-roi
  - ad-testing
  - segmentation
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - performance_tracking
  - decline_diagnosis
decision_stages:
  - measure
  - optimize
study_types:
  - brand_health_tracking
  - competitive_intelligence
not_suitable_for:
  - Campaign-specific message testing (use message-test or ad-testing)
  - Exploratory brand research or new brand development
  - Studies requiring frequent questionnaire changes or flexibility
---


# Brand Tracking

## Overview
Brand tracking measures brand health consistently over time. It tracks movement in awareness, consideration, preference, usage, and brand perceptions to diagnose performance, detect early warning signals, and evaluate the impact of marketing activity.

This skill applies in two contexts:
1. **Standalone tracker**: A dedicated tracking study run on a regular cadence
2. **Brand health module**: A brand tracking section within a larger study (e.g., combined with concept testing or segmentation)

In both cases, the same funnel logic, piping rules, and measurement standards apply.

## Core Principles

- **Wave-over-wave consistency:** Questions, wording, scales, and ordering must remain identical across waves.
- **Stable competitive set:** Comparisons are only meaningful if the brand list is controlled.
- **Funnel logic with progressive piping:** Metrics must follow the natural consumer decision journey, with each stage filtering to the next.
- **Trend sensitivity:** The system must detect small but meaningful changes over time.
- **Governance over flexibility:** Avoid changes that break trend lines.

---

## Competitive Set Definition

### Brand List Rules
- Include the **client brand + 4-9 primary competitors** (5-10 total)
- Use brands relevant to the specific market (e.g., NZ-specific brands for NZ studies)
- Maintain the same list and order across waves
- Add new brands only at planned breakpoints and flag as "new" in reporting
- Randomize brand order within questions to prevent order bias

---

## Brand Funnel Design

### Funnel Structure and Piping

The brand funnel MUST be measured in this order, with **progressive piping** between stages.
Each stage filters the brand list for the next stage, reducing respondent burden and
producing cleaner data.

```
Unaided Awareness (open-ended — no brand list shown)
    ↓
Aided Awareness (full competitive set — "Which have you heard of?")
    ↓ PIPE: only brands selected in aided awareness
Familiarity (optional — "How familiar are you?")
    ↓ PIPE: only brands selected in aided awareness
Consideration ("Which would you consider?" — only brands heard of)
    ↓ PIPE: only brands selected in consideration
Ever Purchased ("Which have you ever purchased?" — only brands considered)
    ↓ PIPE: only brands selected in ever purchased
Current Usage ("Which do you currently use?" — only brands ever purchased)
    ↓ PIPE: only brands selected in current usage
Most Often Used ("Which ONE do you use most often?" — only brands currently used)
```

**CRITICAL**: Do NOT show the full brand list at every funnel stage. A respondent cannot
consider a brand they haven't heard of, cannot have purchased a brand they wouldn't consider,
and cannot currently use a brand they haven't purchased. Progressive piping enforces this
logic and reduces survey fatigue.

**Implementation**: Use the `piping` field on each question to reference the source question.
In options, write `"[PIPE IN: brands selected at <question_id>]"`. Always include
`"None of these"` as an escape option on piped questions.

---

## Question Specifications

### 1. Unaided Awareness (Top-of-Mind)

```json
{
  "question_id": "MS2_Q1",
  "question_text": "When you think about [CATEGORY], which brands come to mind? Please list all brands you can think of.",
  "question_type": "open_ended",
  "options": [],
  "rows": null,
  "columns": null,
  "required": true,
  "notes": "Unaided awareness. Code to brand list during analysis. No brand prompts."
}
```

### 2. Aided Awareness

```json
{
  "question_id": "MS2_Q2",
  "question_text": "Which of the following [CATEGORY] brands have you heard of, even if only by name? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": [
    "ClientBrand",
    "Competitor1",
    "Competitor2",
    "...",
    "None of these"
  ],
  "rows": null,
  "columns": null,
  "required": true,
  "notes": "Aided awareness. Randomize brand order. Full competitive set."
}
```

### 3. Familiarity (Optional but Recommended)

```json
{
  "question_id": "MS2_Q3",
  "question_text": "How familiar are you with each of the following brands?",
  "question_type": "matrix",
  "options": [],
  "rows": "[PIPE IN: brands selected at MS2_Q2]",
  "columns": [
    "Very familiar",
    "Somewhat familiar",
    "Heard of only",
    "Not at all familiar"
  ],
  "piping": "Pipe in brands selected at MS2_Q2",
  "required": true,
  "notes": "Only show brands the respondent has heard of. Randomize row order."
}
```

### 4. Consideration

```json
{
  "question_id": "MS2_Q4",
  "question_text": "Which of the following brands would you consider purchasing the next time you buy [CATEGORY]? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": "[PIPE IN: brands selected at MS2_Q2, plus 'None of these']",
  "piping": "Pipe in brands selected at MS2_Q2",
  "required": true,
  "notes": "Only show brands respondent is aware of. Randomize order."
}
```

### 5. Ever Purchased

```json
{
  "question_id": "MS2_Q5",
  "question_text": "Which of the following brands have you ever purchased? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": "[PIPE IN: brands selected at MS2_Q4, plus 'None of these']",
  "piping": "Pipe in brands selected at MS2_Q4 (consideration set)",
  "required": true,
  "notes": "Only show brands in consideration set."
}
```

### 6. Current Usage

```json
{
  "question_id": "MS2_Q6",
  "question_text": "Which of the following brands have you purchased in the past 3 months? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": "[PIPE IN: brands selected at MS2_Q5, plus 'None of these']",
  "piping": "Pipe in brands selected at MS2_Q5 (ever purchased)",
  "required": true,
  "notes": "Only show brands ever purchased. Timeframe should match category purchase cycle."
}
```

### 7. Most Often Used

```json
{
  "question_id": "MS2_Q7",
  "question_text": "Which ONE brand do you purchase most often?",
  "question_type": "single_choice",
  "options": "[PIPE IN: brands selected at MS2_Q6, plus 'I don't have a brand I purchase most often']",
  "piping": "Pipe in brands selected at MS2_Q6 (current usage)",
  "required": true,
  "notes": "Single select. Only show currently used brands."
}
```

---

## Brand Attribute / Image Measurement

### Matrix Design Rules

Brand image/attribute ratings use a matrix grid. The matrix structure MUST follow these rules:

**Rows** = Brands (piped from aided awareness)
**Columns** = A UNIFORM rating scale

CORRECT example:
```json
{
  "question_id": "MS3_Q1",
  "question_text": "Thinking about [Brand], how well do each of the following statements describe this brand?",
  "question_type": "matrix",
  "options": [],
  "rows": [
    "High quality",
    "Good value for money",
    "Innovative",
    "Trustworthy",
    "Premium/luxury",
    "For people like me"
  ],
  "columns": [
    "Describes very well",
    "Describes somewhat",
    "Does not describe",
    "Don't know"
  ],
  "piping": "Show this matrix once per brand piped from MS2_Q2. Randomize attribute row order.",
  "notes": "Brand image battery. One matrix per brand (piped from aided awareness). Max 12 attributes per matrix. Always include 'Don't know' column. Randomize row order."
}
```

**NEVER** combine brand names with scale points in column headers:
```
WRONG: columns = ["Brand A - Describes very well", "Brand A - Describes somewhat",
                   "Brand B - Describes very well", "Brand B - Describes somewhat"]
```
This creates an unusable grid (10 attributes × 12 brand-scale columns = 120 cells).

### Attribute Selection Rules
- Use 8-12 attributes maximum
- Attributes must be stable over time — avoid campaign-specific language
- Include both category-generic and brand-differentiating attributes
- If the brief specifies attributes or references a prior wave, use those exactly
- If attributes are TBC, note in the question's `notes` field: "Attributes TBC by client —
  must match prior wave baseline if tracking study"

### "Don't Know" Column
ALWAYS include a "Don't know" column on brand attribute matrices. Respondents cannot
meaningfully rate brands they don't know well enough. Forcing a response produces
noise, not data.

---

## NPS (Net Promoter Score)

When the client brand is included in the study and the brief mentions NPS, loyalty,
or recommendation metrics, include NPS for the client brand only.

### NPS Question
```json
{
  "question_id": "MS3_Q2",
  "question_text": "On a scale of 0 to 10, how likely are you to recommend [CLIENT BRAND] to a friend or colleague?",
  "question_type": "scale",
  "options": [
    "0 - Not at all likely",
    "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "10 - Extremely likely"
  ],
  "display_logic": "Show only if respondent selected [CLIENT BRAND] in MS2_Q6 (current usage)",
  "required": true,
  "notes": "NPS for client brand purchasers only. Detractors: 0-6, Passives: 7-8, Promoters: 9-10."
}
```

### NPS Verbatim Follow-Up
```json
{
  "question_id": "MS3_Q3",
  "question_text": "You gave [CLIENT BRAND] a score of [PIPE SCORE]. What is the main reason for your score?",
  "question_type": "open_ended",
  "options": [],
  "piping": "Pipe score from MS3_Q2",
  "display_logic": "Show only if MS3_Q2 was answered",
  "required": false,
  "notes": "NPS verbatim follow-up. Pipe in the respondent's score."
}
```

---

## Scale Design Rules

Tracking studies require absolute consistency in scales.

- Use the same scale length every wave
- Use the same labels every wave
- Use the same polarity every wave
- Do not use numeric scales for familiarity — use labeled categories
- Do not switch from 5-point to 7-point scales mid-tracking

---

## Section Ordering

When brand tracking is part of a larger study (e.g., combined with concept testing):

1. **Place brand tracking BEFORE concept exposure.** Concept exposure contaminates
   unaided awareness and organic brand perceptions. Brand metrics must reflect the
   respondent's pre-exposure state.

2. Typical ordering for a combined study:
   ```
   Screener → Category Usage → Brand Funnel (awareness → usage) →
   Brand Image → [Segmentation battery if applicable] →
   Concept Testing → Comparison → Pricing → Demographics
   ```

3. If NPS is included, place it within the brand metrics section (after brand image,
   before concept exposure).

---

## FLOW Requirements

The FLOW section must include routing rules for:

- **Piping chains**: Each funnel question pipes brands from the prior stage
- **NPS conditional display**: Only show NPS to client brand current users
- **Brand image conditional display**: Only show attribute ratings for brands the respondent
  has heard of (piped from aided awareness)
- **"None of these" handling**: If respondent selects "None of these" at consideration,
  skip to the next section (no usage questions to ask)

Example routing rules:
```json
{
  "rule_id": "R_BRAND_PIPE_1",
  "condition": "MS2_Q4 (consideration) shows only brands selected in MS2_Q2 (aided awareness)",
  "action": "Pipe brand list from MS2_Q2 to MS2_Q4. Include 'None of these' escape."
},
{
  "rule_id": "R_BRAND_PIPE_2",
  "condition": "MS2_Q5 (ever purchased) shows only brands selected in MS2_Q4 (consideration)",
  "action": "Pipe brand list from MS2_Q4 to MS2_Q5. Include 'None of these' escape."
},
{
  "rule_id": "R_BRAND_SKIP",
  "condition": "MS2_Q4 = 'None of these'",
  "action": "Skip MS2_Q5, MS2_Q6, MS2_Q7. Proceed to brand image section."
},
{
  "rule_id": "R_NPS_DISPLAY",
  "condition": "Respondent selected [CLIENT BRAND] in MS2_Q6 (current usage)",
  "action": "Show MS3_Q2 (NPS) and MS3_Q3 (NPS verbatim)"
}
```

---

## Common Mistakes to Avoid

❌ **No piping between funnel stages** — showing the full brand list at every stage inflates
   consideration/usage numbers and wastes respondent time
❌ **Combining brand × scale in matrix columns** — creates an unusable grid (e.g., "Brand A -
   Describes very well", "Brand A - Describes somewhat", "Brand B - Describes very well"...)
❌ **Omitting "Don't know" on brand ratings** — forces respondents to rate brands they don't
   know, producing noise
❌ **Placing brand metrics after concept exposure** — concept exposure contaminates unaided
   awareness and organic perceptions
❌ **Changing question wording between waves** — breaks trend comparability permanently
❌ **Combining usage stages into one question** — "ever used," "currently use," and "most often"
   must be separate questions
❌ **Overloading the tracker** — keep the core tracker lean; rotate deep dives as separate studies
❌ **Ignoring sample consistency** — changing sampling sources or quotas without adjustment
   makes sample shifts look like brand movement

---

## Analysis & Output Requirements

### Core Metrics to Report
- Unaided awareness (%)
- Aided awareness (%)
- Familiarity distribution (if measured)
- Consideration (%)
- Ever purchased (%)
- Current usage (%)
- Most-often-used (%)
- NPS score and distribution (if measured)
- Brand image attribute scores per brand

Report alongside:
- Wave-over-wave change
- Year-over-year change (when applicable)
- Statistical significance flags

### Deliverables
- Awareness funnel visualization (unaided → aided → consideration → usage)
- Brand image perceptual map (correspondence analysis or MDS)
- Competitive set analysis (share of consideration, share of usage)
- NPS score with Promoter/Passive/Detractor breakdown (if measured)

---

## Quality Checklist

- [ ] Questionnaire wording is locked and version-controlled
- [ ] Competitive set is stable and documented
- [ ] Funnel metrics follow awareness → usage order with progressive piping
- [ ] Piping chains are defined in FLOW routing rules
- [ ] Brand image matrix uses uniform columns (scale only, not brand×scale)
- [ ] "Don't know" included on all brand attribute ratings
- [ ] NPS included for client brand current users (if brief requires)
- [ ] Brand tracking section placed BEFORE concept/stimulus exposure
- [ ] Scales and labels are identical across waves
- [ ] Sampling and weighting are consistent

---

## Output Requirements

Survey MUST include:
- Full brand funnel: unaided awareness → aided awareness → consideration → ever purchased → current usage → most often used
- Progressive piping between all funnel stages (defined in FLOW routing rules)
- Brand image matrix with uniform scale columns and "Don't know" column
- NPS with verbatim follow-up for client brand purchasers (if brief requires loyalty/recommendation metrics)
- Brand tracking section positioned BEFORE any concept/stimulus exposure
- "None of these" escape option on all piped brand questions
- Randomization of brand order in all brand list questions