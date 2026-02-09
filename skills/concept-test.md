---
name: concept-test
description: |
  Evaluates new product ideas, messaging, or positioning through monadic, sequential monadic, or proto-monadic designs to measure appeal, purchase intent, uniqueness, and believability. Use when comparing 2-6 product concepts before development investment to identify strongest options and understand appeal drivers. Commonly combined with pricing-study for price sensitivity or segmentation to identify preference-based segments. Not suitable for feature-level optimization, early ideation without defined concepts, or testing more than 6 concepts due to fatigue effects.
category: new_product_development
foundational: false
primary_use_case: Identify which product concepts have strongest market appeal and purchase intent before development investment
secondary_applications:
  - Message and positioning testing for marketing campaigns
  - Service concept evaluation and refinement
  - Portfolio concept screening and prioritization
  - Concept optimization through diagnostic feedback
commonly_combined_with:
  - pricing-study
  - segmentation
  - conjoint
  - market-sizing
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - idea_selection
  - launch_risk
decision_stages:
  - define
  - design
  - validate
study_types:
  - new_product_development
  - messaging_positioning
not_suitable_for:
  - Feature-level optimization (use conjoint instead)
  - Early ideation without defined concepts
  - Testing more than 6 concepts due to respondent fatigue
  - Brand perception or awareness measurement
---


# Concept Testing Survey Design

## Overview
Concept tests evaluate new product ideas, messaging, or positioning before significant investment in development. The goal is to identify which concepts have the strongest appeal and understand why.

## Test Design Types

### 1. Monadic Design
**Each respondent sees ONE concept only**

**When to use**:
- Need absolute measures (not just relative rankings)
- Testing 2-4 concepts
- Budget allows larger sample (need n per concept)
- Want unbiased reactions to each concept

**Advantages**:
- No order bias or fatigue
- Clean read on each concept independently
- Best for predicting real-world performance

**Disadvantages**:
- Expensive (need separate sample for each concept)
- Can't measure direct preference between concepts

### 2. Sequential Monadic Design
**Each respondent sees ALL concepts, one at a time**

**When to use**:
- Testing 2-3 concepts (maximum 4)
- Need both absolute measures AND relative preferences
- Want cost efficiency vs pure monadic
- Concepts are similar enough for comparison

**Advantages**:
- Get both absolute and relative measures
- More cost-efficient than monadic
- Can ask direct preference question

**Disadvantages**:
- Order bias (first concept often scores higher)
- Fatigue effects if too many concepts
- Slightly lower scores than monadic due to comparison

**Required**: Rotate concept order across respondents

### 3. Proto-Monadic Design
**Show ALL concepts simultaneously, then rate individually**

**When to use**:
- Testing 3-6 concepts
- Budget constraints (most efficient)
- Concepts need to be compared in competitive set
- Ranking/choice between concepts is key output

**Advantages**:
- Most cost-efficient
- Simulates competitive marketplace
- Natural for ranking exercises

**Disadvantages**:
- No standalone absolute measures
- High comparison bias
- Not suitable for predicting absolute performance

---

## Survey Section Structure

### Section Structure by Design Type

#### Sequential Monadic
- Create ONE SUBSECTION PER CONCEPT, each containing the identical evaluation battery
- Name subsections after the actual concept/product name (e.g., "FreshBrew Decaf Blend Evaluation")
- Use subsection_ids that indicate concept identity (e.g., MS5_A, MS5_B, MS5_C)
- After all concept subsections, add a COMPARISON SUBSECTION
- FLOW defines randomized rotation orders and balanced assignment

Example for 3 concepts:
```
MS5_A: "FreshBrew Decaf Blend Evaluation"
  - stimulus_display (artefact A1)
  - Appeal scale
  - Purchase intent scale
  - Relevance scale
  - Uniqueness scale
  - Believability scale
  - Open-ended: likes
  - Open-ended: dislikes

MS5_B: "FreshBrew Ethiopian Evaluation"
  - stimulus_display (artefact A2)
  - [identical battery]

MS5_C: "FreshBrew Instant Sachets Evaluation"
  - stimulus_display (artefact A3)
  - [identical battery]

MS6: "Concept Comparison"
  - Overall preference (single_choice with concept names)
  - Preference rationale (open_ended)
  - Improvement suggestions (open_ended)
  - Rejection rationale for "None of these" selectors (open_ended, conditional)
```

#### Monadic
- Create ONE concept evaluation subsection
- FLOW assigns each respondent to exactly one concept cell
- stimulus_display references the assigned artefact
- No comparison subsection

