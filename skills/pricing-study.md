name: pricing-study
description: |
  Determines optimal price points, acceptable price ranges, demand curves, and price-feature trade-offs using Van Westendorp Price Sensitivity Meter (PSM), Gabor-Granger willingness-to-pay analysis, and simplified price-feature conjoint. Use when setting launch prices, evaluating price changes, understanding price elasticity, or optimising revenue across segments. Requires careful attention to competitive price context, realistic price range construction, and segment-level analysis. The methodology selection depends on the pricing question: Van Westendorp for range-finding in new categories, Gabor-Granger for demand curves with known price points, and conjoint for feature-price trade-offs. Not suitable for commoditised markets where price is fully transparent and elastic, or for complex B2B enterprise pricing with bespoke negotiation.
category: pricing
foundational: false
primary_use_case: Determine optimal pricing strategy through measurement of price sensitivity, willingness-to-pay, and feature-value trade-offs
secondary_applications:
  - Launch price setting for new products or services
  - Price increase impact assessment
  - Price-tier and packaging optimisation
  - Competitive price positioning analysis
  - Revenue optimisation across customer segments
  - Promotional pricing and discount strategy
  - Price elasticity estimation
commonly_combined_with:
  - concept-test
  - message-claim-testing
  - competitive-positioning
  - market-sizing
  - segmentation
requires:
  - screening
  - demographics
problem_frames_solved:
  - launch_risk
  - revenue_optimisation
  - competitive_strategy
decision_stages:
  - define
  - validate
  - optimise
study_types:
  - pricing
  - new_product_development
  - revenue_optimisation
not_suitable_for:
  - Commoditised markets with fully transparent and elastic pricing
  - Complex B2B enterprise pricing with bespoke negotiation per deal
  - Pricing decisions where cost-plus is the only viable model
  - Categories where price is regulated or fixed by external authority
  - Situations requiring real-market price testing (use A/B pricing experiments instead)

---

# Pricing Research Methodology

## Overview

Pricing research determines **how much customers will pay, what price range is acceptable, how demand changes at different price points, and what feature-price combinations maximise value perception and revenue**. It supports launch pricing, price change decisions, tier/packaging strategy, competitive positioning, and revenue optimisation.

This methodology covers three complementary techniques, each suited to different pricing questions:

| Technique | Best For | Output |
|-----------|----------|--------|
| **Van Westendorp PSM** | Range-finding in new or unfamiliar categories | Acceptable price range, optimal price point (OPP), indifference price point (IPP) |
| **Gabor-Granger** | Demand curve estimation with known/realistic price points | Demand curve, revenue-maximising price, price elasticity |
| **Price-Feature Conjoint (simplified)** | Understanding trade-offs between features and price | Utility scores, feature importance, willingness-to-pay per feature |

A single pricing study may use one, two, or all three techniques depending on the research question. The survey structure adapts accordingly.

---

## Core Principles

- **Context before price**
  Respondents must understand the product, category, and competitive alternatives before encountering any pricing questions. Price without context produces meaningless data.

- **Competitive anchoring**
  Pricing questions must be grounded in competitive reality. Respondents need reference points — either explicitly provided or measured through awareness of current market prices.

- **Realistic price points**
  Price levels used in Gabor-Granger and conjoint must reflect plausible market prices. Unrealistic ranges produce unreliable data. Always validate ranges through desk research or qualitative pre-testing.

- **Segment-level analysis**
  Price sensitivity varies dramatically by segment. All pricing data must be analysable by key segments (demographics, usage level, brand loyalty, purchase frequency).

- **Behavioural grounding**
  Connect pricing to actual purchase context — where they buy, how often, what they currently pay, and what alternatives exist. Abstract "would you pay X?" questions without behavioural context overstate willingness-to-pay.

- **Revenue optimisation over price maximisation**
  The goal is rarely the highest possible price. It is the price that maximises revenue (price × volume), profit, or long-term customer value. The analysis must model volume impact.

