---
name: rating-scales
description: |
  Provides standardized Likert scales, satisfaction ratings, and numeric scales to measure intensity of attitudes, perceptions, and behaviors. Use when quantifying agreement, satisfaction, likelihood, importance, or frequency across survey questions. Essential foundation for most quantitative research, typically combined with screening and other measurement methodologies. Not suitable as a standalone methodology - always supports other research objectives.
category: specialty
foundational: true
primary_use_case: Standardize measurement of attitude intensity and perception strength across all quantitative survey questions
secondary_applications:
  - Enable statistical analysis and benchmarking through consistent scaling
  - Support matrix questions for efficient multi-attribute rating
  - Provide industry-standard formats (NPS, CSAT, CES)
  - Create comparable metrics across studies and time periods
  - Support importance-performance analysis and driver modeling
commonly_combined_with:
  - screening
  - concept-test
  - brand-tracking
  - nps-csat
  - churn-retention
requires: []
problem_frames_solved:
  - performance_tracking
  - opinion_measurement
  - decline_diagnosis
  - experience_breakdown
decision_stages:
  - discover
  - define
  - design
  - validate
  - measure
  - optimize
study_types:
  - customer_satisfaction
  - brand_strategy
  - new_product_development
  - market_measurement
  - usage_attitudes
  - user_experience
  - advertising_comms
  - employee_research
  - opinion_polling
not_suitable_for:
  - Standalone research methodology (always supports other objectives)
  - Open-ended qualitative insights (use ethnography or interviews)
  - Complex trade-off decisions (use conjoint or maxdiff instead)
---


# Rating Scale Design

## Overview
Rating scales measure the intensity or degree of attitudes, perceptions, and behaviors.
Proper scale design ensures reliable, comparable data. This is a foundational skill —
it provides the building blocks that methodology-specific skills (concept-test, brand-tracking,
churn-retention, etc.) assemble into complete measurement frameworks.

---

## Scale Types

### 1. Likert Scales (Agreement)
**Use for**: Measuring agreement with attitudinal statements, segmentation batteries,
psychographic profiling.

**Standard 5-point**:
```json
{
  "question_text": "I would recommend this product to friends and family",
  "question_type": "scale",
  "options": [
    "Strongly agree",
    "Somewhat agree",
    "Neither agree nor disagree",
    "Somewhat disagree",
    "Strongly disagree"
  ]
}
```

**Standard 7-point** (more precision):
```json
{
  "options": [
    "Strongly agree",
    "Agree",
    "Somewhat agree",
    "Neither agree nor disagree",
    "Somewhat disagree",
    "Disagree",
    "Strongly disagree"
  ]
}
```

### 2. Satisfaction Scales
**Use for**: Measuring satisfaction with products, services, experiences, touchpoints.

**Standard 5-point**:
```json
{
  "question_text": "How satisfied are you with your overall experience with [BRAND]?",
  "question_type": "scale",
  "options": [
    "Very satisfied",
    "Satisfied",
    "Neither satisfied nor dissatisfied",
    "Dissatisfied",
    "Very dissatisfied"
  ]
}
```

**Standard 10-point** (for CSAT benchmarking):
```json
{
  "question_text": "Overall, how satisfied are you with [BRAND]? Please rate on a scale of 1 to 10.",
  "question_type": "scale",
  "options": [
    "1 - Extremely dissatisfied",
    "2", "3", "4", "5", "6", "7", "8", "9",
    "10 - Extremely satisfied"
  ],
  "notes": "CSAT score = mean rating. T2B = % selecting 9-10."
}
```

### 3. Purchase Intent Scale
**Use for**: Measuring likelihood to purchase a product or concept.

There are TWO different purchase intent constructs. Use the correct one for your context.

**Standard PI scale (for concept testing, NPD)**:
```json
{
  "question_text": "How likely would you be to purchase this product if it were available?",
  "question_type": "scale",
  "options": [
    "Definitely would purchase",
    "Probably would purchase",
    "Might or might not purchase",
    "Probably would not purchase",
    "Definitely would not purchase"
  ],
  "notes": "Industry-standard PI scale for concept evaluation. T2B = Definitely + Probably would purchase. Use this scale when the concept-test skill is active."
}
```

**Likelihood scale (for general behavioral intent)**:
```json
{
  "question_text": "How likely are you to switch broadband providers in the next 6 months?",
  "question_type": "scale",
  "options": [
    "Extremely likely",
    "Very likely",
    "Moderately likely",
    "Slightly likely",
    "Not at all likely"
  ],
  "notes": "General likelihood scale. Use for behavioral predictions outside concept testing contexts."
}
```

