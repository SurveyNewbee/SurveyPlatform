---
name: choice-modeling
description: |
  Quantifies how respondents make trade-offs between product or service attributes through forced-choice experiments to model preference structures and choice behavior. Use when optimizing multi-attribute products, pricing strategies, or portfolio configurations where understanding feature-level utilities is critical. Requires 4-6 attributes with multiple levels and forces realistic trade-offs through 8-15 choice tasks per respondent. Not suitable for simple concept comparison, early-stage ideation, or studies requiring opinion-based feedback rather than behavioral modeling.
category: new_product_development
foundational: false
primary_use_case: Model preference structures and trade-offs to optimize product configuration, pricing, and portfolio decisions through revealed choice behavior
secondary_applications:
  - Market share simulation and competitive scenario modeling
  - Price sensitivity analysis and willingness-to-pay estimation
  - Feature prioritization and product roadmap planning
  - Preference-based customer segmentation
commonly_combined_with:
  - conjoint
  - pricing-study
  - segmentation
  - concept-test
requires:
  - screening
  - demographics
problem_frames_solved:
  - tradeoff_optimization
  - idea_selection
decision_stages:
  - design
  - validate
  - optimize
study_types:
  - new_product_development
  - pricing_optimization
  - portfolio_optimization
not_suitable_for:
  - Simple A/B concept testing or binary comparisons
  - Early-stage ideation without defined attributes and levels
  - Studies requiring opinion-based feedback rather than behavioral modeling
  - Brand perception or awareness measurement
---


# Choice Modeling Research Methodology

## Overview

Choice Modeling research is an **experimental survey methodology** used to quantify how respondents make trade-offs between product or service attributes when choosing among alternatives. It is designed to model **revealed preference**, not stated opinion, and is commonly used for pricing, feature optimization, portfolio design, and demand simulation.

This methodology prioritizes **realistic choice tasks, disciplined experimental design, and statistical identifiability**. Surveys must be structured to mimic actual decision-making while maintaining analytic rigor.

---

## Core Principles

- **Choice over opinion**
  Respondents must choose between options, not rate or describe them. Preference is inferred from decisions, not self-report.

- **Trade-off enforcement**
  Each task must force meaningful trade-offs. Designs that allow “everything good” options invalidate results.

- **Attribute independence**
  Attributes must be conceptually distinct and independently variable. Confounded attributes cannot be modeled.

- **Experimental balance**
  Attribute levels must be shown with sufficient variation and balance to enable stable estimation.

- **Cognitive realism**
  Choice tasks must reflect what respondents can realistically process. Over-complexity degrades data quality.

- **Model-driven design**
  Survey structure must be dictated by the intended analytical model, not by questionnaire convenience.

---

## Survey Design Requirements

### Question Structure

Surveys must follow this **mandatory structure**:

1. **Context and task framing**
2. **Attribute education**
3. **Practice choice task**
4. **Main choice tasks**
5. **Holdout or validation tasks**
6. **Optional follow-up diagnostics**
7. **Demographics**

#### Context and Task Framing
- Clearly explain the decision context respondents should imagine.
- Frame the task as a realistic choice they might actually make.
- Avoid marketing language or persuasive framing.

#### Attribute Education
- Define each attribute and level clearly before choice tasks begin.
- Use neutral, literal descriptions.
- Confirm comprehension if attributes are complex.

#### Practice Task
- Include at least one non-analytic practice task.
- Use this to teach task mechanics, not to collect data.

#### Main Choice Tasks
- Present a fixed number of choice tasks per respondent.
- Each task must include:
  - 2–4 alternatives (plus optional “none”)
  - Full attribute profiles per alternative
- Keep task format consistent throughout.

---

### Choice Task Design

- **Alternatives**
  - 2–3 alternatives recommended for most studies.
  - 4 alternatives only when categories are highly familiar.

- **None / No-choice option**
  - Include when realistic in the market.
  - Must be explicitly labeled and consistently presented.