- **Sequential methodology**
  When combining techniques, sequence matters: Van Westendorp first (range-finding), then Gabor-Granger (demand at specific points within that range), then conjoint (feature trade-offs at validated price levels).

- **Anchoring bias management**
  The order in which prices are presented affects responses. Gabor-Granger must use descending price order. Van Westendorp's four questions have a fixed canonical order. Conjoint randomises by design.

---

## Survey Design Requirements

### Question Structure

Surveys must follow this **mandatory pricing sequence**:

1. **Category context and current behaviour**
2. **Product/concept presentation**
3. **Competitive price awareness**
4. **Van Westendorp PSM** (if range-finding needed)
5. **Gabor-Granger willingness-to-pay** (if demand curve needed)
6. **Price-feature conjoint** (if trade-off analysis needed)
7. **Purchase intent at recommended price**
8. **Price-related diagnostics**
9. **Demographics**

Not all sections are required in every study. Methodology selection depends on the brief.

---

### Section 1: Category Context and Current Behaviour

Establish what respondents currently pay, where they buy, and how they think about price in this category. This grounds all subsequent pricing questions in reality.

**Required questions:**

```
1. How often do you purchase [CATEGORY] products?
   - Weekly or more often
   - Every 2-3 weeks
   - Monthly
   - Every 2-3 months
   - Every 4-6 months
   - Less often than every 6 months
   - I have never purchased [CATEGORY]

2. Approximately how much do you typically spend per purchase on [CATEGORY]?
   - Less than $[X]
   - $[X] - $[Y]
   - $[Y] - $[Z]
   [Ranges must be calibrated to the specific category]
   - Not sure / I don't pay attention to price

3. Which brand(s) of [CATEGORY] have you purchased in the past [TIMEFRAME]? Select all that apply.
   [Comprehensive brand list + Other + None]

4. Where do you typically purchase [CATEGORY]? Select all that apply.
   [Relevant channel list]
```

**Why this matters:** Current spend establishes the respondent's personal price anchor. Purchase frequency determines annual value. Brand repertoire reveals competitive frame. Without this context, Van Westendorp and Gabor-Granger responses float without reference.

---

### Section 2: Product/Concept Presentation

Before any pricing question, present the product clearly and consistently. The description must be sufficient for respondents to form a realistic value assessment.

**Requirements:**
- Product description must include: what it is, key benefits, size/quantity, and any differentiation from existing options
- Use a stimulus card (image + text) displayed on a single screen
- The stimulus must remain accessible/visible during all pricing questions (or easily re-accessible)
- Do NOT include price in the concept presentation
- If testing multiple products/concepts, use monadic or sequential monadic design (never show all prices simultaneously)

**Example stimulus:**

```
[PRODUCT IMAGE]

[PRODUCT NAME]
[Brief description — 2-3 sentences covering what it is, key benefits, and size/quantity]

Key features:
• [Feature 1]
• [Feature 2]
• [Feature 3]
```

---

### Section 3: Competitive Price Awareness

Measure whether respondents know current market prices. This validates whether their subsequent price responses are grounded.

```
1. How familiar are you with the prices of [CATEGORY] products?
   - Very familiar — I know prices well and compare regularly
   - Somewhat familiar — I have a general sense of prices
   - Not very familiar — I don't pay much attention to prices
   - Not at all familiar — I have no idea what these products cost

2. To the best of your knowledge, what is the typical price range for [CATEGORY] products similar to the one described?
   - Under $[X]
   - $[X] - $[Y]
   - $[Y] - $[Z]
   - Over $[Z]
   - I really don't know
```

**Why this matters:** Price-unaware respondents produce noisier Van Westendorp and Gabor-Granger data. This question enables filtering or weighting by price awareness in analysis.

---

### Section 4: Van Westendorp Price Sensitivity Meter (PSM)

Van Westendorp uses four price-perception questions to identify an acceptable price range and optimal price point. It is best suited for **new products, new categories, or situations where no established price exists**.

