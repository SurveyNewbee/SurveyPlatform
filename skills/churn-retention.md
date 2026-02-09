---
name: churn-retention
description: |
  Identifies why customers leave, who is at risk of churning, and what actions can prevent or reverse churn through behavioral analysis and lifecycle diagnostics. Use when retention rates are declining, churn costs are high, or you need to prioritize retention investments across customer segments. Must distinguish actual churn behavior from dissatisfaction and focus on actionable, fixable drivers rather than structural constraints.
category: customer_satisfaction
foundational: false
primary_use_case: Diagnose churn drivers and identify actionable retention strategies to reduce customer attrition and increase lifetime value
secondary_applications:
  - Early warning system development for at-risk customer identification
  - Competitive loss analysis and switching behavior understanding
  - Customer lifecycle optimization and intervention timing
  - Save offer effectiveness and recovery program design
commonly_combined_with:
  - nps-csat
  - voc-programs
  - customer-lifecycle
  - segmentation
  - concept-test (for retention offer testing within churn studies)
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - decline_diagnosis
  - performance_tracking
  - experience_breakdown
decision_stages:
  - measure
  - optimize
study_types:
  - customer_satisfaction
  - retention_loyalty
not_suitable_for:
  - New customer acquisition research (use go-to-market-validation instead)
  - Brand perception or awareness studies
  - Early-stage product development before customer base exists
---


# Churn & Retention Research Methodology

## Overview

Churn & Retention research is a **customer lifecycle methodology** used to identify **why customers leave, who is at risk of leaving, and what actions most effectively prevent or reverse churn**. It is critical for subscription, contract, SaaS, service, and repeat-purchase businesses where retention materially impacts growth and profitability.

This methodology prioritizes **behavioral signals, timing accuracy, and actionability**. Surveys must distinguish *actual churn behavior* from dissatisfaction and isolate *fixable drivers* from structural constraints.

---

## Core Principles

- **Behavior defines churn.**
  Churn must be defined by **observable behavior** (cancellation, non-renewal, inactivity), not attitudes or intent alone.

- **Separate paths, not display logic.**
  Churned and current customers have fundamentally different experiences. Design separate survey paths — not one linear survey with "Not applicable" options toggled on and off.

- **Lifecycle precision.**
  Customers at different lifecycle stages (new, established, renewing, former) must be analyzed separately.

- **Recency matters.**
  Diagnostics must be collected close to the churn or renewal event to minimize rationalization and memory decay.

- **Separation of symptoms and causes.**
  Dissatisfaction is a symptom; underlying drivers must be explicitly identified.

- **Comparative framing.**
  Churn decisions are almost always comparative (switching vs. stopping). Capture alternatives where relevant.

- **Save potential focus.**
  The goal is not just explanation, but identifying **interventions that could realistically change outcomes**.

- **CRM-first efficiency.**
  When sample is sourced from CRM, don't ask questions the CRM already answers. Use the survey for perception, attitude, and diagnostic questions that CRM data cannot provide.

---

## CRITICAL: Multi-Path Survey Architecture

Churn studies serve fundamentally different respondent groups who have had fundamentally different experiences. The survey MUST be designed as **separate paths** that share common elements where appropriate, NOT as a single linear questionnaire with display_logic toggles.

### Required Paths

For a typical churn study with three segments (churned, at-risk, stable):

```
SCREENER (all)
    ↓
CUSTOMER STATUS CLASSIFICATION → Routes to path
    ↓                    ↓                    ↓
[CHURNED PATH]      [AT-RISK PATH]      [STABLE PATH]
    ↓                    ↓                    ↓
Former Profile      Current Profile     Current Profile
    ↓                    ↓                    ↓
Retrospective       Current              Current
Satisfaction        Satisfaction          Satisfaction
    ↓                    ↓                    ↓
Switching Journey   Competitive           Competitive
(pre-churn          Consideration         Consideration
behavior,           (considered           (lower
retention attempt,  switching? who?       priority)
post-switch         what stopped you?)
comparison,
win-back potential)
    ↓                    ↓                    ↓
    └──────────── SHARED SECTIONS ─────────────┘
                         ↓
               Retention Offer Testing
                         ↓
               Driver Importance (all)
                         ↓
               Demographics
```

### Path Design Rules

1. **Profile sections are path-specific.** Churned customers answer about their former service; current customers answer about their current service. Use past tense for churned, present tense for current.

