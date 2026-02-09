---
name: segmentation
description: |
  Identifies distinct, meaningful customer groups within a market using multivariate clustering techniques based on shared needs, attitudes, behaviors, or motivations. Use when you need to guide targeting, positioning, or portfolio strategy decisions and have 200+ respondents with 15-30 well-designed segmentation variables. Requires analytical methodology designed specifically for clustering (not repurposed descriptive questions) and focuses on psychographic/behavioral inputs rather than demographics. Commonly combined with concept-test or message-test to tailor strategies by segment. Not suitable for simple audience profiling, brand-specific studies, or when you have fewer than 15 segmentation variables.
category: brand_strategy
foundational: false
primary_use_case: Identify distinct customer groups to guide targeting strategy, positioning decisions, and portfolio optimization
secondary_applications:
  - Tailoring product development roadmaps to segment needs
  - Optimizing marketing messages and channel strategies by segment
  - Portfolio strategy and go-to-market planning
  - Price sensitivity analysis across customer groups
commonly_combined_with:
  - concept-test
  - message-test
  - pricing-study
  - brand-positioning
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - unknown_needs
  - tradeoff_optimization
  - performance_tracking
decision_stages:
  - discover
  - define
  - design
study_types:
  - brand_strategy
  - market_measurement
  - new_product_development
not_suitable_for:
  - Simple audience profiling or demographic breakdowns
  - Brand-specific studies or satisfaction measurement
  - Studies with fewer than 200 respondents or 15 segmentation variables
---


# Segmentation

## Overview
Segmentation research identifies distinct, meaningful groups within a market based on shared needs, attitudes, behaviors, or motivations. Unlike descriptive profiling, segmentation is an **analytical methodology** that uses multivariate techniques to uncover latent structure in the data. Segmentation is used to guide targeting, positioning, portfolio strategy, and go-to-market decisions.

## Core Principles
Segmentation only works when it is designed for analysis from the start. Always follow these principles:

- **Segmentation-first design:** Questions must be written specifically for clustering, not repurposed from other studies.
- **Needs and motivations over demographics:** Attitudinal and behavioral variables drive segments; demographics describe them.
- **Variance is essential:** Variables must meaningfully differentiate respondents.
- **Parsimony:** Fewer, stronger variables outperform long, unfocused batteries.
- **Actionability:** Segments must be targetable, sizeable, and strategically distinct.

## Survey Design Requirements

### Segmentation Type Selection

#### Analytical Segmentation (Primary)
Use when:
- You need statistically derived segments
- The goal is targeting or positioning
- You will run cluster or latent class analysis

This skill focuses on **analytical segmentation**.

#### Descriptive Segmentation (Secondary)
Use when:
- You only need audience descriptions
- No clustering will be performed

Do not label descriptive groupings as “segments.”

---

### Segmentation Variable Design

#### Core Segmentation Battery
Segmentation variables MUST:
- Reflect **needs, motivations, attitudes, or behaviors**
- Be category-relevant
- Be stable over time
- Avoid brand or price specificity

Avoid using:
- Brand awareness
- Brand usage
- Purchase intent
- Demographics
- Satisfaction or NPS

These belong in profiling, not segmentation inputs.

---

### Psychographic & Needs Batteries

#### Statement Construction Rules
Each statement MUST:
- Express one clear idea
- Be written in first person
- Avoid absolutes (“always”, “never”)
- Be applicable to all respondents

**Correct format:**
```

I am willing to pay more for products that make my life easier.

```

**Incorrect formats:**
- “Price is important to me and affects my choices.”
- “Premium brands are better.”

---

### Scale Design for Segmentation

Use **agreement scales** optimized for variance.

#### Recommended Scale
- Strongly agree
- Somewhat agree
- Neither agree nor disagree
- Somewhat disagree
- Strongly disagree

Rules:
- Use a **5-point scale** only
- Label all points
- Keep polarity consistent
- Include a neutral midpoint

Avoid:
- 7–10 point scales
- Importance scales
- Binary agree/disagree

---