#### The Four Canonical Questions

These must be asked in this exact order. Each uses an open-ended numeric entry (not ranges).

```
Thinking about the [PRODUCT] described above...

1. At what price would you consider this product to be so INEXPENSIVE that you would question its quality?
   $[____]

2. At what price would you consider this product to be a BARGAIN — a great buy for the money?
   $[____]

3. At what price would you consider this product to be getting EXPENSIVE — not out of the question, but you'd have to think about it?
   $[____]

4. At what price would you consider this product to be so EXPENSIVE that you would not consider buying it?
   $[____]
```

#### Validation Rules

- **Logical order must hold:** Too Cheap < Bargain < Expensive < Too Expensive
- If a respondent's answers violate this order, flag the response for review (do not auto-correct)
- Set reasonable floor and ceiling bounds based on category context (e.g., $0.50 floor for FMCG, $1 floor for beauty)
- Allow decimal entry for categories where cents matter (e.g., $3.49)
- Do NOT use pre-defined ranges — the power of Van Westendorp is in open numeric entry

#### Design Notes

- Present the product stimulus above or alongside the four questions
- Number entry fields should be clearly labeled with currency symbol
- On mobile, use numeric keyboard
- Consider showing all four questions on one page (reduces context switching) but accept one-per-page if screen real estate requires it
- Helper text below each question can reinforce the meaning: e.g., "This is the price below which you'd doubt the quality"

---

### Section 5: Gabor-Granger Willingness-to-Pay

Gabor-Granger measures purchase intent at specific price points to construct a demand curve. It is best for **established categories where realistic price points are known**, or as a follow-up to Van Westendorp to test specific points within the identified range.

#### Price Point Selection

- Use **5-7 price points** spanning the realistic range
- If Van Westendorp was used, select points within the PMC-PME range (Point of Marginal Cheapness to Point of Marginal Expensiveness)
- If no Van Westendorp, base points on competitive pricing, cost-plus targets, and desk research
- Price points must be **evenly or strategically spaced** (not random)
- Include at least one point below the expected optimal and one above

#### Question Format — Descending Price Order

Gabor-Granger MUST use **descending price order** (highest first) to avoid low-anchor bias. The respondent sees the highest price first, states intent, then sees the next lower price if they rejected the previous one.

```
[SHOW PRODUCT STIMULUS]

Would you purchase [PRODUCT] at $[HIGHEST PRICE]?

- Definitely would buy
- Probably would buy
- Might or might not buy
- Probably would not buy
- Definitely would not buy

[IF "Probably would not" or "Definitely would not" → show next lower price]
[IF "Definitely would" or "Probably would" → STOP, record price as WTP ceiling]
[IF "Might or might not" → show next lower price]
```

**Alternative: Full-grid approach** (all prices shown, all rated)

For simpler implementation or when the cascading logic is complex, an alternative is to show ALL price points and measure intent at each:

```
For each of the following prices, how likely would you be to purchase [PRODUCT]?

                    Definitely  Probably  Might or   Probably   Definitely
                    would buy   would buy might not  would not  would not
$[Price 1 - highest]    ○          ○         ○          ○          ○
$[Price 2]              ○          ○         ○          ○          ○
$[Price 3]              ○          ○         ○          ○          ○
$[Price 4]              ○          ○         ○          ○          ○
$[Price 5 - lowest]     ○          ○         ○          ○          ○
```

**Trade-off:** The cascading approach is methodologically purer (reduces anchoring), but the grid is simpler to implement and still produces usable demand curves. For MVP, the grid approach is acceptable.

#### Design Notes

- Always present prices in **descending order** (highest at top) in the grid
- Currency formatting must be consistent and realistic (e.g., $29.99, not $30)
- If combined with Van Westendorp, the GG prices should be derived from PSM results
- For subscription pricing, specify the billing period clearly: "per month" or "per year"

---

### Section 6: Price-Feature Conjoint (Simplified)