2. **Satisfaction batteries must be identical across paths** — same rows, same scale, same wording (except tense). This enables direct comparison between churned, at-risk, and stable satisfaction profiles.

3. **The switching journey section is CHURNED-ONLY.** Current customers do not get pre-churn behavior questions, retention attempt questions, or post-switch comparison. They get competitive consideration questions instead.

4. **Retention offer testing and driver importance are SHARED** — all segments see these sections.

5. **The FLOW section must define complete path routing** — not just question-level display_logic. Each path should be described as a complete sequence of sections.

### Implementation in JSON

Path routing belongs in FLOW.routing_rules, NOT in question-level display_logic:

```json
{
  "rule_id": "R_CHURNED_PATH",
  "condition": "SCR_Q2 = 'I previously had [BRAND] but switched to another provider'",
  "action": "Route to CHURNED_PROFILE → SATISFACTION_FORMER → CHURN_JOURNEY → RETENTION_OFFERS → DRIVER_IMPORTANCE → DEMOGRAPHICS"
},
{
  "rule_id": "R_CURRENT_PATH",
  "condition": "SCR_Q2 = 'I currently have [BRAND] as my provider'",
  "action": "Route to CURRENT_PROFILE → SATISFACTION_CURRENT → COMPETITIVE_CONTEXT → RETENTION_OFFERS → DRIVER_IMPORTANCE → DEMOGRAPHICS"
}
```

Use display_logic on individual questions ONLY for simple within-section conditional displays (e.g., "show CES only if contacted support").

---

## CRM-Sourced Sample Design

Many churn studies use CRM databases rather than open panels. This changes the survey design significantly.

### CRM Append Strategy

When sample is CRM-sourced, the following data should be **appended from CRM records**, NOT asked in the survey:

| Data Field | CRM Source | Survey Role |
|---|---|---|
| Customer ID | CRM record | Linking variable |
| Customer status | Churn/active flag | Pre-classification (validate in screener) |
| Tenure | Account start date | Analysis segmentation |
| Plan/tier | Account details | Analysis segmentation |
| Region | Account address | Quota management |
| Complaint history | Support records | Risk classification |
| Cancellation date | Account records | Recency verification |
| Last contact date | Support records | Behavioral analysis |

**Survey validates but doesn't duplicate.** The screener confirms customer status with a neutral question (see Privacy-Sensitive Wording below), and the CRM flag provides the definitive classification for analysis.

### When CRM Data Is NOT Available

If sample is panel-sourced (no CRM append), the survey must capture tenure, plan type, recency of churn, and self-reported customer status directly. Add these as screener or early main-section questions.

### Programming Specification

Include a `CRM_append_fields` list in STUDY_METADATA or PROGRAMMING_SPECIFICATIONS:

```json
"CRM_append_fields": [
  "Customer_ID",
  "Customer_Status (Churned/At-Risk/Stable)",
  "Tenure_Months",
  "Plan_Type",
  "Region",
  "Complaint_History_Flag",
  "Cancellation_Date (if churned)",
  "Last_Contact_Date"
]
```

---

## Privacy-Sensitive Wording

CRITICAL: When researching customers sourced from CRM data, survey language must **never imply the company has access to specific complaint data, call transcripts, or behavioral records** — even though it does.

### Rules

1. **Screener classification must be neutral.** Ask about general customer status, not specific behavior the CRM recorded.

   CORRECT:
   > "Which of the following best describes your current internet/broadband service situation?"
   > - I currently have [BRAND] as my provider
   > - I previously had [BRAND] but switched to another provider
   > - I have never had [BRAND]

   WRONG:
   > "Which best describes your relationship with [BRAND]?"
   > - I am a current customer with no recent complaints
   > - I am a current customer who has made a complaint or enquired about cancelling
   > - I cancelled within the past 6 months

   The WRONG version reveals that the company has complaint records and is segmenting respondents by complaint behavior. This makes respondents feel surveilled.

2. **Let CRM flags do the segmentation.** The CRM already knows who complained and who cancelled. Use the CRM flag for routing and quota assignment; use the neutral screener for respondent experience.

3. **Frame questions as general experience**, not specific incidents. Ask "have you experienced any issues?" not "we noticed you called about an issue."

