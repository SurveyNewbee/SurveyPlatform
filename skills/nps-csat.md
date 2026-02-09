---
name: nps-csat
description: |
  Measures customer loyalty (NPS) and satisfaction (CSAT) using standardized metrics to track relationship health and experience quality. Use when establishing ongoing measurement programs to monitor customer sentiment trends, benchmark performance, or diagnose experience breakdowns. Most effective as continuous tracking systems rather than one-off measurements, requiring strict adherence to standard wording and scales for comparability. Not suitable for concept testing, feature evaluation, or studies requiring customized satisfaction dimensions.
category: customer_satisfaction
foundational: false
primary_use_case: Monitor customer loyalty and satisfaction trends through standardized metrics that enable benchmarking and performance tracking
secondary_applications:
  - Diagnose specific touchpoint or interaction performance
  - Identify at-risk customer segments (Passives and Detractors)
  - Support executive KPI dashboards and reporting
  - Trigger closed-loop feedback and recovery programs
commonly_combined_with:
  - journey-mapping
  - customer-lifecycle
  - churn-retention
  - voc-programs
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - performance_tracking
  - decline_diagnosis
  - experience_breakdown
decision_stages:
  - measure
  - optimize
study_types:
  - customer_satisfaction
  - user_experience
  - performance_tracking
not_suitable_for:
  - Concept testing or product feature evaluation (use concept-test instead)
  - One-off satisfaction studies without trend comparison needs
  - Studies requiring customized satisfaction dimensions or non-standard scales
  - Brand perception or awareness measurement (use brand-tracking instead)
---


# NPS & CSAT

## Overview
NPS (Net Promoter Score) and CSAT (Customer Satisfaction) are standardized metrics used to measure customer sentiment, loyalty, and experience quality. They are most powerful when implemented as **ongoing measurement programs**, not one-off questions. Correct execution depends on strict adherence to wording, scales, and follow-up structure.

## Core Principles
NPS and CSAT are deceptively simple and frequently misused. Always follow these principles:

- **Standardization over customization:** Comparability matters more than creativity.
- **Context clarity:** Metrics must clearly reflect either a relationship or a specific interaction.
- **Closed-loop learning:** Scores alone are useless without diagnostic follow-up.
- **Trend integrity:** Changes in wording, scale, or placement invalidate comparisons.
- **Action orientation:** Every metric must map to an improvement lever.

## Survey Design Requirements

### Metric Selection

#### Net Promoter Score (NPS)
Use NPS when:
- You need a standardized loyalty benchmark
- Comparability across time, brands, or industries matters
- Advocacy and word-of-mouth are strategic goals

Do not use NPS as a general satisfaction metric.

---

#### Customer Satisfaction (CSAT)
Use CSAT when:
- Evaluating specific interactions or touchpoints
- Measuring short-term experience quality
- Diagnosing operational performance

Do not compare CSAT scores directly to NPS.

---

### Relationship vs Transactional Context

#### Relationship NPS
Measures overall brand or company relationship.

**Use when:**
- Tracking loyalty over time
- Evaluating brand health
- Supporting executive KPIs

---

#### Transactional NPS / CSAT
Measures a **specific recent interaction**.

**Use when:**
- Diagnosing service performance
- Evaluating specific journeys or touchpoints
- Driving operational improvements

Never mix relationship and transactional metrics in the same score.

---

### Question Structure

#### NPS Question (Must Be Exact)

Always use this wording:

```

How likely are you to recommend [COMPANY / BRAND] to a friend or colleague?

```

Scale:
- 0 = Not at all likely
- 10 = Extremely likely

Rules:
- Do not change the wording
- Do not change the scale
- Always show numeric anchors
- Always place the question early in the survey

---

#### NPS Classification
- **Promoters:** 9–10
- **Passives:** 7–8
- **Detractors:** 0–6

NPS = % Promoters − % Detractors

Never redefine these thresholds.

---

#### CSAT Question Structure

Standard format:
```

Overall, how satisfied were you with [EXPERIENCE]?

```

Recommended scale:
- Very satisfied
- Somewhat satisfied
- Neither satisfied nor dissatisfied
- Somewhat dissatisfied
- Very dissatisfied

Alternative (acceptable):
- 1–5 satisfaction scale with labeled endpoints