Simplified conjoint measures trade-offs between features and price. Use when the pricing question isn't just "how much?" but "how much for what combination of features?"

This is a **Choice-Based Conjoint (CBC) adaptation** simplified for survey implementation.

#### Attribute and Level Design

- **3-5 attributes** (including price)
- **2-4 levels per attribute**
- Price levels should span the realistic range identified through Van Westendorp or desk research
- Total profiles per choice task: 2-3 options + "None of these"

**Example attributes and levels:**

```
Attribute 1: Price
  - $24.99
  - $34.99
  - $44.99

Attribute 2: Size
  - 30ml
  - 50ml

Attribute 3: Key Ingredient
  - Retinol
  - Vitamin C
  - Hyaluronic Acid

Attribute 4: Brand Promise
  - "Visible results in 2 weeks"
  - "Dermatologist recommended"
  - "100% natural ingredients"
```

#### Choice Task Format

```
Which of the following would you most prefer to purchase?

Option A:
  [Feature combo A with Price A]

Option B:
  [Feature combo B with Price B]

Option C:
  [Feature combo C with Price C]

○ None of these — I would not purchase any of these options
```

**Design Requirements:**
- **8-12 choice tasks** per respondent (fatigue increases errors beyond 12)
- Use an **orthogonal or D-efficient experimental design** to generate profiles
- Randomise the order of options within each task
- Randomise the order of tasks across respondents
- Always include a "None" option to avoid forced choice

#### Design Notes for Implementation

- Conjoint design generation requires statistical software or design algorithms (not hand-crafted)
- For MVP, a **fixed design** (pre-generated set of tasks) is acceptable if D-efficiency is verified
- Each respondent sees the SAME set of tasks (full-profile design) or a random subset (if using a modular design)
- Present each choice task on its own screen
- Feature labels must be short enough for side-by-side comparison on mobile

---

### Section 7: Purchase Intent at Recommended Price

After pricing exercises, test purchase intent at a specific price the client is considering or that emerged as optimal:

```
[PRODUCT] will be available at $[RECOMMENDED PRICE].

How likely are you to purchase this product at this price?
- Definitely would buy
- Probably would buy
- Might or might not buy
- Probably would not buy
- Definitely would not buy
```

**Why this matters:** Provides a direct PI benchmark at the price being considered. Enables comparison with concept test norms and competitive PI benchmarks.

---

### Section 8: Price-Related Diagnostics

Capture the reasoning behind price perceptions:

```
1. Compared to similar products you've purchased or considered, this price is:
   - Much lower than expected
   - Somewhat lower than expected
   - About what I'd expect
   - Somewhat higher than expected
   - Much higher than expected

2. At the price shown ($[X]), which of the following best describes your view?
   - Excellent value for money
   - Good value for money
   - Fair value for money
   - Somewhat poor value for money
   - Very poor value for money

3. [IF PROBABLY/DEFINITELY WOULD NOT BUY]
   What is the main reason this price would stop you from purchasing? Select ONE.
   - It's more than I can afford for this type of product
   - I can get something similar for less
   - The product doesn't seem worth that much
   - I'd need to see more evidence of quality/effectiveness
   - I'd wait for a sale or promotion
   - Other (please specify)
```

---

## Scale Design

- **Van Westendorp:** Open numeric entry only. No ranges, no sliders, no pre-defined options. Currency-formatted input fields with decimal support.

- **Gabor-Granger purchase intent:** 5-point scale, consistently worded:
  - Definitely would buy
  - Probably would buy
  - Might or might not buy
  - Probably would not buy
  - Definitely would not buy

- **Value perception:** 5-point scale from "Excellent value" to "Very poor value"

- **Price expectation:** 5-point scale from "Much lower than expected" to "Much higher than expected"

- **Conjoint:** Forced choice among 2-3 profiles + "None of these"

