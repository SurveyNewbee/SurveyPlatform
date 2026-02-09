---
name: demographics
description: |
  Collects standard classification variables (age, gender, income, education, household composition) to enable segmentation analysis and sample profiling. Use at the end of every survey after all substantive questions to minimize dropout from personal questions. Essential foundation for cross-tabulation analysis and quota monitoring across virtually all research studies.
category: specialty
foundational: true
primary_use_case: Enable segmentation analysis and sample profiling by collecting respondent classification variables
secondary_applications:
  - Quota monitoring and sample balancing during fieldwork
  - Post-stratification weighting of survey results
  - Audience profiling for targeting and media planning
  - Compliance with diversity and inclusion reporting requirements
commonly_combined_with:
  - screening
  - rating-scales
  - segmentation
  - brand-tracking
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
  - brand_tracking
  - customer_satisfaction
  - market_research
  - opinion_polling
  - employee_research
  - usage_attitudes
  - advertising_testing
  - concept_testing
  - pricing_research
  - segmentation_study
not_suitable_for:
  - Qualifying respondents for study participation (use screening instead)
  - Primary research objectives or key business decisions
  - Placement at beginning of survey (causes higher dropout rates)
---


# Demographics Section Design

## Overview
Demographics are classification variables collected at the END of surveys. They enable segmentation analysis and sample profiling but should be asked last to minimize dropout.

## Core Principle
**Always place demographics at the END of the survey** (after all substantive questions). Respondents are more willing to share personal information after they're invested in the survey.

## Standard Demographic Questions

### Age
```json
{
  "question_id": "DEMO_AGE",
  "question_text": "What is your age?",
  "question_type": "single_choice",
  "options": [
    "Under 18",
    "18-24",
    "25-34",
    "35-44",
    "45-54",
    "55-64",
    "65-74",
    "75 or older",
    "Prefer not to say"
  ]
}
```

**Alternative (exact age)**:
```json
{
  "question_id": "DEMO_AGE_EXACT",
  "question_text": "What is your age?",
  "question_type": "open_ended"
}
```
Use ranges for general surveys; exact age for narrow targeting.

### Gender
```json
{
  "question_id": "DEMO_GENDER",
  "question_text": "What is your gender?",
  "question_type": "single_choice",
  "options": [
    "Male",
    "Female",
    "Non-binary",
    "Prefer to self-describe",
    "Prefer not to say"
  ]
}
```

### Household Income
```json
{
  "question_id": "DEMO_INCOME",
  "question_text": "What is your total annual household income before taxes?",
  "question_type": "single_choice",
  "options": [
    "Less than $25,000",
    "$25,000 to $49,999",
    "$50,000 to $74,999",
    "$75,000 to $99,999",
    "$100,000 to $149,999",
    "$150,000 to $199,999",
    "$200,000 or more",
    "Prefer not to say"
  ]
}
```

**Adjust ranges** based on country and category (luxury vs mass market).

### Education
```json
{
  "question_id": "DEMO_EDUCATION",
  "question_text": "What is the highest level of education you have completed?",
  "question_type": "single_choice",
  "options": [
    "Less than high school",
    "High school diploma or equivalent",
    "Some college, no degree",
    "Associate's degree",
    "Bachelor's degree",
    "Master's degree",
    "Doctorate or professional degree",
    "Prefer not to say"
  ]
}
```

### Employment Status
```json
{
  "question_id": "DEMO_EMPLOYMENT",
  "question_text": "Which of the following best describes your current employment status?",
  "question_type": "single_choice",
  "options": [
    "Employed full-time",
    "Employed part-time",
    "Self-employed",
    "Unemployed and looking for work",
    "Unemployed and not looking for work",
    "Retired",
    "Student",
    "Stay-at-home parent",
    "Prefer not to say"
  ]
}
```

### Marital Status
```json
{
  "question_id": "DEMO_MARITAL",
  "question_text": "What is your current marital status?",
  "question_type": "single_choice",
  "options": [
    "Single, never married",
    "Married or domestic partnership",
    "Widowed",
    "Divorced",
    "Separated",
    "Prefer not to say"
  ]
}
```