Do not use 0–10 scales for CSAT.

---

### Follow-Up Diagnostics (Mandatory)

#### NPS Follow-Up
Immediately follow NPS with an open-end:

```

What is the primary reason for the score you just gave?

```

Rules:
- Open-ended
- Unprompted
- Mandatory

Never skip the NPS verbatim.

---

#### CSAT Diagnostics
Use structured follow-ups:

```

Which of the following most influenced your satisfaction?

```

Include drivers such as:
- Ease of use
- Speed
- Staff interaction
- Product quality
- Value for money

Follow with an open-end for detail.

---

### Scale Design

Rules:
- Do not mix scales within the same metric
- Label all scale points
- Keep polarity consistent across waves
- Maintain identical formatting across surveys

Never:
- Use emojis instead of numbers
- Collapse scales post-field
- Recode scales differently by wave

---

### Sample Questions

#### NPS Example
```

How likely are you to recommend [Brand] to a friend or colleague?

0 1 2 3 4 5 6 7 8 9 10
Not at all likely — Extremely likely

```

#### NPS Follow-Up
```

What is the main reason you gave that score?

```

---

#### CSAT Example
```

Overall, how satisfied were you with your most recent support interaction?

* Very satisfied
* Somewhat satisfied
* Neither satisfied nor dissatisfied
* Somewhat dissatisfied
* Very dissatisfied

```

---

## Common Mistakes to Avoid

### Mistake 1: Rewording the NPS Question
**Wrong:**  
“How likely are you to tell others about us?”

**Why it’s wrong:**  
Breaks comparability with NPS benchmarks.

**Correct approach:**  
Use the exact standard wording.

---

### Mistake 2: Asking “Why” Before the Score
**Wrong:**  
“Why would you recommend us?”

**Why it’s wrong:**  
Biases the numeric rating.

**Correct approach:**  
Always collect the score first, then diagnose.

---

### Mistake 3: Treating Passives as Neutral
**Wrong:**  
Ignoring Passives in analysis.

**Why it’s wrong:**  
Passives are at risk and easily lost.

**Correct approach:**  
Analyze Passives separately and identify conversion opportunities.

---

### Mistake 4: Averaging NPS Scores
**Wrong:**  
Reporting a mean NPS score.

**Why it’s wrong:**  
NPS is not an average-based metric.

**Correct approach:**  
Always report NPS as Promoters − Detractors.

---

## Analysis & Output Requirements

### Required Data Structure
Each record must include:
- Raw NPS or CSAT score
- Promoter/Passive/Detractor flag (for NPS)
- Verbatim response
- Interaction type (if transactional)
- Date / wave identifier

Never store only the calculated NPS score.

---

### Core Outputs

#### NPS Reporting
Always include:
- NPS score
- % Promoters, % Passives, % Detractors
- Trend over time
- Verbatim themes by group

---

#### CSAT Reporting
Always include:
- % satisfied (top-2 box)
- Mean satisfaction (if used)
- Driver importance
- Key dissatisfaction drivers

---

### Segmentation & Filtering
Analyze NPS/CSAT by:
- Customer tenure
- Product or service line
- Channel or touchpoint
- Key demographic or behavioral segments

Avoid over-segmentation that leads to unstable results.

---

## Integration with Other Methods

NPS and CSAT integrate with:
- **Journey mapping:** Identify where loyalty breaks down
- **Usability testing:** Link friction to satisfaction
- **Brand tracking:** Connect loyalty to brand health
- **Win-loss analysis:** Understand defection drivers

Use NPS as a signal, not a diagnosis.

---

## Quality Checklist

- [ ] NPS wording and scale are exact
- [ ] Metric context (relationship vs transactional) is clear
- [ ] Follow-up diagnostics are included
- [ ] Scores are stored at the respondent level
- [ ] Trends are interpreted cautiously
- [ ] Passives are analyzed explicitly
- [ ] Results link to action plans
- [ ] Governance prevents metric drift

---

## Final Guidance
NPS and CSAT are **management systems**, not just questions. Their value depends entirely on consistency, discipline, and follow-through. Protect the integrity of the metric, close the loop on feedback, and treat scores as leading indicators—not answers in themselves.
```

---