#### Proto-Monadic
- Structure like sequential monadic but:
  - First concept gets full evaluation battery
  - Second concept gets abbreviated battery (appeal, PI, uniqueness only)
  - FLOW assigns each respondent to 2 of N concepts

**CRITICAL**: Never put multiple concept evaluations in a single flat subsection with
interleaved questions. Each concept MUST be its own subsection for clean rotation,
independent analysis, and clear audit trail.

---

## Concept Presentation

Use `stimulus_display` question type to show concepts. NEVER use `open_ended` for
concept exposure — respondents should not see a text input box when reading a concept.

```json
{
  "question_id": "MS5_A_Q1",
  "question_text": "Please read the following product concept carefully. Take your time to review all the details before continuing.",
  "question_type": "stimulus_display",
  "options": [],
  "rows": null,
  "columns": null,
  "displays_artefact": "A1",
  "required": true,
  "notes": "Concept exposure. Minimum 10 seconds display before continue button activates."
}
```

---

## Standard Evaluation Battery

Every concept MUST be measured on these five metrics using IDENTICAL scales across
all concepts. This is the minimum viable battery — skills or briefs may add more.

### Scale Direction Rule
All concept evaluation scales run **positive-to-negative** (high end first).
This is the industry standard for concept testing and matches established benchmarks.

### 1. Overall Appeal
```json
{
  "question_id": "MS5_A_Q2",
  "question_text": "Overall, how appealing is this product concept to you?",
  "question_type": "scale",
  "options": [
    "Extremely appealing",
    "Very appealing",
    "Moderately appealing",
    "Slightly appealing",
    "Not at all appealing"
  ],
  "notes": "T2B = Extremely + Very appealing."
}
```

### 2. Purchase Intent
Use the **standard 5-point purchase intent scale** with benchmark-compatible wording.
Do NOT use a likelihood scale ("Extremely likely" / "Very likely") — this is a different
construct with different norms.

```json
{
  "question_id": "MS5_A_Q3",
  "question_text": "How likely would you be to purchase this product if it were available?",
  "question_type": "scale",
  "options": [
    "Definitely would purchase",
    "Probably would purchase",
    "Might or might not purchase",
    "Probably would not purchase",
    "Definitely would not purchase"
  ],
  "notes": "T2B = Definitely + Probably would purchase. Industry-standard PI scale."
}
```

### 3. Relevance
```json
{
  "question_id": "MS5_A_Q4",
  "question_text": "How relevant is this product to your needs?",
  "question_type": "scale",
  "options": [
    "Extremely relevant",
    "Very relevant",
    "Moderately relevant",
    "Slightly relevant",
    "Not at all relevant"
  ],
  "notes": "T2B = Extremely + Very relevant."
}
```

### 4. Uniqueness / Differentiation
```json
{
  "question_id": "MS5_A_Q5",
  "question_text": "How different is this product from other products currently available?",
  "question_type": "scale",
  "options": [
    "Extremely different",
    "Very different",
    "Moderately different",
    "Slightly different",
    "Not at all different"
  ],
  "notes": "T2B = Extremely + Very different."
}
```

### 5. Believability
```json
{
  "question_id": "MS5_A_Q6",
  "question_text": "How believable are the claims made in this product concept?",
  "question_type": "scale",
  "options": [
    "Extremely believable",
    "Very believable",
    "Moderately believable",
    "Slightly believable",
    "Not at all believable"
  ],
  "notes": "T2B = Extremely + Very believable."
}
```

---

## Per-Concept Open-Ended Feedback (REQUIRED)

Every concept evaluation subsection MUST include open-ended likes and dislikes.
These are essential for understanding WHY each concept scored as it did and for
providing actionable optimization guidance. Do NOT skip these.

```json
{
  "question_id": "MS5_A_Q7",
  "question_text": "What do you like most about this product concept?",
  "question_type": "open_ended",
  "options": [],
  "required": true,
  "notes": "Minimum 10 characters. Code to themes during analysis."
},
{
  "question_id": "MS5_A_Q8",
  "question_text": "What, if anything, do you dislike about this product concept?",
  "question_type": "open_ended",
  "options": [],
  "required": false,
  "notes": "Optional response — some respondents may have no dislikes."
}
```

---

## Comparative Questions (Sequential / Proto-Monadic Only)

After all concepts have been shown and rated individually, add a comparison subsection.

### Overall Preference
Use actual concept names with brief descriptors — NEVER use generic "Concept A / B / C".