4. **Invitation language must be neutral.** Email subject lines should reference "internet services research" or "your opinion matters," not "we noticed you left" or "help us understand your cancellation."

---

## Survey Section Requirements

### 1. Screener

Confirm identity and qualify respondents. For CRM-sourced samples, this validates status rather than discovering it.

Required screener questions:
- Decision-maker role (primary or joint — screen out non-decision-makers)
- Customer status (current vs. former — neutral wording, routes to path)
- Industry exclusion (screen out market research and focal industry employees)
- Region (for quota management, if not appended from CRM)

### 2. Customer Profile (Path-Specific)

**Current customers:** Current plan, tenure (if not CRM-appended).
**Churned customers:** Former plan, tenure, when cancelled, who they switched to.

The "who did you switch to?" question is CRITICAL for churned customers — it's the foundation of competitive loss analysis. Include all major competitors plus "Other" and "I don't currently have [service]."

### 3. Satisfaction Assessment (Path-Specific, Identical Battery)

**CRITICAL: Follow rating-scales skill rules for IPA.**

The satisfaction section MUST follow this order:
1. **Overall satisfaction FIRST** (single question, before any attribute ratings)
2. **Attribute satisfaction matrix** (detailed performance ratings)
3. **Behavioral problem incidence** (multi-select checklist)
4. **Customer service contact and CES** (conditional)
5. **NPS + verbatim** (per nps-csat skill)

#### Overall Satisfaction

Place BEFORE the attribute matrix. This is the dependent variable for derived importance analysis. If it comes after the attribute ratings, respondents anchor their overall rating on the specific attributes they just evaluated, contaminating the DV.

```json
{
  "question_id": "SAT_C1",
  "question_text": "Overall, how satisfied are you with [BRAND] as your [service] provider?",
  "question_type": "scale",
  "options": [
    "Extremely satisfied",
    "Very satisfied",
    "Moderately satisfied",
    "Slightly satisfied",
    "Not at all satisfied"
  ],
  "notes": "Overall satisfaction. Place BEFORE attribute matrix. Primary DV for key driver analysis."
}
```

For churned customers, use past tense: "Thinking back to when you were a [BRAND] customer, overall how satisfied were you..."

#### Attribute Satisfaction Matrix

The rows in this matrix MUST exactly match the rows in the Driver Importance matrix (Section 7). This is non-negotiable for IPA analysis.

Design attributes in grouped domains:
- **Service quality** (speed, reliability, consistency, outage frequency, technical issue resolution)
- **Pricing** (value for money, pricing transparency)
- **Customer experience** (customer service quality, account management, communication, plan flexibility)

Include "Not applicable / Haven't experienced" as final column.

Example (11 attributes covering three domains):

```json
{
  "question_id": "SAT_C2",
  "question_text": "How satisfied are you with the following aspects of your [BRAND] service?",
  "question_type": "matrix",
  "rows": [
    "Internet speed during peak hours (evenings/weekends)",
    "Internet speed during off-peak hours",
    "Consistency and reliability of connection",
    "Frequency of outages or service interruptions",
    "Speed of resolving technical issues when they occur",
    "Value for money given the price you pay",
    "Transparency of pricing and billing",
    "Quality of customer service when you contact them",
    "Ease of managing your account online or via app",
    "Clarity of communication from [BRAND]",
    "Range of plan options available to you"
  ],
  "columns": [
    "Extremely satisfied",
    "Very satisfied",
    "Moderately satisfied",
    "Slightly satisfied",
    "Not at all satisfied",
    "Not applicable / Haven't experienced"
  ],
  "notes": "Attribute satisfaction. Rows MUST match DRIVER_IMPORTANCE matrix rows exactly for IPA. Randomize row order."
}
```

For churned customers, use identical rows with past tense in the question stem and scale labels adjusted ("Didn't experience" instead of "Haven't experienced").

#### Behavioral Problem Incidence

A multi-select checklist of specific problems the customer has experienced. This validates satisfaction ratings with behavioral data and enables triangulation (stated satisfaction vs. actual problems encountered).