**Rule**: When the concept-test skill is active, ALWAYS use the standard PI scale
("Definitely would / Probably would"), not the likelihood scale ("Extremely likely / Very likely").
These are different constructs with different norms and benchmarks.

### 4. NPS (Net Promoter Score)
**Use for**: Measuring recommendation likelihood. Industry-standard 0-10 format.

```json
{
  "question_text": "How likely are you to recommend [BRAND] to a friend or colleague?",
  "question_type": "scale",
  "options": [
    "0 - Not at all likely",
    "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "10 - Extremely likely"
  ],
  "notes": "NPS. Detractors: 0-6, Passives: 7-8, Promoters: 9-10. NPS = %Promoters - %Detractors. Always follow with open-ended: 'What is the main reason for your score?'"
}
```

**NPS rules**:
- Always 0-10 scale. Never modify.
- Always follow with an open-ended verbatim question piping in the respondent's score.
- Only ask for brands/services the respondent has actually used (conditional display).

### 5. Customer Effort Score (CES)
**Use for**: Measuring ease of service interactions. Predicts churn better than CSAT
for service-driven categories.

**Standard 7-point CES**:
```json
{
  "question_text": "To what extent do you agree with the following statement: [BRAND] made it easy for me to resolve my issue.",
  "question_type": "scale",
  "options": [
    "Strongly agree",
    "Agree",
    "Somewhat agree",
    "Neither agree nor disagree",
    "Somewhat disagree",
    "Disagree",
    "Strongly disagree"
  ],
  "notes": "CES 2.0 format. Score = mean. Low-effort = Strongly agree + Agree. High-effort = Disagree + Strongly disagree. Show only to respondents who have interacted with the service/support touchpoint."
}
```

**Alternative CES format (5-point effort)**:
```json
{
  "question_text": "How easy was it to get your issue resolved?",
  "question_type": "scale",
  "options": [
    "Very easy",
    "Easy",
    "Neither easy nor difficult",
    "Difficult",
    "Very difficult"
  ],
  "notes": "Simpler CES variant. Use when asking about a specific interaction."
}
```

**CES rules**:
- Only ask about interactions the respondent has actually had (conditional display).
- Best measured soon after an interaction — in tracking studies, ask about most recent interaction.
- Can be applied to multiple touchpoints (e.g., ease of contacting support, ease of understanding bill, ease of using app).

### 6. Frequency Scales
**Use for**: Measuring how often behaviors occur.

```json
{
  "question_text": "How often do you experience slow internet speeds at home?",
  "question_type": "scale",
  "options": [
    "Never",
    "Rarely (less than once a month)",
    "Occasionally (1-3 times a month)",
    "Frequently (1-2 times a week)",
    "Very frequently (3+ times a week)"
  ]
}
```

### 7. Importance Scales
**Use for**: Measuring how important attributes or factors are to the respondent.

```json
{
  "question_text": "How important is internet speed reliability when choosing a broadband provider?",
  "question_type": "scale",
  "options": [
    "Extremely important",
    "Very important",
    "Moderately important",
    "Slightly important",
    "Not at all important"
  ]
}
```

**Warning on stated importance**: Asking respondents to rate importance directly often
produces flat distributions where most attributes are rated "very" or "extremely" important.
This provides weak discrimination between drivers. See the "Importance-Performance Analysis"
section below for the recommended approach that combines stated importance with satisfaction
ratings to produce derived importance through regression analysis.

---

## Importance-Performance Analysis (IPA)

### When to Use
IPA is the standard framework for diagnostic studies: customer satisfaction, churn analysis,
service quality assessment, and any research that needs to identify which attributes to
prioritize for improvement. It answers: "What matters most AND where are we underperforming?"

### How It Works
You collect TWO measures for each attribute:
1. **Importance**: How important is this attribute to the customer?
2. **Performance/Satisfaction**: How well does the brand/product deliver on this attribute?

The gap between importance and performance identifies priority action areas.

### Matrix Design for IPA

**Step 1: Importance matrix**
```json
{
  "question_id": "MS2_Q1",
  "question_text": "How important are each of the following when choosing a broadband provider?",
  "question_type": "matrix",
  "options": [],
  "rows": [
    "Internet speed during peak hours",
    "Connection reliability (no dropouts)",
    "Value for money",
    "Ease of contacting customer support",
    "Speed of resolving issues",
    "Clarity of billing and pricing",
    "Flexibility to change plans",
    "Quality of the mobile app / online account"
  ],
  "columns": [
    "Extremely important",
    "Very important",
    "Moderately important",
    "Slightly important",
    "Not at all important"
  ],
  "notes": "Importance ratings. Randomize row order. Pair with MS2_Q2 (satisfaction) for IPA."
}
```

