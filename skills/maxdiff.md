---
name: maxdiff
description: |
  Measures relative importance and preference rankings through best-worst scaling choice tasks, forcing trade-offs between 4-5 items per task to eliminate scale bias. Use when you need clear prioritization among 10-40 attributes and rating scales produce flat or inflated results due to scale compression. Commonly paired with concept-test (prioritize features before testing) or conjoint (narrow attribute lists before design). Not suitable for interdependent items, absolute willingness-to-pay measurement, or complete product bundle evaluation.
category: new_product_development
foundational: false
primary_use_case: Determine clear priority rankings among multiple attributes or features when rating scales fail to discriminate
secondary_applications:
  - Feature prioritization for product roadmaps
  - Message or claims prioritization before creative development
  - Attribute reduction for conjoint analysis design
  - Preference-based input for segmentation analysis
commonly_combined_with:
  - concept-test
  - conjoint
  - segmentation
  - message-test
requires:
  - screening
problem_frames_solved:
  - tradeoff_optimization
  - idea_selection
decision_stages:
  - define
  - design
  - validate
study_types:
  - new_product_development
  - advertising_communications
  - brand_strategy
not_suitable_for:
  - Studies with fewer than 10 items to prioritize (use rating-scales instead)
  - Measuring absolute willingness-to-pay or price sensitivity (use conjoint or pricing-study)
  - Evaluating complete product bundles or interdependent features
---


# MaxDiff (Best–Worst Scaling)

## Overview
MaxDiff (Maximum Difference Scaling), also called Best–Worst Scaling, is a choice-based methodology used to measure the relative importance or preference of a list of items. Respondents repeatedly choose the **most important** and **least important** (or best and worst) items from small sets, producing discriminating, scale-free importance scores. Use MaxDiff when you need **clear prioritization** among many attributes and rating scales or rankings fail due to scale bias or respondent fatigue.

## Core Principles
MaxDiff differs fundamentally from rating and ranking approaches. Always adhere to these principles:

- **Forced trade-offs:** Respondents must choose one “best” and one “worst” item per task, eliminating scale inflation and satisficing.
- **Small, repeated sets:** Items are shown in subsets (typically 4–5 items), repeated across tasks using an experimental design.
- **Balanced exposure:** Each item must appear approximately the same number of times and with varied competitors to allow unbiased estimation.
- **Relative measurement:** Outputs are relative importance scores, not absolute ratings. Interpret results comparatively, not independently.
- **Choice-based estimation:** Analysis relies on multinomial logit or hierarchical Bayes models, not simple averages.

## Survey Design Requirements

### Question Structure

#### Set Size and Task Design
Always follow these rules:

- **Use 4 or 5 items per task.**  
  - 3 items provide insufficient discrimination.  
  - More than 5 increases cognitive load and reduces data quality.
- **Include exactly one “Most” and one “Least” selection per task.**
- **Present items as a simple list, not a grid.**
- **Use consistent phrasing and grammatical structure across all items.**
- **Avoid double-barreled or compound items.**

**Standard instruction text (recommended):**
> “From the list below, please select the option that is **MOST important** to you and the option that is **LEAST important** to you.”

#### Number of Tasks
- **8–12 tasks per respondent** is standard for 12–30 total items.
- Never exceed **15 tasks per respondent**.
- If the item list is long (>30 items), split into blocks and use larger samples per block.

#### Experimental Design
MaxDiff requires a **balanced incomplete block design (BIBD)** or equivalent algorithmic design.

Design requirements:
- Each item appears **the same number of times** (±1).
- Each item appears with **different combinations of other items**.
- No item appears more than once in the same task.
- Position of items within tasks is randomized.

Never manually construct MaxDiff sets without a design engine. Always use a MaxDiff-capable survey platform or external design generator.

---

### Scale Design
MaxDiff does **not** use numeric rating scales. The scale is implicit and derived from choices.

However, you must:
- Use **binary selections** (Most / Least).
- Avoid adding intensity qualifiers (e.g., “Very most important”).
- Avoid neutral or “none” options. MaxDiff requires forced choice.

---

### Sample Questions

#### Correct MaxDiff Task Example

```

Which of the following features is MOST important to you when choosing a streaming service, and which is LEAST important?

[ ] Exclusive original content
[ ] Monthly subscription price
[ ] Ability to download shows for offline viewing
[ ] Number of simultaneous streams allowed

MOST important:  (select one)
LEAST important: (select one)

```

