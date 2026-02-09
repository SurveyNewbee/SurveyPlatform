---
name: screening
description: |
  Determines respondent eligibility through demographic, behavioral, and firmographic qualification questions to ensure surveys reach the right target audience. Use at the start of any survey requiring specific participant criteria (age, usage, purchase behavior, job role, etc.). Essential foundation for all survey research - typically combined with rating-scales and specific methodologies like concept-test or segmentation.
category: specialty
foundational: true
primary_use_case: Qualify survey respondents based on specific demographic, behavioral, or firmographic criteria to ensure data quality and target audience precision
secondary_applications:
  - Quota management across demographic segments
  - Panel quality control and validation
  - Market sizing through incidence rate measurement
  - Sample stratification for representative studies
commonly_combined_with:
  - rating-scales
  - demographics
  - concept-test
  - segmentation
requires: []
problem_frames_solved:
  - performance_tracking
  - opinion_measurement
decision_stages:
  - discover
  - define
  - design
  - validate
  - measure
  - optimize
study_types:
  - new_product_development
  - market_measurement
  - customer_satisfaction
  - usage_attitudes
  - user_experience
  - advertising_comms
  - brand_strategy
  - pricing_optimization
  - b2b_research
  - employee_research
  - opinion_polling
not_suitable_for:
  - Attitudinal or opinion questions (save for main survey)
  - Complex multi-part qualification logic (keep simple)
  - Studies where broad general population is needed without qualification
---


# Survey Screener Design

## Overview
Screeners determine respondent eligibility and ensure you're surveying the right target audience. Well-designed screeners balance precision (finding qualified respondents) with efficiency (not screening out too many).

## Core Principles

### 1. Use Categorical Options, Never Binary
❌ BAD: "Do you work in healthcare? Yes/No"
✓ GOOD: "Which industry do you work in? Healthcare / Finance / Technology / Retail / Government / Other"

**Why**: Binary questions reveal the "right answer" and encourage misrepresentation. Categorical options hide qualification criteria.

### 2. Include Both Qualifying AND Disqualifying Options
Every screener question should have:
- Options that qualify the respondent
- Options that disqualify the respondent  
- Neutral options (e.g., "Prefer not to say")

This prevents respondents from guessing the "right" answer.

### 3. Order Matters
- Start with **broad demographic** screeners (age, location)
- Move to **behavioral** screeners (usage, purchase)
- End with **attitudinal** screeners (if needed)
- Never screen on sensitive topics first (income, health)

## Question Type Guidelines

### Demographic Screeners
```json
{
  "question_id": "SCR_Q1",
  "question_text": "What is your age?",
  "question_type": "single_choice",
  "options": [
    "Under 18",
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65 or older",
    "Prefer not to say"
  ]
}
```

**Qualification logic**: Screen out "Under 18" and "Prefer not to say"

### Category Usage Screeners
```json
{
  "question_id": "SCR_Q2",
  "question_text": "How often do you purchase coffee from coffee shops or cafes?",
  "question_type": "single_choice",
  "options": [
    "Multiple times per week",
    "About once a week",
    "A few times a month",
    "Once a month or less",
    "Never",
    "Not sure"
  ]
}
```

**Qualification logic**: Qualify "Multiple times per week" through "A few times a month"; screen out "Once a month or less", "Never", "Not sure"

### Purchase Intent Screeners
```json
{
  "question_id": "SCR_Q3",
  "question_text": "When do you expect to purchase or lease your next vehicle?",
  "question_type": "single_choice",
  "options": [
    "Within the next 3 months",
    "In 4-6 months",
    "In 7-12 months",
    "In 1-2 years",
    "More than 2 years from now",
    "No plans to purchase",
    "Not sure"
  ]
}
```

**Qualification logic**: Qualify based on research timeframe (typically within 6-12 months)

### Industry/Employment Screeners
```json
{
  "question_id": "SCR_Q4",
  "question_text": "Which of the following best describes your current employment situation?",
  "question_type": "single_choice",
  "options": [
    "Employed full-time",
    "Employed part-time",
    "Self-employed/Freelance",
    "Unemployed and looking for work",
    "Unemployed and not looking for work",
    "Retired",
    "Student",
    "Prefer not to say"
  ]
}
```

### B2B Role Screeners
```json
{
  "question_id": "SCR_Q5",
  "question_text": "What is your role in technology purchasing decisions at your organization?",
  "question_type": "single_choice",
  "options": [
    "Final decision maker",
    "Significant influence on decisions",
    "Some influence on decisions",
    "Provide input but no decision authority",
    "No involvement in purchasing decisions",
    "Not sure"
  ]
}
```

**Qualification logic**: Qualify top 2-3 options depending on research needs

## Critical Rules

### ❌ Never Use Matrix Format for Screeners
Screeners must be simple single-choice questions. Matrix format is:
- Harder to answer quickly
- Increases dropout
- Makes routing logic more complex

### ❌ Never Ask Attitudinal Questions in Screener
Screener focuses ONLY on qualification criteria:
- Demographics (age, gender, location)
- Behavior (usage, purchase, role)
- Firmographics (company size, industry - for B2B)

Move attitudinal/opinion questions to main survey.

### ✓ Always Include "Prefer Not to Say" or "Not Sure"
Forcing respondents to answer sensitive questions increases:
- Dropout rates
- False responses
- Panel complaints

### ✓ Keep Screeners Short (3-7 Questions)
- More than 7 screener questions = higher dropout
- Only screen on criteria that truly matter for analysis
- Combine multiple criteria into single questions when possible

## Screen-Out Handling

### Termination Message
When respondents don't qualify, provide a professional termination message:

```
"Thank you for your interest in this study. Based on your responses, 
you do not meet the qualifications for this particular survey. 
We appreciate your time."
```

**Never** reveal the specific reason for termination (prevents gaming).

### Quota Management
When using quotas (e.g., 50% male, 50% female):
- Terminate with same message regardless of quota fill vs non-qualification
- Don't reveal quota status to respondents
- Track separately in routing logic

## Routing Logic in FLOW Section

```json
{
  "routing_rules": [
    {
      "rule_id": "R1",
      "condition": "SCR_Q1 = 'Under 18' OR SCR_Q1 = 'Prefer not to say'",
      "action": "Terminate survey (thank you screen)"
    },
    {
      "rule_id": "R2", 
      "condition": "SCR_Q2 = 'Never' OR SCR_Q2 = 'Not sure'",
      "action": "Terminate survey (thank you screen)"
    },
    {
      "rule_id": "R3",
      "condition": "All screener criteria met",
      "action": "Proceed to MAIN_SECTION"
    }
  ]
}
```

## Quality Checks

✓ Incidence rate matches expectations (test with pilot)
✓ Each question has clear qualify/disqualify criteria
✓ No leading questions that reveal "right" answer
✓ Screener flows logically (broad to specific)
✓ Termination messages are professional and non-revealing
✓ All categorical options are mutually exclusive and exhaustive