**Step 2: Satisfaction matrix (SAME attributes)**
```json
{
  "question_id": "MS2_Q2",
  "question_text": "How satisfied are you with [BRAND] on each of the following?",
  "question_type": "matrix",
  "options": [],
  "rows": [
    "Internet speed during peak hours",
    "Connection reliability (no dropouts)",
    "Value for money",
    "Ease of contacting customer support",
    "Speed of resolving issues",
    "Clarity of billing and pricing",
    "Flexibility to change plans",
    "Quality of the mobile app / online account"
  ],
  "columns": [
    "Very satisfied",
    "Satisfied",
    "Neither satisfied nor dissatisfied",
    "Dissatisfied",
    "Very dissatisfied",
    "Not applicable"
  ],
  "notes": "Satisfaction ratings. MUST use identical attribute rows as importance matrix (MS2_Q1). Include 'Not applicable' for touchpoints not all respondents have experienced. Randomize row order (same order as MS2_Q1)."
}
```

**CRITICAL**: The importance and satisfaction matrices MUST use identical row attributes
in the same order. The rows are the unit of analysis — each attribute gets an importance
score and a performance score, which are plotted together.

### Derived Importance (Recommended Addition)
Stated importance (asking "how important is X?") tells you what people SAY matters.
Derived importance (regressing attribute satisfaction against overall satisfaction) tells
you what ACTUALLY drives satisfaction.

To enable derived importance analysis:
1. Include an **overall satisfaction** question BEFORE the attribute satisfaction matrix
2. Include attribute satisfaction ratings (the matrix above)
3. Analysis: Regress each attribute satisfaction score against overall satisfaction
   to determine which attributes have the strongest statistical relationship with
   overall satisfaction

The overall satisfaction question acts as the dependent variable:
```json
{
  "question_id": "MS2_Q0",
  "question_text": "Overall, how satisfied are you with [BRAND] as your broadband provider?",
  "question_type": "scale",
  "options": [
    "Very satisfied",
    "Satisfied",
    "Neither satisfied nor dissatisfied",
    "Dissatisfied",
    "Very dissatisfied"
  ],
  "notes": "Overall satisfaction. Place BEFORE attribute satisfaction matrix. Used as dependent variable for derived importance analysis."
}
```

**Best practice**: Report BOTH stated importance and derived importance. Where they diverge,
derived importance is more actionable (it reveals hygiene factors that people don't think
to mention but that drive dissatisfaction when they fail).

---

## Scale Direction Rules

### Default Direction
For most survey types, scales run **positive-first** (highest/best option at the top):
- "Very satisfied" → "Very dissatisfied"
- "Extremely important" → "Not at all important"
- "Strongly agree" → "Strongly disagree"

This is the natural reading direction for most online survey formats and matches
how respondents expect to interact with scales.

### Methodology-Specific Overrides
Some methodology skills specify their own scale direction. When a methodology skill
(e.g., concept-test, brand-tracking) specifies scale direction, follow the methodology
skill's guidance — it overrides this default.

### Within-Study Consistency Rule
**All scales of the same type within a single survey MUST use the same direction.**
Never mix positive-first and negative-first versions of the same scale type within
one survey. This confuses respondents and introduces measurement error.

Similarly, **use the same scale length for the same construct throughout a survey**.
If you use 5-point satisfaction for one attribute battery, use 5-point satisfaction
for all attribute batteries — never mix 5-point and 7-point versions of the same
construct in the same survey.

---

## Matrix Scale Design

### When to Use Matrix Format
Use matrix (grid) questions when:
- Rating **3 or more** items on the **identical** scale
- Items are conceptually related (e.g., all service attributes, all brand perceptions)
- The same response format applies to every row

### When to Avoid Matrix Format
- Fewer than 3 items → use individual scale questions
- Items need different scales → use individual questions
- Items are unrelated → use individual questions
- More than 12 rows → split into two matrices to prevent fatigue
- In screener sections → never use matrix for screening questions

### "Not Applicable" Column
**Always include a "Not applicable" or "Don't know" column when**:
- Not all respondents will have experienced every touchpoint
  (e.g., "Ease of contacting support" — some may never have called)
- Asking about brands the respondent may not know well enough to rate
- Asking about features the respondent may not have used

**Omit "Not applicable" only when** every row is guaranteed to be answerable by
every respondent (e.g., attitudinal statements in a segmentation battery where
all respondents can express agreement/disagreement).

Without "Not applicable," respondents forced to rate touchpoints they haven't
experienced will either guess (noise) or satisfice (pick the midpoint), both of
which contaminate the data.

### Matrix Example with N/A

