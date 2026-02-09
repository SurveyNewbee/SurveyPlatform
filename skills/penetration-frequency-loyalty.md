---
name: penetration-frequency-loyalty
description: |
  Decomposes brand growth or decline into three behavioral drivers: who buys (penetration), how often they buy (frequency), and how concentrated their buying is (loyalty). Use when diagnosing brand performance changes, explaining market share differences, or identifying growth levers through actual purchase behavior rather than attitudes. Requires behavioral data with consistent recall periods and mathematically reconcilable metrics. Not suitable for early-stage concepts, attitudinal research, or categories without repeat purchase behavior.
category: market_measurement
foundational: false
primary_use_case: Diagnose why brands are growing or declining by quantifying the relative contribution of penetration, frequency, and loyalty drivers
secondary_applications:
  - Explain market share differences across competing brands
  - Identify optimal growth strategies (penetration-led vs loyalty-led)
  - Track behavioral trends over time in brand tracking studies
  - Profile customer acquisition vs retention performance
commonly_combined_with:
  - market-share-tracking
  - brand-tracking
  - market-sizing
  - segmentation
requires:
  - screening
problem_frames_solved:
  - performance_tracking
  - decline_diagnosis
decision_stages:
  - measure
  - optimize
study_types:
  - brand_tracking
  - market_share_tracking
  - customer_satisfaction
not_suitable_for:
  - Early-stage concept testing without established purchase behavior
  - Attitudinal brand research (use brand-positioning instead)
  - One-time purchase categories without repeat buying patterns
  - Studies focused on consideration or intent rather than actual behavior
---


# Penetration–Frequency–Loyalty (PFL) Analysis Methodology

## Overview

Penetration–Frequency–Loyalty (PFL) analysis is a **behavioral market measurement methodology** used to explain **why brands grow or decline** by decomposing performance into three fundamental drivers: **who buys (penetration), how often they buy (frequency), and how concentrated their buying is (loyalty)**.

This methodology prioritizes **behavioral truth, mathematical consistency, and diagnostic clarity**. Surveys must be designed so that penetration, frequency, and loyalty can be calculated cleanly and reconciled without contradiction.

---

## Core Principles

- **Behavior over attitude**
  PFL is strictly behavioral. Do not substitute intent, preference, or satisfaction for actual purchase or usage.

- **Mutually dependent metrics**
  Penetration, frequency, and loyalty are mathematically linked. Measurement error in one contaminates the others.

- **Clear population base**
  All metrics must share a common, explicitly defined category user base.

- **Time-bound measurement**
  Frequency and loyalty are only interpretable within a defined recall period aligned to purchase cycles.

- **Parsimony**
  Use the minimum number of questions required to calculate robust metrics. Over-measurement increases error.

- **Comparability**
  Identical definitions must be applied across brands, segments, and waves.

---

## Survey Design Requirements

### Question Structure

Surveys must follow this **mandatory sequence**:

1. **Category qualification**
2. **Brand penetration**
3. **Brand purchase frequency**
4. **Multi-brand usage**
5. **Primary brand identification**
6. **Spend or volume allocation (optional)**
7. **Light diagnostics (optional)**
8. **Demographics / firmographics**

#### Category Qualification
- Define the category behaviorally (e.g., “purchased \[CATEGORY] in the past 12 months”).
- Use a fixed recall window that matches normal purchase cycles.
- Disqualify non-buyers.

#### Brand Penetration
- Measure whether each brand was purchased or used at least once in the recall period.
- Use binary indicators per brand.

#### Purchase Frequency
- Measure frequency **for the category first**, then optionally by brand.
- Frequency must be numeric or ordinal and time-based.

#### Multi-Brand Usage
- Explicitly allow respondents to indicate purchasing multiple brands.
- Do not assume exclusivity unless category rules require it.

#### Primary Brand
- Identify the brand used most often or bought most recently.
- This anchors loyalty calculations when spend is unavailable.

---

### Scale Design

- **Penetration**
  - Binary per brand (Purchased / Did not purchase).
  - No agreement or likelihood scales.