```json
{
  "question_id": "MS6_Q1",
  "question_text": "Now that you have seen all the product concepts, which ONE would you be most likely to purchase?",
  "question_type": "single_choice",
  "options": [
    "FreshBrew Decaf Blend — The Swiss Water Process decaf",
    "FreshBrew Single Origin Ethiopian — The Yirgacheffe single origin",
    "FreshBrew Instant Sachets — The premium instant sachets",
    "None of these — I would not purchase any of them"
  ],
  "notes": "Randomize first three options. Always include 'None of these' escape."
}
```

### Preference Rationale
```json
{
  "question_id": "MS6_Q2",
  "question_text": "Why did you choose this concept as your preferred option? Please explain in your own words.",
  "question_type": "open_ended",
  "display_logic": "Show if MS6_Q1 is not 'None of these'",
  "required": true,
  "notes": "Minimum 10 characters."
},
{
  "question_id": "MS6_Q3",
  "question_text": "What, if anything, would make your preferred concept even more appealing to you?",
  "question_type": "open_ended",
  "display_logic": "Show if MS6_Q1 is not 'None of these'",
  "required": false
}
```

### Rejection Rationale
```json
{
  "question_id": "MS6_Q4",
  "question_text": "You indicated you would not purchase any of these concepts. Please tell us why none of these products appealed to you.",
  "question_type": "open_ended",
  "display_logic": "Show only if MS6_Q1 = 'None of these'",
  "required": true,
  "notes": "Critical for understanding category barriers."
}
```

---

## Price Sensitivity (Optional — Per Concept or Preferred Only)

When pricing is a secondary objective (not the primary study focus), use Van Westendorp
questions. For rigorous pricing optimization, combine with the pricing-study skill.

### Application Rule
- **Preferred concept only** (recommended): Ask VW questions only for the concept selected
  in the preference question. Skip if respondent selected "None of these." This minimizes
  respondent burden and is sufficient for directional pricing guidance.
- **All concepts** (use only if brief explicitly requires it): Ask VW for each concept
  within its evaluation subsection. Only do this for 2 concepts maximum — 3+ creates
  unacceptable fatigue (12+ pricing questions).

### Question Format
Use `numeric_input` type — NEVER use `open_ended` for price questions.
Respondents must enter a number, not free text.

### Question Order
Follow the standard Van Westendorp sequence. Start from the top (too expensive) and
work down. This anchors respondents at the upper end first, producing more reliable
price sensitivity curves.

```json
{
  "question_id": "MS7_Q1",
  "question_text": "Thinking about [PIPE CONCEPT NAME], at what price would you consider this product to be so expensive that you would not consider buying it?",
  "question_type": "numeric_input",
  "options": [],
  "piping": "Pipe in concept name from MS6_Q1",
  "display_logic": "Show only if MS6_Q1 is not 'None of these'",
  "required": true,
  "notes": "Van Westendorp: Too expensive. Format: $X.XX. Min: 0, Max: 100."
},
{
  "question_id": "MS7_Q2",
  "question_text": "At what price would you consider [PIPE CONCEPT NAME] to be starting to get expensive, but you would still consider buying it?",
  "question_type": "numeric_input",
  "options": [],
  "piping": "Pipe in concept name from MS6_Q1",
  "display_logic": "Show only if MS6_Q1 is not 'None of these'",
  "required": true,
  "notes": "Van Westendorp: Expensive. Must be <= MS7_Q1."
},
{
  "question_id": "MS7_Q3",
  "question_text": "At what price would you consider [PIPE CONCEPT NAME] to be a bargain — a great buy for the money?",
  "question_type": "numeric_input",
  "options": [],
  "piping": "Pipe in concept name from MS6_Q1",
  "display_logic": "Show only if MS6_Q1 is not 'None of these'",
  "required": true,
  "notes": "Van Westendorp: Bargain. Must be <= MS7_Q2."
},
{
  "question_id": "MS7_Q4",
  "question_text": "At what price would you consider [PIPE CONCEPT NAME] to be so inexpensive that you would question its quality?",
  "question_type": "numeric_input",
  "options": [],
  "piping": "Pipe in concept name from MS6_Q1",
  "display_logic": "Show only if MS6_Q1 is not 'None of these'",
  "required": true,
  "notes": "Van Westendorp: Too cheap. Must be <= MS7_Q3. Validate full chain: Q4 <= Q3 <= Q2 <= Q1."
}
```

### Pricing Validation
Add a FLOW routing rule enforcing logical consistency:
```
Too cheap (Q4) <= Bargain (Q3) <= Expensive (Q2) <= Too expensive (Q1)
If validation fails, prompt respondent to review and correct.
```