### Household Composition
```json
{
  "question_id": "DEMO_HH_SIZE",
  "question_text": "Including yourself, how many people currently live in your household?",
  "question_type": "single_choice",
  "options": [
    "1 (just me)",
    "2",
    "3",
    "4",
    "5",
    "6 or more",
    "Prefer not to say"
  ]
}
```

**Children in household**:
```json
{
  "question_id": "DEMO_CHILDREN",
  "question_text": "How many children under 18 currently live in your household?",
  "question_type": "single_choice",
  "options": [
    "0",
    "1",
    "2",
    "3",
    "4 or more",
    "Prefer not to say"
  ]
}
```

### Geographic
```json
{
  "question_id": "DEMO_REGION",
  "question_text": "In which region do you currently live?",
  "question_type": "single_choice",
  "options": [
    "Northeast",
    "Southeast", 
    "Midwest",
    "Southwest",
    "West",
    "Prefer not to say"
  ]
}
```

**Or postal/zip code** (for precise location):
```json
{
  "question_id": "DEMO_ZIP",
  "question_text": "What is your ZIP code?",
  "question_type": "open_ended"
}
```

### Race/Ethnicity
```json
{
  "question_id": "DEMO_ETHNICITY",
  "question_text": "Which of the following best describes your race or ethnicity? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": [
    "White or Caucasian",
    "Black or African American",
    "Hispanic or Latino",
    "Asian or Pacific Islander",
    "Native American or Alaska Native",
    "Middle Eastern or North African",
    "Multiracial",
    "Other",
    "Prefer not to say"
  ]
}
```

## Category-Specific Demographics

### B2B Research
```json
{
  "question_id": "DEMO_COMPANY_SIZE",
  "question_text": "How many employees does your company have?",
  "question_type": "single_choice",
  "options": [
    "1-10 employees",
    "11-50 employees",
    "51-200 employees",
    "201-500 employees",
    "501-1,000 employees",
    "1,001-5,000 employees",
    "More than 5,000 employees",
    "Not sure"
  ]
},
{
  "question_id": "DEMO_INDUSTRY",
  "question_text": "Which industry does your company primarily operate in?",
  "question_type": "single_choice",
  "options": [
    "Technology/Software",
    "Healthcare",
    "Financial Services",
    "Manufacturing",
    "Retail/E-commerce",
    "Professional Services",
    "Education",
    "Government",
    "Other"
  ]
},
{
  "question_id": "DEMO_JOB_TITLE",
  "question_text": "What is your job title?",
  "question_type": "open_ended"
}
```

## Design Guidelines

### 1. Question Order
Standard order (most to least sensitive):
1. Age
2. Gender  
3. Employment
4. Education
5. Marital status
6. Household composition
7. Income (most sensitive - ask last)
8. Race/ethnicity (very sensitive - optional)

### 2. Always Include "Prefer Not to Say"
Every demographic question should have an opt-out option. **Never force** respondents to answer sensitive questions.

### 3. Keep It Minimal
Only ask demographics that:
- Are essential for segmentation
- Will actually be used in analysis
- Are relevant to the research objectives

**Avoid** asking "nice to know" demographics that bloat the survey.

### 4. Cultural Sensitivity
- Adapt income ranges to local currency and norms
- Adjust education levels to local systems
- Be sensitive to regional differences in acceptable demographic questions

### 5. Mobile-Friendly
- Use simple single-choice or multiple-choice formats
- Avoid long dropdown lists
- Keep option lists scannable (8-10 options max)

## Common Pitfalls

❌ Asking demographics at start of survey (higher dropout)
❌ Forcing answers to sensitive questions (use "Prefer not to say")
❌ Too many demographic questions (survey fatigue)
❌ Inappropriate categories (e.g., income ranges too broad/narrow for category)
❌ Missing "Other" or "Prefer to self-describe" options
❌ Using exact age when ranges would suffice

## Quality Checks

✓ All demographics at end of survey
✓ Every question has "Prefer not to say" option
✓ Income ranges appropriate for category/geography
✓ Question wording is neutral and non-judgmental
✓ Only asking demographics that will be used in analysis
✓ Options are mutually exclusive and exhaustive