- **Consistency rules:**
  - Always show prices with consistent decimal formatting within a study ($29.99 or $30, not mixed)
  - Always specify unit (per unit, per month, per year, per pack)
  - Currency symbol must match the market being surveyed
  - Price-related scales must use the same direction throughout (e.g., always positive-to-negative or always high-to-low)

---

## Common Mistakes to Avoid

- **Price questions before context**
  *Wrong:* Asking "What would you pay for this?" immediately after a brief description
  *Correct:* Establish category behaviour, current spend, and competitive awareness first
  *Why it matters:* Without context, respondents guess rather than evaluate

- **Unrealistic price ranges in Gabor-Granger**
  *Wrong:* Testing $5 to $500 for a skincare product
  *Correct:* Use 5-7 points within the plausible competitive range
  *Why it matters:* Extreme prices produce floor/ceiling effects that flatten the demand curve

- **Ascending price order in Gabor-Granger**
  *Wrong:* Showing lowest price first
  *Correct:* Always descend from highest to lowest
  *Why it matters:* Low-to-high creates anchoring bias that depresses WTP

- **Ranges instead of open entry in Van Westendorp**
  *Wrong:* Giving respondents price ranges to select from
  *Correct:* Open numeric entry for all four questions
  *Why it matters:* Ranges bias responses to midpoints and prevent precise curve intersection calculation

- **Logical order violations in Van Westendorp**
  *Wrong:* Accepting data where "Too Cheap" > "Bargain" or "Expensive" > "Too Expensive" without flagging
  *Correct:* Validate logical order at data collection (warning) and analysis (exclusion or review)
  *Why it matters:* Illogical responses distort the cumulative distribution curves

- **Too many conjoint tasks**
  *Wrong:* 20+ choice tasks per respondent
  *Correct:* 8-12 maximum
  *Why it matters:* Fatigue degrades response quality after 12 tasks, producing random clicking

- **Price without features in conjoint**
  *Wrong:* Testing price as the only varying attribute
  *Correct:* Price must trade off against at least 2-3 feature attributes
  *Why it matters:* Price-only conjoint is just Gabor-Granger with extra steps. Conjoint's value is in trade-off analysis.

- **Ignoring segment differences**
  *Wrong:* Reporting a single optimal price for the entire sample
  *Correct:* Analyse VW, GG, and conjoint by key segments
  *Why it matters:* Heavy users, premium buyers, and price-sensitive segments have dramatically different WTP curves

- **Treating top-box purchase intent as conversion rate**
  *Wrong:* "42% said they'd definitely buy at $29.99, so we'll capture 42% of the market"
  *Correct:* Apply industry-standard calibration factors (typically 70-80% of "definitely" and 20-30% of "probably")
  *Why it matters:* Stated purchase intent systematically overstates actual purchasing behaviour

- **Missing the revenue-maximising price**
  *Wrong:* Recommending the price most people find "acceptable"
  *Correct:* Model revenue = price × estimated volume at that price
  *Why it matters:* The most acceptable price is usually not the most profitable one

---

## Analysis & Output Requirements

### Van Westendorp PSM Analysis

**Cumulative Distribution Curves:**

Plot four cumulative distribution curves from the four questions:
- "Too Cheap" — cumulative from high to low (% saying price X or lower is too cheap)
- "Bargain" — cumulative from high to low
- "Expensive" — cumulative from low to high (% saying price X or higher is expensive)
- "Too Expensive" — cumulative from low to high

**Key Intersection Points:**

| Point | Intersection | Meaning |
|-------|-------------|---------|
| **OPP** (Optimal Price Point) | "Too Cheap" × "Too Expensive" | Price where equal proportions feel it's too cheap vs too expensive. Theoretical optimal. |
| **IPP** (Indifference Price Point) | "Bargain" × "Expensive" | Price where equal proportions feel it's a bargain vs expensive. Market norm/expected price. |
| **PMC** (Point of Marginal Cheapness) | "Too Cheap" × "Expensive" | Lower bound of acceptable range. Below this, quality concerns dominate. |
| **PME** (Point of Marginal Expensiveness) | "Bargain" × "Too Expensive" | Upper bound of acceptable range. Above this, resistance is too high. |