```json
{
  "question_id": "SAT_C3",
  "question_text": "In the past [timeframe], have you experienced any of the following issues with your [BRAND] service? (Select all that apply)",
  "question_type": "multiple_choice",
  "options": [
    "Slow speeds during peak times",
    "Slow speeds at other times",
    "Frequent dropouts or disconnections",
    "Complete service outages",
    "Delays in technical support response",
    "Billing errors or unexpected charges",
    "Difficulty reaching customer service",
    "Confusing or unclear communication",
    "Problems with online account management",
    "None of the above"
  ],
  "notes": "Behavioral validation of satisfaction. 'None of the above' is exclusive."
}
```

#### Customer Service Contact and CES

Ask whether the customer has contacted support, then conditionally show Customer Effort Score (CES). CES is a strong predictor of churn — stronger than satisfaction for service-driven industries.

```json
{
  "question_id": "SAT_C4",
  "question_text": "Have you contacted [BRAND] customer service in the past 6 months?",
  "question_type": "single_choice",
  "options": ["Yes", "No"],
  "notes": "Gate question for CES. Route: Yes → show CES, No → skip to NPS."
}
```

```json
{
  "question_id": "SAT_C5",
  "question_text": "Thinking about your most recent interaction with [BRAND] customer service, how much effort did you personally have to put forth to get your issue resolved?",
  "question_type": "scale",
  "options": [
    "Very low effort",
    "Low effort",
    "Moderate effort",
    "High effort",
    "Very high effort",
    "My issue was not resolved"
  ],
  "display_logic": "Show only if SAT_C4 = 'Yes'",
  "notes": "Customer Effort Score (CES). Strong churn predictor. Per nps-csat skill."
}
```

#### NPS + Verbatim

Standard NPS (0-10) followed by mandatory open-ended verbatim. Per nps-csat skill.

### 4. Churn Drivers (Churned and At-Risk)

**Primary reason** (single-select, forced choice) → **Secondary factors** (multi-select) → **Driver impact matrix** (rated importance of each factor in the decision).

For stable customers who are not considering cancelling: SKIP this section entirely. Do not show it with a "Not applicable" option.

#### Save Potential (Churned Only)

```json
{
  "question_id": "CJ_SAVE",
  "question_text": "If the main issue you experienced had been resolved, how likely would you have been to continue as a customer?",
  "question_type": "scale",
  "options": [
    "Very likely to stay",
    "Likely to stay",
    "Neither likely nor unlikely",
    "Unlikely to stay",
    "Very unlikely to stay"
  ],
  "notes": "Save potential assessment. Churned customers only. Quantifies preventable vs structural churn."
}
```

### 5. Switching Journey (CHURNED ONLY)

This section captures the complete switching decision journey. It is shown ONLY to churned customers.

Required questions:
1. **Pre-churn behavior** — "Before you switched, which actions did you take?" (contacted to report problem, asked about better pricing, told them you were considering leaving, researched other providers, compared prices, asked friends, etc.)
2. **Retention attempt** — "Did [BRAND] make any attempt to keep you as a customer?" (offered discount, offered upgrade, made unappealing offer, made no offer)
3. **Why retention failed** (open-ended, conditional on retention attempt being made)
4. **Post-switch comparison** — "How satisfied are you with your current provider compared to [BRAND]?" (Much more satisfied → Much less satisfied)
5. **Win-back potential** — "How likely would you be to consider returning to [BRAND] in the future?" (5-point likelihood)

The pre-churn behavior question is particularly valuable — it identifies whether churned customers gave the company warning signals before leaving (and therefore whether intervention was possible).

### 6. Competitive Consideration (CURRENT CUSTOMERS ONLY)

This section is the current-customer equivalent of the switching journey. It captures competitive threat without the actual switching event.