---

## Critical Design Rules

### 1. Concept Quality
- Concepts must be equally developed (same level of detail)
- Use neutral language — avoid bias in descriptions
- Include enough detail to be realistic but not overwhelming
- Use visuals when product design matters
- When the brief provides concept descriptions, use them verbatim in artefacts —
  do not replace with generic placeholders

### 2. Rotation Requirements

**Sequential Monadic**: MUST rotate concept subsection order.
For N concepts, create N! rotation orders (or a balanced subset).
- 2 concepts: 2 orders (AB, BA)
- 3 concepts: 6 orders (ABC, ACB, BAC, BCA, CAB, CBA)
- 4 concepts: Use balanced Latin square (not all 24 orders)

Assign respondents equally across rotation orders in FLOW.

**Proto-Monadic**: Rotate concept position in initial display.

### 3. Key Metrics Summary

**Essential metrics** (MUST include for every concept):
- Overall appeal (5-point, positive-first)
- Purchase intent (standard 5-point PI scale: Definitely would / Probably would / etc.)
- Relevance (5-point, positive-first)
- Uniqueness/differentiation (5-point, positive-first)
- Believability (5-point, positive-first)

**Diagnostic metrics** (MUST include for every concept):
- Open-ended likes (required)
- Open-ended dislikes (optional response, but question must be present)

**Comparative metrics** (sequential/proto-monadic only):
- Overall preference (single_choice with real concept names + "None of these")
- Preference rationale (open-ended)
- Rejection rationale for "None" selectors (open-ended, conditional)

### 4. Concept Limits by Design

- **Monadic**: 2-4 concepts (budget permitting)
- **Sequential Monadic**: 2-3 concepts (maximum 4)
- **Proto-Monadic**: 3-6 concepts

**Never** exceed these limits — fatigue kills data quality.

### 5. Sample Size Requirements

**Monadic**:
- Minimum n=150 per concept
- n=200+ per concept preferred for stability

**Sequential Monadic**:
- Minimum n=150 total (all see all concepts)
- n=200+ preferred

**Proto-Monadic**:
- Minimum n=150 total
- n=200+ preferred

---

## Common Pitfalls

❌ Using likelihood scale ("Extremely likely") instead of standard PI scale ("Definitely would purchase")
❌ Scales running low-to-high (negative-first) — use positive-first for concept testing
❌ Putting all concept evaluations in one flat subsection instead of separate subsections per concept
❌ Using `open_ended` for concept display — use `stimulus_display` type
❌ Using `open_ended` for pricing questions — use `numeric_input` type
❌ Using generic "Concept A / B / C" labels instead of actual concept names
❌ Omitting per-concept open-ended likes/dislikes (miss the "why")
❌ Testing too many concepts (>4 in sequential = fatigue)
❌ Unequal concept development (some more detailed than others)
❌ No rotation in sequential design (order bias)
❌ Only asking purchase intent without appeal, relevance, uniqueness, believability
❌ Asking Van Westendorp for all concepts when 3+ are tested (12+ pricing questions = fatigue)

---

## Success Criteria

**Winning concept** typically shows:
- Top 2 Box Appeal: 50%+ (Extremely + Very appealing)
- Top 2 Box Purchase Intent: 40%+ (Definitely + Probably would purchase)
- Relevance: T2B 40%+ (Extremely + Very relevant)
- Uniqueness: Rated higher than competitors
- Believability: 70%+ (Moderately to Extremely believable)

These benchmarks vary by category — adjust based on norms.

---

## Complementary Skills

When price is a key decision factor, consider combining concept testing with:
- **pricing-study**: Add Gabor-Granger or Van Westendorp methodology for rigorous
  price sensitivity measurement
- Use standard concept testing for appeal/preference, then follow with pricing module

Basic Van Westendorp questions (included in this skill) are fine for directional pricing.
Formal pricing studies with the pricing-study skill provide more actionable outputs for
go-to-market decisions.

---

## Output Requirements

Survey MUST include:
- STUDY_METADATA defining all concept artefacts with actual names and content
- Separate subsection per concept (not one flat section) — see Section Structure above
- stimulus_display question type for concept exposure
- Standard 5-point PI scale (Definitely would / Probably would / etc.)
- Positive-first scale direction for all evaluation metrics
- Per-concept open-ended likes and dislikes
- Comparative preference question with real concept names (sequential/proto-monadic)
- Clear rotation/assignment logic in FLOW
- numeric_input for any pricing questions (not open_ended)