**Acceptable Price Range:** PMC to PME

**Segment Comparison:**
Run VW analysis separately for each key segment. Compare OPP and acceptable ranges across segments to identify pricing tiers or segment-specific strategies.

### Gabor-Granger Demand Curve Analysis

**Demand Curve Construction:**

For each price point, calculate:
```
Demand % = % "Definitely would buy" + % "Probably would buy"

(Alternative: use calibrated weights — e.g., 80% of "Definitely" + 30% of "Probably")
```

Plot demand % (Y-axis) vs price (X-axis) to produce the demand curve.

**Revenue Optimisation:**

```
Revenue Index at Price X = Price X × Demand % at Price X

Revenue-Maximising Price = Price X where Revenue Index is highest
```

**Price Elasticity:**

```
Elasticity between Price A and Price B = 
  (% change in demand) / (% change in price)

Elastic: |E| > 1 (demand drops faster than price rises — avoid this zone)
Inelastic: |E| < 1 (demand is relatively stable — pricing power exists here)
```

**Segment Comparison:**
Overlay demand curves by segment. Identify segments where the demand curve is flatter (less price sensitive = higher WTP) vs steeper (highly elastic = price sensitive).

### Conjoint Analysis

**Part-Worth Utilities:**

Calculate utility scores for each level of each attribute. Higher utility = more preferred.

```
For price levels: Negative utility increases as price increases (all else equal)
For feature levels: Utility reflects relative preference
```

**Attribute Importance:**

```
Importance % = (Max utility - Min utility for attribute) / Sum across all attributes × 100

Tells you: How much does this attribute matter relative to others in the purchase decision?
```

**Willingness-to-Pay per Feature:**

```
WTP for Feature X = Price difference that produces equivalent utility change

Example: If upgrading from "30ml" to "50ml" adds 0.5 utility,
and each $5 price increase subtracts 0.25 utility,
then WTP for the 50ml upgrade = $10
```

**Market Simulation:**

Using utility scores, simulate market share at different price/feature combinations:

```
For a given product profile, calculate total utility = sum of part-worths
Share of preference = exp(Utility_A) / [exp(Utility_A) + exp(Utility_B) + ... + exp(Utility_None)]
```

This enables "what-if" pricing scenarios.

### Integrated Pricing Recommendation

When multiple techniques are used, synthesise findings:

1. **Van Westendorp** defines the acceptable range (PMC to PME)
2. **Gabor-Granger** identifies the revenue-maximising point within that range
3. **Conjoint** reveals which features justify a premium and which features can be removed to support a lower tier

**Output format:**

```
Recommended Price: $[X]
Acceptable Range: $[PMC] – $[PME]
Revenue-Maximising Price: $[GG optimal]
Key Trade-offs: [From conjoint — e.g., "50ml size justifies $8 premium over 30ml"]

Segment-Specific Recommendations:
- [Segment A]: $[X] — less price sensitive, higher WTP
- [Segment B]: $[Y] — price sensitive, consider entry tier
```

---

## Integration with Other Methods

- **Concept Testing**
  Pricing is often embedded within concept testing. Test the concept first (appeal, relevance, uniqueness), then test pricing for the concepts that clear the appeal threshold. This prevents pricing dead concepts.

- **Message & Claim Testing**
  Claims that resonate can justify price premiums. Test claims first, then test pricing with the winning claims attached to the product description.

- **Competitive Positioning**
  Competitive attribute ratings provide context for whether a product can command a premium, parity, or discount price relative to competitors.

- **Market Sizing**
  Pricing inputs refine market size estimates. Demand curves from Gabor-Granger enable volume-at-price projections for TAM/SAM calculations.

- **Segmentation**
  Segments provide the structure for differentiated pricing strategy. Pricing analysis by segment is essential — a single price rarely optimises across all segments.

