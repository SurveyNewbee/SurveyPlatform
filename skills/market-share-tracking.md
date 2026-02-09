---
name: market-share-tracking
description: |
  Measures and monitors competitive brand share over time using consistent survey-based behavioral indicators to track market position changes. Use when transactional data is unavailable, incomplete, or needs contextualization with brand and behavioral drivers across multiple measurement periods. Requires fixed methodology and category definitions to ensure trend integrity and change detection capability. Not suitable for one-time competitive assessments or early-stage markets without established purchase patterns.
category: market_measurement
foundational: false
primary_use_case: Monitor competitive market position changes over time to understand share gains/losses and underlying behavioral drivers
secondary_applications:
  - Validate marketing campaign effectiveness through share movement
  - Identify switching patterns and competitive threats
  - Support portfolio optimization decisions with share trend data
  - Benchmark performance against category growth or decline
commonly_combined_with:
  - brand-tracking
  - penetration-frequency-loyalty
  - market-sizing
  - customer-lifecycle
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
  - competitive_intelligence
  - performance_measurement
not_suitable_for:
  - One-time competitive snapshots (use market-share-benchmarking instead)
  - Early-stage markets without established purchase patterns
  - Categories where behavior changes too rapidly for survey tracking
---


# Market Share Tracking (Ongoing Competitive Share Measurement)

## Overview
Market Share Tracking is a longitudinal research methodology used to **measure, monitor, and explain changes in competitive share over time** using survey-based indicators. It is applied when transactional data is incomplete, delayed, inaccessible, or needs to be contextualized with brand, category, and behavioral drivers.

This methodology prioritizes **trend integrity, competitive comparability, and diagnostic depth**, enabling stakeholders to understand not just who is winning or losing share, but **why**.

## Core Principles
- **Consistency beats precision.** Trend stability is more important than single-wave accuracy.
- **Define the market once and protect it.** Category, competitors, and eligibility rules must remain fixed.
- **Anchor share to behavior, not attitudes.** Share must be derived from reported purchase or usage, not preference.
- **Separate incidence from allocation.** Category participation and brand choice are distinct analytical steps.
- **Design for change detection.** Small shifts must be distinguishable from noise.
- **Avoid false certainty.** Survey-based share is directional and must be framed appropriately.

## Survey Design Requirements

### Question Structure
- **Always start with category qualification.**
  - Confirm recent purchase, usage, or ownership within a defined time window.
- **Define a clear reference period.**
  - Example: “In the past 4 weeks” or “Your most recent purchase”
- **Use a two-step structure for share derivation:**
  1. Category incidence (who participated)
  2. Brand allocation (what they chose)
- **For multi-brand usage categories, allow multiple selections with allocation rules.**
  - Example: primary brand vs secondary brands
- **For single-purchase categories, force a single choice.**
- **Include an explicit “other brand” option.**
  - Follow with open-ended brand capture.
- **Do not rotate brand lists across waves.**
  - Brand order must remain fixed unless a new competitor is formally added.
- **If measuring value share, collect spend or price proxies.**
  - Unit volume alone is insufficient.

### Scale Design
- **Market share questions are categorical, not scaled.**
  - Avoid rating scales for share derivation.
- **When collecting frequency or spend, use bounded numeric ranges.**
  - Example: “1 time”, “2–3 times”, “4+ times”
- **Maintain identical response options across waves.**
- **Avoid “don’t know” options for core share questions.**
  - Respondents must recall their own behavior.
- **Use separate scales for diagnostic drivers.**
  - Do not conflate share measurement with explanation.

### Sample Questions
**Category Qualification**
- “Which of the following categories have you purchased in the past 30 days?”
  - [Target category] (continue)
  - None of the above (terminate)

**Brand Allocation (Single Choice)**
- “Which brand did you purchase most recently in this category?”
  - Brand A
  - Brand B
  - Brand C
  - Other (please specify)

**Multi-Brand Usage**
- “Which of the following brands have you used in this category in the past 30 days?”
  - Select all that apply
- “Which ONE of these do you consider your primary brand?”

**Value Proxy**
- “Approximately how much did you spend on this category in the past 30 days?”

## Common Mistakes to Avoid
- **Changing the category definition mid-tracking.**
  - *Wrong:* Expanding from “premium” to “all” without resetting trends.
  - *Correct:* Start a new trend series when scope changes.
- **Mixing awareness or preference with share.**
  - Share must be behavior-based.
- **Overloading the core share question.**
  - Diagnostics come after allocation, not during.
- **Allowing brand list drift.**
  - Removing or renaming brands breaks comparability.
- **Ignoring small competitors.**
  - “Other” must be actively monitored and coded.
- **Reporting share without incidence context.**
  - Share of buyers ≠ share of population.

## Analysis & Output Requirements
- **Primary outputs must include:**
  - Category incidence rate
  - Share of buyers by brand
  - Share of usage or value (if available)
  - Trend lines over time
- **Report confidence intervals or stability indicators.**
  - Especially for smaller brands.
- **Decompose share change drivers where possible:**
  - Incidence change
  - Switching behavior
  - Usage intensity
- **Sample size guidance:**
  - Minimum 400–600 category users per wave
  - Larger samples for fragmented markets
- **Weighting rules must be fixed and documented.**
  - Never reweight historical waves retroactively without restatement.
- **Segment reporting is mandatory.**
  - At minimum by key demographics or customer type.
- **Flag statistically insignificant movement.**
  - Avoid over-interpreting noise.

## Integration with Other Methods
- **Brand Tracking:** Use brand metrics to explain share movement.
- **Penetration–Frequency–Loyalty:** Decompose share into behavioral components.
- **Win–Loss Studies:** Qualitatively diagnose switching behavior.
- **Customer Lifecycle Research:** Understand which stages are gaining or losing share.
- **Market Sizing:** Convert share trends into revenue implications.

## Quality Checklist
- [ ] Category definition and reference period are fixed and explicit
- [ ] Share is derived from reported behavior, not attitudes
- [ ] Brand lists are stable and comprehensive
- [ ] Incidence and allocation are measured separately
- [ ] Sample size supports trend detection
- [ ] Weighting and methodology are documented and consistent
- [ ] Outputs distinguish real change from noise
- [ ] Results enable explanation, not just reporting