```json
{
  "question_text": "How satisfied are you with each of the following aspects of [BRAND]?",
  "question_type": "matrix",
  "options": [],
  "rows": [
    "Speed of internet connection",
    "Reliability (no dropouts)",
    "Value for money",
    "Customer support responsiveness",
    "Billing clarity",
    "Mobile app experience"
  ],
  "columns": [
    "Very satisfied",
    "Satisfied",
    "Neither satisfied nor dissatisfied",
    "Dissatisfied",
    "Very dissatisfied",
    "Not applicable / Have not experienced"
  ],
  "notes": "Include N/A for touchpoints not all respondents have used. Randomize row order. Max 12 rows per matrix."
}
```

---

## Critical Design Rules

### 1. Scale Balance
Always use balanced scales with equal positive and negative options:
- 5-point: 2 positive, 1 neutral, 2 negative
- 7-point: 3 positive, 1 neutral, 3 negative

Never use unbalanced scales:
```
WRONG: Poor / Fair / Good / Very Good / Excellent  (1 negative vs 3 positive)
RIGHT: Very poor / Poor / Fair / Good / Very good
```

### 2. Endpoint Labels
- Always label the first and last option (endpoints)
- Always label the midpoint (neutral) for 5-point and 7-point scales
- For online surveys, label all points for maximum clarity (recommended)

### 3. Scale Length Selection

**5-point scales**: Default for most applications.
- Sufficient precision for most research needs
- Lower cognitive load → better completion rates
- Use for: satisfaction, importance, agreement, likelihood

**7-point scales**: More precision, higher cognitive load.
- Use when detecting subtle differences matters
- Good for advanced analytics (factor analysis, SEM)
- Use for: segmentation batteries where discrimination matters

**10 or 11-point scales**: Industry standard formats only.
- NPS: 0-10 (11 points). Never modify.
- CSAT benchmark: 1-10 (10 points). Use when comparing to industry benchmarks.
- Do not invent custom 10-point scales.

**Avoid**:
- 3-point scales (too coarse, poor discrimination)
- 4 or 6-point scales (forced choice without neutral — only use intentionally when methodology requires)
- Scales longer than 11 points (diminishing returns)

### 4. Neutral Option

**Include neutral** when:
- Respondents may genuinely have no opinion
- Measuring agreement/disagreement
- General attitude measurement

**Omit neutral (force choice)** when:
- Need decisive responses for decision-making
- Methodology requires it (e.g., some forced-choice preference tasks)

### 5. Within-Study Consistency (CRITICAL)

Within a single survey:
- Use the **same scale length** for the same construct (don't mix 5-point and 7-point satisfaction)
- Use the **same direction** for the same scale type (don't flip positive/negative-first)
- Use the **same labels** for the same construct (don't use "Very satisfied" in one question and "Extremely satisfied" in another for the same satisfaction scale)
- Use the **same column headings** across related matrices

Inconsistency confuses respondents, introduces measurement error, and makes
cross-question analysis unreliable.

---

## Common Scale Wording Reference

### Agreement (Likert)
Strongly agree / Somewhat agree / Neither agree nor disagree / Somewhat disagree / Strongly disagree

### Satisfaction
Very satisfied / Satisfied / Neither satisfied nor dissatisfied / Dissatisfied / Very dissatisfied

### Importance
Extremely important / Very important / Moderately important / Slightly important / Not at all important

### Likelihood (general behavioral intent)
Extremely likely / Very likely / Moderately likely / Slightly likely / Not at all likely

### Purchase Intent (concept testing — different construct)
Definitely would purchase / Probably would purchase / Might or might not purchase / Probably would not purchase / Definitely would not purchase

### Effort
Very easy / Easy / Neither easy nor difficult / Difficult / Very difficult

### Quality
Excellent / Very good / Good / Fair / Poor

### Frequency
Very frequently / Frequently / Occasionally / Rarely / Never

### Concern
Extremely concerned / Very concerned / Moderately concerned / Slightly concerned / Not at all concerned

---

## Quality Checklist

- [ ] All scales are balanced (equal positive and negative options)
- [ ] Endpoints and midpoints are clearly labeled
- [ ] Same scale length used for same construct throughout survey
- [ ] Same direction used for same scale type throughout survey
- [ ] Same labels used for same construct throughout survey
- [ ] "Not applicable" included in matrices where not all rows apply to all respondents
- [ ] "Don't know" included where respondents may lack information to answer
- [ ] Matrix questions have 3-12 rows (split if more than 12)
- [ ] Purchase intent uses standard PI scale when concept-test skill is active
- [ ] NPS uses standard 0-10 format with verbatim follow-up
- [ ] IPA pairs use identical attribute rows in importance and satisfaction matrices
- [ ] Overall satisfaction placed BEFORE attribute satisfaction (for derived importance)
- [ ] CES questions shown only to respondents who experienced the relevant interaction