---

## Deliverables Framework

### Primary Outputs

1. **Optimal Price Recommendation** — with supporting rationale and confidence level
2. **Acceptable Price Range** — PMC to PME from Van Westendorp
3. **Demand Curve** — from Gabor-Granger, showing volume at each price point
4. **Revenue Optimisation Model** — price × volume modelling with revenue-maximising price
5. **Price Elasticity Assessment** — elastic vs inelastic zones
6. **Segment-Level Pricing Analysis** — different WTP by segment

### Secondary Outputs (if conjoint included)

7. **Feature Importance Rankings** — relative importance of price vs features
8. **Willingness-to-Pay per Feature** — dollar value of each feature/upgrade
9. **Market Simulation** — share of preference under different price/feature scenarios
10. **Tier/Packaging Strategy** — recommended good/better/best configurations

### Diagnostic Outputs

11. **Value Perception Mapping** — perceived value relative to price
12. **Competitive Price Positioning** — how the recommended price compares to competitive set
13. **Price Barrier Analysis** — reasons for rejection at higher price points
14. **Price Awareness Assessment** — how well the target market knows current pricing

---

## Quality Checklist

### Survey Design
- [ ] Product/concept is presented clearly before any pricing questions
- [ ] Category context and current spend are captured before pricing
- [ ] Competitive price awareness is measured
- [ ] Van Westendorp uses open numeric entry (not ranges)
- [ ] Van Westendorp questions are in canonical order (Too Cheap → Bargain → Expensive → Too Expensive)
- [ ] Gabor-Granger uses descending price order
- [ ] Gabor-Granger price points span a realistic, competitive range
- [ ] Conjoint has 3-5 attributes with 2-4 levels each
- [ ] Conjoint uses 8-12 choice tasks maximum
- [ ] Conjoint includes "None of these" option
- [ ] Purchase intent is captured at the recommended/tested price
- [ ] Price diagnostics capture value perception and rejection reasons

### Analysis
- [ ] Van Westendorp curves are plotted correctly (cumulative distributions)
- [ ] All four VW intersection points are calculated (OPP, IPP, PMC, PME)
- [ ] Gabor-Granger demand curve uses appropriate calibration
- [ ] Revenue optimisation model is calculated (price × volume)
- [ ] Price elasticity is computed between adjacent price points
- [ ] Conjoint utilities are estimated using appropriate model (logit/HB)
- [ ] Feature importance and WTP per feature are derived from conjoint
- [ ] All analysis is segmented by key demographic/behavioural groups
- [ ] Purchase intent calibration factors are applied (not raw top-box)

### Deliverables
- [ ] Clear price recommendation with supporting evidence
- [ ] Acceptable range is defensible and grounded in data
- [ ] Segment-level pricing differences are identified and actionable
- [ ] Revenue impact is modelled, not just price acceptability
- [ ] Competitive context is reflected in recommendations

---

## Final Guidance

Pricing research is deceptively simple to field and dangerously easy to misinterpret. The biggest risks are:

1. **Context starvation:** Pricing questions asked too early, before the respondent has a realistic value anchor. Always establish category context and product understanding first.
2. **False precision:** Van Westendorp intersections calculated to the penny, reported as if they're exact. They're not. Report ranges and confidence intervals.
3. **Revenue blindness:** Recommending the "acceptable" price without modelling the revenue impact. A $5 price increase that loses 10% of volume may still increase total revenue.
4. **Segment averaging:** Reporting one price for a heterogeneous market. Always segment. If heavy users will pay $45 and light users will pay $25, the "average" of $35 may be wrong for both groups.
5. **Static thinking:** Pricing is dynamic. Competitive responses, promotional activity, and market maturation all shift price sensitivity over time. Build in flexibility and re-test periodically.

**Remember:** The best pricing research doesn't just find a number — it builds a pricing *framework* that the business can use to make ongoing decisions as the market evolves.