Required questions:
1. **Switching consideration** — "In the past 6 months, have you actively considered switching to a different provider?" (Yes/No — gates subsequent questions)
2. **Competitive set** — "Which providers did you consider?" (multi-select, show if considered switching)
3. **Switching barriers** — "What stopped you from switching?" (multi-select, show if considered switching)
4. **Competitive comparison** — "How does [BRAND] compare to other providers on the following?" (matrix with comparative scale: Much better → Much worse → Don't know)

The switching barriers question is critical for retention strategy — "too much hassle to change" (passive retention) is a fundamentally different insight from "[BRAND] resolved my issue" (active retention).

### 7. Driver Importance (ALL RESPONDENTS)

Stated importance of each service dimension. This section is shared across all paths.

**CRITICAL: The rows in this matrix MUST exactly match the rows in the Satisfaction matrix (Section 3).** Same count, same concepts, matched wording. This enables Importance-Performance Analysis (IPA) and penalty-reward analysis.

```json
{
  "question_id": "IMP1",
  "question_text": "How important is each of the following when choosing or evaluating an internet provider?",
  "question_type": "matrix",
  "rows": [
    "Internet speed during peak hours",
    "Internet speed during off-peak hours",
    "Consistent and reliable connection",
    "Infrequent outages or service interruptions",
    "Quick resolution of technical issues",
    "Good value for money",
    "Transparent pricing and billing",
    "Helpful and responsive customer service",
    "Easy-to-use online account management",
    "Clear communication about service issues",
    "Flexible plan options"
  ],
  "columns": [
    "Extremely important",
    "Very important",
    "Moderately important",
    "Slightly important",
    "Not at all important"
  ],
  "notes": "Stated importance. Rows MUST match satisfaction matrix rows for IPA. Randomize row order."
}
```

**Also include a single direct priority question** to validate driver analysis:

```json
{
  "question_id": "IMP2",
  "question_text": "Which ONE improvement from [BRAND] would be most important to you personally?",
  "question_type": "single_choice",
  "options": [
    "Faster internet speeds",
    "More consistent/reliable connection",
    "Lower monthly pricing",
    "Better customer service",
    "Easier account management",
    "More flexible contract terms",
    "Better communication about outages and issues"
  ],
  "notes": "Direct priority validation. Randomize options. Validates regression-based driver analysis."
}
```

### 8. Retention Offer Testing (ALL RESPONDENTS)

Two approaches, depending on study design and LOI budget:

#### Approach A: Lean Ranking (Default — 2-3 questions, ~2 min)

Use when retention offer testing is one component of a broader churn study, or LOI is constrained (≤15 min total).

1. **Forced ranking** of 3-5 specific, concrete offers (not multi-bullet packages)
2. **Effectiveness measure** piping top-ranked offer: "If [BRAND] offered you [top choice], how likely would this be to keep you as a customer / convince you to return?"
3. Optional: open-ended "Why did you rank [top choice] first?"

```json
{
  "question_id": "RET1",
  "question_text": "Which of the following offers would make you most likely to stay with [BRAND]? Please rank from most appealing (1) to least appealing (4).",
  "question_type": "ranking",
  "options": [
    "20% discount on your monthly bill for 12 months",
    "Free upgrade to the next speed tier for 12 months",
    "Priority customer support with guaranteed 24-hour response time",
    "Price lock guarantee — your rate won't increase for 24 months"
  ],
  "notes": "Lean retention offer ranking. Each offer maps to an investment area (pricing, infrastructure, service, pricing stability). Pipe top choice into RET2."
}
```

```json
{
  "question_id": "RET2",
  "question_text": "If [BRAND] offered you [PIPE: top-ranked offer from RET1], how likely would this be to [keep you as a customer / convince you to return]?",
  "question_type": "scale",
  "options": [
    "Extremely likely",
    "Very likely",
    "Moderately likely",
    "Slightly likely",
    "Not at all likely"
  ],
  "piping": "Insert respondent's top-ranked offer from RET1. Adapt stem for churned (return) vs current (stay).",
  "notes": "Retention offer effectiveness. Measures conversion probability for preferred intervention."
}
```

#### Approach B: Full Monadic Concept Test (Optional — 15-25 questions, ~5-8 min)

Use when retention offer testing is the PRIMARY objective of the study, when offers are complex multi-element packages, or when detailed diagnostics (appeal, relevance, believability) are needed per offer.

Follow concept-test skill guidance:
- Separate subsection per offer (MS6_A, MS6_B, MS6_C)
- Sequential monadic with counterbalanced rotation
- Evaluation battery: appeal, retention intent (adapted PI scale: "Definitely would stay/return"), relevance, believability, open-ended likes/dislikes
- Comparison section with preference + ranking + rationale

**Adapt the PI scale for retention context:**
- "Definitely would stay/return" (not "Definitely would purchase")
- "Probably would stay/return"
- "Might or might not stay/return"
- "Probably would not stay/return"
- "Definitely would not stay/return"

**Default to Approach A** unless the brief explicitly calls for detailed offer testing or the study is primarily about retention offer evaluation. Approach B adds 5-8 minutes to LOI and is excessive for studies with a 12-15 minute LOI constraint.

### 9. Demographics

Standard demographics, but include context-relevant items:

- Age, gender, household composition (standard)
- **Household size** (correlates with bandwidth demand)
- **Work-from-home status** (correlates with performance expectations and churn risk)
- Income (if not available from CRM)
- Dwelling type (may relate to infrastructure/connectivity quality)

If CRM already provides demographic data, limit survey demographics to items CRM doesn't have (e.g., WFH status, household composition).

---

## LOI Management

Churn studies from CRM-sourced samples have tighter LOI constraints than panel surveys because respondents are less motivated (no panel incentive habit) and more sensitive (they may have a negative relationship with the brand).

### LOI Targets

| Study Type | Target LOI | Max LOI |
|---|---|---|
| Churn diagnosis + lean retention testing | 12-15 min | 15 min |
| Churn diagnosis + full monadic retention offers | 18-20 min | 20 min |
| Churn diagnosis only (no retention testing) | 10-12 min | 12 min |

### LOI Efficiency Rules

1. **CRM append saves 2-3 minutes.** Don't ask tenure, plan, region, or complaint history if CRM provides them.
2. **Lean retention testing saves 5-8 minutes** vs full monadic approach.
3. **Behavioral problem incidence** (multi-select) takes ~30 seconds vs 2-3 minutes for a full diagnostic satisfaction matrix. Include it — it's high-value and fast.
4. **Separate paths reduce per-respondent LOI** because churned customers skip competitive consideration and vice versa.
5. **Cap matrix batteries at 11 rows.** Split or reduce if more rows needed.

---

## Analysis Framework

### Churn Driver Model

The survey must enable triangulation of multiple driver identification methods:

| Method | Data Source | What It Reveals |
|---|---|---|
| Derived importance | Regression of attribute satisfaction against overall CSAT | Which attributes statistically drive satisfaction (and by extension retention) |
| Stated importance | Driver importance matrix (Section 7) | What customers say matters to them |
| Stated reasons | Primary/secondary churn reasons (Section 4) | Direct causality claims from churned customers |
| Behavioral validation | Problem incidence checklist (Section 3) | Which problems were actually experienced |
| Revealed preferences | Retention offer ranking/preference (Section 8) | What customers would act on |

**Best practice:** Report all five and note where they converge (high confidence) and diverge (further investigation needed). Where stated importance and derived importance disagree, derived importance is more actionable (it reveals hygiene factors people don't consciously value).

### Key Outputs

1. **Churn driver ranking** — Prioritized list of drivers with impact scores, segmented by customer status.
2. **Preventable vs structural churn** — % of churn that was fixable (save potential) vs structural (moving house, no longer needs service).
3. **Early warning profile** — Satisfaction thresholds, problem patterns, and behavioral flags that differentiate at-risk from stable customers.
4. **Competitive loss analysis** — Where customers go when they leave, why they chose the competitor, whether they're happier now.
5. **Investment prioritization** — IPA quadrant analysis mapping driver importance against current performance to identify priority improvement areas.
6. **Retention offer effectiveness** — Which intervention would have highest take-rate, by segment.
7. **Win-back opportunity sizing** — % of churned customers open to returning, and under what conditions.

### Segmentation Axes

Always analyze by:
- Customer status (churned vs at-risk vs stable)
- Tenure (early tenure risk period vs established)
- Plan type/tier
- Region (if infrastructure quality varies geographically)
- Problem experience (had issues vs no issues)

---

## Common Mistakes to Avoid

### Architectural Mistakes

- **Single linear path for all segments.**
  *Wrong:* One questionnaire with display_logic toggling questions on/off per segment.
  *Correct:* Separate paths for churned vs current customers with shared sections where appropriate.
  *Why:* Churned customers need a switching journey; current customers need competitive consideration. "Not applicable" options waste LOI and produce poor data.

- **Asking CRM-available data in the survey.**
  *Wrong:* Full tenure, plan, region, and complaint questions when sample is CRM-sourced.
  *Correct:* Append from CRM; use survey for validation only.
  *Why:* Wastes 2-3 minutes of LOI and misses cross-validation opportunity.

### Methodological Mistakes

- **Overall satisfaction AFTER attribute ratings.**
  *Wrong:* Attribute matrix → then overall satisfaction.
  *Correct:* Overall satisfaction → then attribute matrix.
  *Why:* Attribute ratings anchor the overall rating, contaminating the dependent variable for derived importance analysis. See rating-scales skill.

- **Mismatched IPA rows.**
  *Wrong:* 6-row satisfaction matrix + 10-row importance matrix with different wording.
  *Correct:* Identical row count, identical concepts, matched wording in both matrices.
  *Why:* IPA requires paired importance-performance data. Mismatched rows make it impossible.

- **Missing CES.**
  *Wrong:* Only NPS and CSAT for service-driven churn.
  *Correct:* Include CES (Customer Effort Score) conditional on having contacted support.
  *Why:* CES is the strongest predictor of churn in service-driven industries. A customer who had to make 4 calls to resolve an issue may rate satisfaction as "moderate" but CES reveals the real problem.

- **Over-engineered retention offer testing.**
  *Wrong:* Full sequential monadic concept test (21 questions) for retention offers within a 15-minute churn study.
  *Correct:* Lean ranking approach (2-3 questions) as default; full monadic only when retention offers are the primary study objective.
  *Why:* 21 questions of retention offer evaluation in a 15-minute study leaves no room for the diagnostic work that makes the offers actionable.

### Measurement Mistakes

- **Defining churn attitudinally.**
  *Wrong:* "How likely are you to churn?" as the main measure.
  *Correct:* Classify based on actual cancellation or inactivity.
  *Why:* Intent does not equal behavior.

- **Asking reasons without prioritization.**
  *Wrong:* Multi-select list with no primary reason.
  *Correct:* Force a single primary reason, then allow secondary.
  *Why:* Without prioritization, all drivers look equal.

- **Missing behavioral problem incidence.**
  *Wrong:* Only satisfaction ratings and churn reasons.
  *Correct:* Include a multi-select checklist of specific problems experienced.
  *Why:* Validates satisfaction data with behavioral evidence. Enables triangulation.

- **No switching barriers for considerers-who-stayed.**
  *Wrong:* Skip competitive context for at-risk customers who didn't churn.
  *Correct:* Ask "what stopped you from switching?" for those who considered but stayed.
  *Why:* Passive barriers (hassle) vs active retention (issue resolved) are fundamentally different insights.

- **No pre-churn behavior journey for churned customers.**
  *Wrong:* Jump straight from churn reasons to retention offers.
  *Correct:* Ask what actions the customer took before switching (reported problem, researched competitors, told company they were leaving, etc.).
  *Why:* Identifies whether the company had an intervention opportunity and missed it.

- **No post-switch comparison.**
  *Wrong:* No follow-up on whether churned customers are happier with their new provider.
  *Correct:* Ask comparative satisfaction and win-back likelihood.
  *Why:* "Regrettable churn" (they're same/worse off) represents the highest win-back opportunity.

- **Privacy-violating screener wording.**
  *Wrong:* "Are you a customer who has made a complaint in the past 6 months?"
  *Correct:* "Which best describes your current [service] situation?" with neutral options.
  *Why:* Respondents feel surveilled when questions reveal the company's knowledge of their specific behavior.

---

## Quality Checklist

- [ ] Churn is defined by actual behavior, not intent alone
- [ ] Survey has separate paths for churned vs current customers (not just display_logic)
- [ ] Customer status classification uses neutral, privacy-sensitive wording
- [ ] CRM append strategy is defined (if CRM-sourced sample)
- [ ] Overall satisfaction is placed BEFORE attribute satisfaction matrix
- [ ] Satisfaction matrix rows exactly match importance matrix rows (IPA alignment)
- [ ] Behavioral problem incidence checklist is included
- [ ] Customer Effort Score (CES) is included, conditional on support contact
- [ ] NPS + mandatory verbatim follow-up included
- [ ] Primary churn reason is single-select forced choice
- [ ] Churned path includes: pre-churn behavior, retention attempt, post-switch comparison, win-back potential
- [ ] Current path includes: competitive consideration, switching barriers
- [ ] Retention offer testing uses lean ranking (default) or full monadic (if primary objective)
- [ ] Driver importance matrix uses identical rows to satisfaction matrix
- [ ] Direct priority improvement question validates driver analysis
- [ ] Context-relevant demographics included (WFH status, dwelling type)
- [ ] LOI is within target range for study type
- [ ] Outputs identify preventable vs structural churn
- [ ] Findings translate directly into retention investment decisions