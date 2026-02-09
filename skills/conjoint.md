---
name: conjoint
description: |
  Measures feature-level utilities and price sensitivity through choice-based experiments to optimize product configuration and pricing. Use when testing 4-8 attributes with multiple levels to understand feature trade-offs and willingness to pay across complete product profiles. Typically includes 12-15 choice tasks showing 3-4 product profiles per task with systematic attribute variation. Not suitable for simple A/B concept comparison, early-stage ideation, or studies with fewer than 3 meaningful attributes.
category: new_product_development
foundational: false
primary_use_case: Determine optimal product configuration and price point by quantifying feature-level utilities and trade-offs
secondary_applications:
  - Market share simulation and competitive scenario modeling
  - Portfolio optimization across product lines
  - Feature prioritization for product roadmaps
  - Price elasticity analysis in context of features
commonly_combined_with:
  - concept-test
  - pricing-study
  - segmentation
  - choice-modeling
requires:
  - screening
  - rating-scales
problem_frames_solved:
  - tradeoff_optimization
  - idea_selection
decision_stages:
  - design
  - validate
study_types:
  - new_product_development
  - pricing_optimization
not_suitable_for:
  - Simple A/B concept testing (use concept-test instead)
  - Early-stage ideation without defined attributes and levels
  - Studies with fewer than 3 attributes or simple binary choices
---


# Conjoint Analysis Survey Design

## Overview
Choice-based conjoint (CBC) measures how people make trade-offs between product features by having them choose between complete product profiles in realistic choice scenarios.

## When to Use This Skill
- Testing multiple product attributes simultaneously (typically 4-8 attributes)
- Understanding relative importance of features vs. price
- Optimizing product configurations
- Simulating market share for different product variants
- Price sensitivity analysis in context of features

## Survey Structure Requirements

### Screener Section
- Qualify based on category usage and purchase intent
- Ensure respondents are familiar with the product category
- Screen for recent purchase or high purchase intent (next 6-12 months)

### Warm-Up Section (Before Choice Tasks)
- Brief explanation of the exercise
- 1-2 practice tasks to familiarize respondents
- Clear instructions that "none of these" is always an option

### Choice Task Design
- **Number of tasks**: 12-15 tasks per respondent (minimum 10, maximum 20)
- **Profiles per task**: 3-4 product profiles + "none" option
- **Attribute levels**: Vary systematically using experimental design (not shown to user)
- **Presentation**: Show complete product profiles with all attributes
- **Question format**: "Which of these would you be most likely to purchase?"

### Task Layout Example
```
Which espresso machine would you most likely purchase?

○ Option A
  • Brewing: Semi-automatic with pressure gauge
  • Milk System: Manual steam wand
  • Smart Features: No connectivity
  • Build: Stainless steel exterior
  • Grinder: Burr grinder included
  • Price: $449

○ Option B
  • Brewing: Fully automatic one-touch
  • Milk System: Integrated one-touch system
  • Smart Features: WiFi-enabled
  • Build: Commercial-grade stainless
  • Grinder: No grinder
  • Price: $799

○ Option C
  • Brewing: Manual lever machine
  • Milk System: Automatic frother
  • Smart Features: Bluetooth app
  • Build: Plastic construction
  • Grinder: Blade grinder
  • Price: $299

○ None of these
```

### Post-Task Questions
- Overall preference ranking (optional)
- Holistic ratings of winning concept from choice tasks
- Usage scenarios and context

## Critical Design Rules

1. **Attribute Selection**
   - Limit to 4-8 attributes total (including price)
   - Each attribute must be meaningful and actionable
   - Levels must be realistic and achievable
   - Avoid dominated profiles (all worst levels)

2. **Level Balance**
   - Keep level counts similar across attributes (2-5 levels each)
   - More levels = more precision but longer survey
   - Price typically needs 4-5 levels for elasticity curves

3. **Experimental Design**
   - Use orthogonal or D-optimal design for level combinations
   - Balance attribute appearance across tasks
   - Ensure level pairs appear together systematically
   - Avoid unrealistic combinations where possible

4. **Questionnaire Flow**
   - Screener → Warm-up → Choice tasks → Post-task questions → Demographics
   - Keep choice tasks together (don't interrupt with other questions)
   - Randomize task order per respondent

5. **Response Quality**
   - Include 1-2 validation tasks (dominated profiles)
   - Monitor "none" selection rate (>40% suggests pricing too high)
   - Track completion time (too fast = low quality)

## Output Requirements for Survey JSON

The survey must include:
- Clear STUDY_METADATA with all attribute definitions
- Choice tasks in MAIN_SECTION with proper randomization logic
- FLOW rules for task presentation and validation
- Post-task holistic questions after choice section

## Common Pitfalls to Avoid

❌ Too many attributes (>8) = cognitive overload
❌ Too many levels per attribute = survey too long
❌ Dominated profiles = respondents disengage
❌ Missing "none" option = forced choices, unrealistic demand
❌ No practice tasks = higher dropout, lower quality
❌ Mixing choice tasks with other question types = confusion

## Quality Indicators

✓ Task completion rate >85%
✓ Average time per task: 15-30 seconds
✓ "None" selection rate: 10-30%
✓ Logical consistency in choices
✓ Attribute importance aligns with category norms