- **Frequency**
  - Use ordered frequency bands or numeric entry.
  - Anchors must reflect real category behavior.

- **Loyalty**
  - Derived, not directly asked.
  - Calculated via primary brand, share of wallet, or repeat purchase.

- **Spend / Volume (optional)**
  - Percentage allocation totaling 100% or spend ranges.
  - Use only if respondents can estimate reliably.

- **Consistency rules**
  - One recall window across all PFL inputs.
  - Identical brand lists and order randomization.

---

### Sample Questions

**Category Frequency**
> About how many times have you purchased \[CATEGORY] in the past 12 months?  
> - 1 time  
> - 2–3 times  
> - 4–6 times  
> - 7–10 times  
> - More than 10 times  

**Brand Penetration**
> Which of the following brands have you purchased in the past 12 months?  
> *(Select all that apply)*  
> - Brand A  
> - Brand B  
> - Brand C  
> - Other brand  

**Primary Brand**
> Which ONE brand do you purchase most often in this category?  
> - Brand A  
> - Brand B  
> - Brand C  
> - I do not have a primary brand  

---

## Common Mistakes to Avoid

- **Using intent as penetration**
  *Wrong:* “Which brands would you consider buying?”  
  *Correct:* “Which brands have you purchased?”  
  *Why it matters:* Consideration inflates penetration.

- **Inconsistent recall windows**
  *Wrong:* Penetration over 12 months, frequency over 3 months  
  *Correct:* One coherent time frame  
  *Why it matters:* Metrics become mathematically incompatible.

- **Assuming loyalty**
  *Wrong:* Treating primary brand as exclusive usage  
  *Correct:* Explicitly capture multi-brand behavior  
  *Why it matters:* Most categories exhibit repertoire buying.

- **Directly asking loyalty**
  *Wrong:* “How loyal are you to Brand X?”  
  *Correct:* Derive loyalty from behavior  
  *Why it matters:* Self-reported loyalty is unreliable.

- **Over-segmentation**
  *Wrong:* Calculating PFL on very small subgroups  
  *Correct:* Enforce minimum base sizes  
  *Why it matters:* Small bases produce volatile metrics.

---

## Analysis & Output Requirements

The survey must enable the following calculations:

- **Penetration**
  - % of category buyers purchasing each brand
  - Primary growth driver in most categories

- **Frequency**
  - Average category purchase frequency
  - Brand-level frequency where data supports it

- **Loyalty**
  - % of buyers naming brand as primary
  - Share of wallet (if spend allocation is available)
  - Repeat purchase indicators where applicable

- **Decomposition**
  - Attribution of growth or decline to:
    - Penetration change
    - Frequency change
    - Loyalty change

- **Competitive comparison**
  - PFL profiles across brands
  - Identification of penetration-led vs. loyalty-led brands

- **Sample size guidance**
  - Minimum n=500 category buyers
  - n=800–1,000 recommended for stable brand PFL
  - Enforce n≥100 per brand for frequency analysis

- **Data structure**
  - Binary brand penetration flags
  - Ordinal or numeric frequency variables
  - Primary brand indicator
  - Optional spend allocation variables

---

## Integration with Other Methods

- **Market Share Benchmarking**
  PFL explains *why* share differs across brands.

- **Brand Tracking**
  Penetration and loyalty trends contextualize attitudinal KPIs.

- **Market Sizing**
  Frequency and penetration inputs feed bottom-up sizing.

- **Segmentation**
  PFL metrics can be profiled by segment to identify growth levers.

---

## Quality Checklist

- [ ] Category buyer base is clearly defined  
- [ ] Penetration is measured behaviorally per brand  
- [ ] Frequency uses a consistent recall window  
- [ ] Multi-brand behavior is explicitly captured  
- [ ] Loyalty is derived, not self-reported  
- [ ] Metrics reconcile mathematically  
- [ ] Sample size supports brand-level stability  
- [ ] Outputs decompose growth drivers clearly  
- [ ] Results align with known category dynamics  
- [ ] Findings are actionable for growth strategy