### Number of Variables
- **Minimum:** 15–20 well-designed variables
- **Ideal:** 20–30 variables
- **Maximum:** 40 (only if sample size supports it)

Rule of thumb:
- At least **10 respondents per variable**, preferably more

Never run segmentation with fewer than 200 respondents.

---

### Behavioral Segmentation Inputs

Behavioral variables may be included if they:
- Are category-level (not brand-specific)
- Reflect frequency, occasions, or involvement
- Show meaningful spread

**Examples:**
- Usage frequency
- Purchase channel preference
- Occasion-based usage

Avoid binary behaviors unless highly diagnostic.

---

### Sample Segmentation Questions

#### Psychographic Statement Example
```

Please indicate how much you agree or disagree with the following statements.

I like to research products extensively before making a purchase.

```

#### Needs-State Example
```

When choosing a [CATEGORY], how important are the following?

Feeling confident in my decision
Saving time
Getting the lowest possible price

```

(Use agreement framing, not importance framing, when possible.)

---

## Common Mistakes to Avoid

### Mistake 1: Using Demographics as Segmentation Inputs
**Wrong:**  
Clustering on age, gender, and income.

**Why it’s wrong:**  
Demographics describe people; they do not explain behavior.

**Correct approach:**  
Use demographics only after segments are defined.

---

### Mistake 2: Too Many Similar Statements
**Wrong:**  
Multiple items that say essentially the same thing.

**Why it’s wrong:**  
Redundant variables dilute clustering power.

**Correct approach:**  
Ensure each variable adds unique information.

---

### Mistake 3: Brand-Contaminated Statements
**Wrong:**  
“I trust Brand X to deliver quality.”

**Why it’s wrong:**  
Segments become brand-specific and unstable.

**Correct approach:**  
Keep inputs brand-agnostic.

---

### Mistake 4: Optimizing for Statistical Fit Alone
**Wrong:**  
Choosing a 6-segment solution because metrics look best.

**Why it’s wrong:**  
Statistically “optimal” solutions can be unusable.

**Correct approach:**  
Balance statistical quality with interpretability and actionability.

---

## Analysis & Output Requirements

### Data Preparation
Before clustering:
- Remove straight-liners
- Check variance and distributions
- Standardize variables (z-scores)
- Remove highly correlated variables

Never cluster on raw, unvalidated data.

---

### Clustering Approaches
Common methods:
- Hierarchical clustering (Ward’s method)
- K-means clustering
- Latent class analysis (LCA)

Select method based on:
- Sample size
- Variable types
- Need for probabilistic assignment

---

### Segment Solution Validation
Always validate segments by:
- Size (each segment ≥10% unless niche is intended)
- Stability (split-sample validation)
- Distinctiveness (clear separation on key variables)
- Interpretability (clear narrative)

---

### Segment Profiling
After segments are defined, profile using:
- Demographics
- Brand usage
- Media behavior
- Attitudinal outcomes

Never re-run clustering after profiling.

---

### Deliverables
Always produce:
- Segment descriptions and names
- Size of each segment
- Key defining needs and motivations
- Targetability indicators
- Strategic implications

Avoid naming segments after demographics alone.

---

## Integration with Other Methods

Segmentation integrates with:
- **Concept testing:** Read appeal by segment
- **Message testing:** Tailor messaging by segment
- **Pricing studies:** Identify price sensitivity differences
- **Brand tracking:** Track brand health within segments

Treat segmentation as foundational, not standalone.

---

## Quality Checklist

- [ ] Segmentation inputs are needs- and attitude-based
- [ ] Variables show sufficient variance
- [ ] Sample size supports clustering
- [ ] Scale design is consistent and labeled
- [ ] Clustering method is appropriate
- [ ] Segments are interpretable and actionable
- [ ] Profiling is done post-segmentation
- [ ] Clear strategic guidance is provided

---

## Final Guidance
Segmentation is one of the most misused methodologies in research. Discipline in **question design** matters more than analytical sophistication. If the inputs are weak, no clustering technique will save the study. Design the survey as if the segmentation depends on it—because it does.
```

---