- **Number of tasks**
  - Typically 8–15 tasks per respondent.
  - Never exceed 20 tasks.

- **Experimental design**
  - Use an efficient or fractional factorial design.
  - Ensure level balance and minimal multicollinearity.

- **Randomization**
  - Randomize task order.
  - Randomize alternative order within tasks.

---

### Scale Design

Choice modeling **does not use rating or agreement scales** for primary outcomes.

Permitted scales are limited to:

- **Forced choice**
  - “Which would you choose?” (single select)

- **Optional follow-ups**
  - Confidence in choice (5-point scale)
  - Likelihood to choose in real life (5-point scale)

Never substitute scaled preference questions for choice tasks.

---

### Sample Choice Task

> Imagine you are choosing a \[PRODUCT] for your next purchase. Which option would you choose?

|                | Option A | Option B | Option C |
|----------------|----------|----------|----------|
| Price          | $20      | $25      | $30      |
| Key Feature    | Basic    | Advanced | Advanced |
| Brand          | Brand X  | Brand Y  | Brand X  |
| Availability   | Online   | In-store | Online   |

- ☐ Option A  
- ☐ Option B  
- ☐ Option C  
- ☐ I would choose none of these  

---

## Common Mistakes to Avoid

- **Using ratings instead of choices**
  *Wrong:* “How appealing is each option?”  
  *Correct:* Force a single choice per task  
  *Why it matters:* Ratings do not produce trade-off data.

- **Too many attributes**
  *Wrong:* 8–10 attributes per option  
  *Correct:* 4–6 attributes maximum  
  *Why it matters:* Cognitive overload increases noise.

- **Dominant options**
  *Wrong:* One option is clearly best on all attributes  
  *Correct:* Ensure every option involves trade-offs  
  *Why it matters:* Dominance prevents preference estimation.

- **Inconsistent attribute levels**
  *Wrong:* Changing attribute definitions mid-survey  
  *Correct:* Lock attributes and levels across all tasks  
  *Why it matters:* Inconsistency breaks model assumptions.

- **Ignoring the “none” decision**
  *Wrong:* Forcing choice when opting out is realistic  
  *Correct:* Include a no-choice option when appropriate  
  *Why it matters:* Overstates demand if excluded.

---

## Analysis & Output Requirements

The survey must enable the following analyses:

- **Utility estimation**
  - Part-worth utilities for each attribute level
  - Relative importance of attributes

- **Preference heterogeneity**
  - Individual-level or segment-level utilities
  - Optional latent class or hierarchical models

- **Scenario simulation**
  - Market share predictions for hypothetical offerings
  - Price sensitivity and feature trade-offs

- **Model validation**
  - Holdout task hit rates
  - Predictive accuracy checks

- **Sample size guidance**
  - Minimum n=200 for simple designs
  - n=300–500 recommended for segmentation or pricing
  - Ensure enough observations per parameter

- **Data structure**
  - One record per respondent per task
  - Explicit task and alternative IDs
  - Binary choice indicators

---

## Integration with Other Methods

- **Conjoint Analysis**
  Choice modeling is often implemented as choice-based conjoint; principles apply directly.

- **Pricing Studies**
  Choice models provide elasticities and willingness-to-pay when price is included.

- **Segmentation**
  Utilities can be used as inputs for needs- or value-based segmentation.

- **Concept Testing**
  Concepts can be decomposed into attributes for deeper optimization.

---

## Quality Checklist

- [ ] Respondents make forced choices between full profiles  
- [ ] Attributes and levels are clearly defined and independent  
- [ ] Choice tasks enforce real trade-offs  
- [ ] Number of tasks is cognitively manageable  
- [ ] Experimental design supports parameter estimation  
- [ ] “None” option is included when realistic  
- [ ] Task and alternative order are randomized  
- [ ] Data structure supports utility modeling  
- [ ] Holdout tasks are included for validation  
- [ ] Outputs enable simulation and decision-making