#### Incorrect Formats (Do NOT Use)
- Asking respondents to **rank all items** in the set
- Using a **1–5 importance scale**
- Allowing respondents to select **multiple “most” items**
- Adding a “Not applicable” option

---

## Common Mistakes to Avoid

### Mistake 1: Treating MaxDiff Like Rating Scales
**Wrong:**  
“Please rate how important each feature is on a 1–7 scale.”

**Why it’s wrong:**  
Rating scales suffer from scale compression, cultural bias, and lack of discrimination. MaxDiff exists to eliminate these issues.

**Correct approach:**  
Use forced best–worst choices only. Do not mix MaxDiff with ratings in the same task.

---

### Mistake 2: Using Unequal or Poorly Written Items
**Wrong:**  
- “Low price”  
- “Customer service and support availability”  

**Why it’s wrong:**  
Items differ in specificity and cognitive weight, biasing results.

**Correct approach:**  
Write all items at the same level of abstraction and length:
- “Low monthly price”
- “Access to live customer support”

---

### Mistake 3: Too Many Items Without Blocking
**Wrong:**  
Running 40 items in a single MaxDiff with 10 tasks per respondent.

**Why it’s wrong:**  
Items will appear too infrequently for stable estimation.

**Correct approach:**  
Block the design or reduce the item list. Aim for **3–5 appearances per item per respondent** across the sample.

---

### Mistake 4: Interpreting Raw Counts as Final Results
**Wrong:**  
Reporting “times chosen as most important” as the primary metric.

**Why it’s wrong:**  
Raw counts ignore competitive context and least selections.

**Correct approach:**  
Estimate utilities using appropriate MaxDiff models (HB or MNL) and report relative importance scores.

---

## Analysis & Output Requirements

### Required Data Structure
Each task must capture:
- Task ID
- Item IDs shown
- Item selected as “Most”
- Item selected as “Least”

Do not store MaxDiff data as a grid. Each task is a discrete choice observation.

### Statistical Requirements
- Use **Hierarchical Bayes (HB)** for individual-level utilities (preferred).
- Use **Multinomial Logit (MNL)** for aggregate-only studies.
- Minimum sample size:
  - **150–200 respondents** for aggregate results
  - **300+ respondents** for stable segmentation or subgroup analysis

### Common Output Metrics
Always include:
- Relative importance scores (scaled to sum to 100 or range 0–1)
- Rank order of items
- Confidence intervals or standard errors
- Segment-level utilities (if segmentation is applied)

Avoid reporting:
- Absolute “importance” without comparison
- Percent choosing “most” only
- Mean scores (not applicable)

---

## Integration with Other Methods

MaxDiff is frequently combined with:
- **Concept testing:** Use MaxDiff to prioritize features before concept exposure.
- **Conjoint analysis:** Use MaxDiff to narrow attribute lists before conjoint design.
- **Segmentation:** Use individual-level MaxDiff utilities as inputs for clustering.
- **Message testing:** Prioritize claims or messages using MaxDiff before deep diagnostics.

Never replace conjoint with MaxDiff when price trade-offs or full product configurations are required. MaxDiff measures **importance**, not **choice simulation**.

---

## When to Use MaxDiff vs Alternatives

Use MaxDiff when:
- You have **10–40 items** to prioritize
- Rating scales produce flat or inflated results
- Clear prioritization is required for decision-making

Do NOT use MaxDiff when:
- Items are highly interdependent
- You need absolute willingness-to-pay
- Respondents must evaluate complete product bundles

---

## Quality Checklist

- [ ] Items are mutually exclusive, clearly written, and equally specific
- [ ] Each task includes exactly 4–5 items
- [ ] Each task requires one “Most” and one “Least” selection
- [ ] Items are rotated using a balanced experimental design
- [ ] Respondents complete no more than 12–15 tasks
- [ ] No rating scales or rankings are mixed into MaxDiff tasks
- [ ] Analysis plan includes appropriate MaxDiff modeling
- [ ] Outputs are reported as relative importance, not raw counts

---

## Final Guidance
MaxDiff is powerful precisely because it is **constrained**. Never relax its rules for convenience. If the design feels rigid, that is a feature—not a flaw. Properly executed, MaxDiff delivers some of the clearest prioritization data available in survey research.
