---
name: market-sizing
description: |
  Quantifies total addressable market (TAM), serviceable available market (SAM), and obtainable market share (SOM) through behavioral measurement of category incidence, usage frequency, spending patterns, adoption intent, and competitive dynamics. Use when making investment decisions, entering new markets, or validating business cases that require defensible demand estimates. Requires modular construction from discrete behavioral components rather than top-down projections, and is not suitable for early-stage ideation or abstract market interest assessment.
category: market_measurement
foundational: false
primary_use_case: Estimate market size and revenue potential to support investment decisions, growth planning, and market entry strategies
secondary_applications:
  - Segment prioritization and resource allocation
  - Competitive scenario modeling and share planning
  - Business case validation for new products or services
  - Geographic expansion opportunity assessment
  - Growth forecasting and CAGR projections
  - Adoption timeline modeling
commonly_combined_with:
  - usage-attitudes
  - segmentation
  - pricing-study
  - market-share-benchmarking
  - competitive-intelligence
requires:
  - screening
  - demographics
  - firmographics (for B2B)
problem_frames_solved:
  - performance_tracking
  - launch_risk
  - idea_selection
decision_stages:
  - define
  - validate
  - measure
study_types:
  - market_measurement
  - new_product_development
  - competitive_intelligence
not_suitable_for:
  - Early-stage ideation without defined target markets
  - Abstract interest or intent measurement (use concept-test instead)
  - Markets where behavioral data cannot be reliably recalled or estimated
---


# Market Sizing Research Methodology

## Overview

Market Sizing research is used to estimate the **size, structure, and revenue potential of a market**, typically expressed as **TAM (Total Addressable Market), SAM (Serviceable Available Market), and SOM (Serviceable Obtainable Market)**. It supports investment decisions, growth planning, pricing strategy, and prioritization of segments or geographies.

This methodology prioritizes **defensible assumptions, behavioral grounding, and transparent math**. Surveys must produce inputs that can be credibly scaled, audited, and stress-tested.

---

## Core Principles

- **Behavioral anchoring**
  Market size must be grounded in **actual or plausibly reachable behavior**, not abstract interest or optimism.

- **Explicit universe definition**
  The population being sized must be clearly defined and consistently applied. Ambiguity invalidates totals.

- **Modular construction**
  Market size must be built from discrete components (incidence × frequency × spend), not single "top-down" guesses.

- **Conservative assumptions**
  When uncertainty exists, default to defensible lower-bound assumptions rather than aggressive projections.

- **Transparency**
  Every number must be traceable to a survey question, external input, or stated assumption.

- **Segmentation awareness**
  Market size is rarely uniform. Differences by segment, use case, or geography must be measurable.

- **Temporal modeling**
  Markets evolve. Capture both current state and future adoption to enable growth forecasting.

---

## Survey Design Requirements

### Question Structure

Surveys must follow this **mandatory sizing sequence**:

1. **Universe qualification**
2. **Category incidence and current usage**
3. **Eligibility or fit screening**
4. **Usage or purchase frequency**
5. **Spend or volume measurement**
6. **Competitive landscape mapping**
7. **Adoption barriers and drivers**
8. **Future adoption intent and timeline**
9. **Growth trajectory indicators**
10. **Demographics / firmographics**

#### Universe Qualification
- Define the population precisely (e.g., adults 18–64, SMBs with 10–200 employees).
- Qualification must be **objective and verifiable**, not self-identification alone.
- Use hard screeners for exclusion criteria.
- For B2B: Include decision-maker validation (role, authority level).

#### Category Incidence and Current Usage
- Measure whether respondents **currently participate** in the category.
- Use a defined time window (e.g., past 12 months).
- Incidence must be binary and unambiguous.
- **CRITICAL FOR B2B/TECH:** Distinguish between different solution types (e.g., cloud vs desktop, free vs paid, legacy vs modern).
- Capture **primary vs secondary usage** to avoid over-counting.

#### Eligibility or Fit
- If not all category users are addressable, apply a second screen.
- Examples: regulatory eligibility, budget threshold, technical compatibility.
- **For emerging categories:** Include consideration funnel (never considered, considered before, actively evaluating).

#### Frequency and Spend
- Frequency and spend must be measured **separately**, never combined.
- Use realistic recall periods aligned to purchase cycles.
- For subscription/recurring models: Capture both one-time and recurring costs.
- For B2B: Include total company spend, not just per-user costs.

#### Competitive Landscape Mapping
- **Current provider identification** (primary and secondary)
- **Market share calculation inputs** (% using each provider)
- **Satisfaction with current solution** (indicates switching likelihood)
- **Tenure with current provider** (indicates market maturity)
- **Switching intent** (among current users)
- **Consideration set** (among those intending to switch)

#### Adoption Barriers and Drivers
- **Why non-users haven't adopted** (barriers preventing SAM expansion)
- **What would trigger adoption** (drivers that unlock latent demand)
- **What prevents switching** (lock-in factors reducing market fluidity)
- Critical for distinguishing addressable vs non-addressable portions of TAM.

#### Future Adoption Intent and Timeline
- **Likelihood to adopt** within specific timeframes (12 months, 1-2 years, 2-3 years, etc.)
- **Likelihood to switch** (for current category users)
- **Planned investment levels** (budget allocation trends)
- These inputs enable growth forecasting and CAGR projections.

#### Growth Trajectory Indicators
- **Business/personal growth expectations** (revenue, headcount, lifestyle changes)
- **Technology adoption orientation** (early adopter vs laggard)
- **Category spending trajectory** (increasing, stable, decreasing)
- Used to model different growth scenarios (conservative, moderate, aggressive).

---

### Scale Design

- **Incidence / Eligibility**
  - Use categorical options that cover all possibilities, NOT binary yes/no
  - Include qualifying AND disqualifying options
  - Example: "Which type of accounting software do you use?" with options for cloud, desktop, spreadsheets, manual, outsourced, none

- **Frequency**
  - Use ordered frequency bands tied to time.
  - Anchors must reflect real category behavior.

- **Spend**
  - Use ranges rather than open numeric entry unless respondents are highly informed.
  - Ranges must be non-overlapping and exhaustive.
  - For B2B subscription models: Include "Not sure/Don't know" option.

- **Adoption Intent**
  - Use 5-point likelihood scales ("Extremely likely" to "Not at all likely")
  - Separate measurement for different timeframes
  - Do NOT conflate interest with realistic adoption likelihood

- **Timeline**
  - Use specific time ranges (Within 3 months, 3-6 months, 6-12 months, 1-2 years, etc.)
  - Include "No plans" option
  - Critical for growth forecasting

- **Consistency rules**
  - Keep recall windows consistent across frequency and spend.
  - Do not mix household, personal, and organizational units.
  - Ensure all categorical questions include "Not sure" or "Other" as appropriate.

---

### Sample Questions

**Category Incidence (B2B Software Example)**
> Does your business currently use any form of [CATEGORY] software?
> - Yes, cloud-based [CATEGORY] software
> - Yes, desktop/locally-installed [CATEGORY] software
> - Yes, spreadsheets only for [FUNCTION]
> - No, we use manual/paper-based methods
> - No, we outsource all [FUNCTION]
> - Not sure

**Current Provider Mapping**
> Which [CATEGORY] solution(s) does your business currently use? Select all that apply.
> [List of known providers + Other + Spreadsheets only]

**Primary Provider**
> Which ONE is your primary [CATEGORY] solution?
> [PIPE IN: Options selected in previous question]

**Current Spend**
> Approximately how much does your business spend per month on your primary [CATEGORY] solution (including all licenses/seats)?
> - No cost (free version)
> - Under $50 per month
> - $50-$99 per month
> - $100-$199 per month
> - $200-$399 per month
> - $400-$699 per month
> - $700-$999 per month
> - $1,000+ per month
> - Not sure/Don't know

**Adoption Barriers (for non-users)**
> Why does your business currently use [CURRENT METHOD] rather than [NEW CATEGORY]? Select all that apply.
> - Current solution meets all our needs
> - Lower cost than alternatives
> - [Specific barrier 1]
> - [Specific barrier 2]
> - Not aware of [CATEGORY] options
> - Tried [CATEGORY] before and didn't like it
> - Industry/regulatory requirements prevent use
> - Other (please specify)

**Adoption Intent**
> How likely is your business to adopt [CATEGORY] in the next 12 months?
> - Extremely likely (definitely will adopt)
> - Very likely
> - Moderately likely
> - Slightly likely
> - Not at all likely

**Adoption Timeline**
> Within what timeframe is your business likely to adopt [CATEGORY]?
> - Already using and satisfied (no change planned)
> - Within 3 months
> - Within 6 months
> - Within 12 months
> - 1-2 years
> - 2-3 years
> - 3-5 years
> - More than 5 years
> - No plans to adopt/change

**Growth Expectations**
> How do you expect your [business revenue/household income/category usage] to change over the next 3 years?
> - Significant growth (>20% annually)
> - Moderate growth (10-20% annually)
> - Modest growth (5-10% annually)
> - Stable/flat (0-5% annually)
> - Decline
> - Not sure

**Technology Adoption Orientation**
> How would you characterize your [business's/personal] overall approach to adopting new technology?
> - Early adopter - we embrace new technology quickly
> - Fast follower - we adopt proven technology relatively quickly
> - Mainstream - we adopt when technology is well-established
> - Late adopter - we wait until technology is mature and necessary
> - Laggard - we resist technology change and adopt only when forced

---

## B2B Market Sizing Considerations

When sizing B2B or organizational markets, additional requirements apply:

### Decision-Maker Validation
- Screen for actual decision-making authority, not just involvement
- Include role validation (owner, C-level, director, manager)
- Verify influence over budget decisions

### Firmographic Stratification
- **Employee count** (critical for quota management and weighting)
- **Revenue bands** (correlates with spend capacity)
- **Industry/vertical** (different penetration rates and needs)
- **Geographic distribution** (for regional market sizing)
- **Business age** (maturity correlates with adoption)
- **Multi-location status** (affects complexity and spend)

### External Data Integration
- Survey data must be **weighted to national business population statistics**
- Source: Census bureau, statistics agencies (e.g., ABS, Stats NZ, Census Bureau)
- Weighting variables: Country, region, company size, industry
- Projection method: Apply survey incidence rates to weighted population totals

### Sample Size Requirements for B2B
- Minimum n=300 for single-country B2B market sizing
- n=500+ for multi-country or detailed segmentation
- Oversample smaller company size bands (they have lower incidence but higher population)
- Regional quotas should match business distribution, not population

---

## Competitive Landscape Integration

Market sizing surveys should capture competitive dynamics:

### Current State Metrics
- **Provider market share** (% using each solution among current users)
- **Primary provider share** (more accurate than multi-select for share calculations)
- **Solution type penetration** (cloud vs desktop, free vs paid, etc.)
- **Average spend by provider** (value share vs volume share)
- **Satisfaction by provider** (indicates vulnerability to switching)
- **Tenure by provider** (indicates market maturity and lock-in)

### Market Fluidity Metrics
- **Switching intent** (% of current users likely to switch)
- **Consideration set** (share of voice among switchers)
- **Reasons for switching** (opportunity areas)
- **Barriers to switching** (switching costs, lock-in factors)

### Outputs
- Current market share by provider
- Share of consideration among active evaluators
- Competitive switching matrix (from Provider A to Provider B)
- At-risk share (high switching intent + low satisfaction)
- Competitive SOM (portion of market "in play")

---

## Growth Forecasting and Temporal Modeling

Market sizing surveys must enable multi-year projections:

### Timeline Segmentation
Use **adoption timeline** question to segment the market:
- **Year 1:** Current users + high intent adopters (within 12 months)
- **Year 2:** Add medium intent (1-2 years)
- **Year 3:** Add next cohort (2-3 years)
- **Year 4-5:** Remaining latent demand

### Adoption Curve Modeling
Use **technology adoption orientation** to model conversion rates:
- Early adopters: High conversion from intent to actual adoption
- Fast followers: Moderate conversion
- Mainstream: Lower conversion, longer timeline
- Late adopters/laggards: Very low conversion, extended timeline

### Scenario Construction
Build three scenarios using different assumptions:

**Conservative Scenario:**
- Use bottom-2-box intent only
- Apply low business growth expectations
- Model late adopter conversion rates
- Include higher barrier constraints

**Moderate Scenario:**
- Use middle-range intent
- Apply median growth expectations
- Model mainstream adopter rates
- Balanced barrier assumptions

**Aggressive Scenario:**
- Use top-2-box intent
- Apply high growth expectations
- Model early/fast follower rates
- Lower barrier constraints

### CAGR Calculation
- Compound Annual Growth Rate = [(Market Size Year 5 / Market Size Year 1)^(1/5)] - 1
- Calculate for TAM, SAM, and SOM separately
- Show sensitivity to key assumptions

---

## Weighting and Projection Methodology

### Why Weighting Matters
- Survey samples rarely match population distributions perfectly
- Without weighting, market size estimates will be biased
- Critical for defensible projections

### Weighting Approach
**Post-stratification weighting** to match known population totals:

1. **Identify weighting variables:**
   - Demographics (age, gender, region) for consumer
   - Firmographics (company size, industry, region) for B2B

2. **Obtain population benchmarks:**
   - Census data, business registers, industry associations
   - Must be from authoritative, recent sources

3. **Calculate weights:**
   - Weight = (Population % in segment) / (Sample % in segment)
   - Apply iterative proportional fitting if using multiple variables

4. **Apply weights:**
   - All incidence, frequency, and spend calculations use weighted data
   - Check effective sample size (sum of squared weights)

### Projection Method
**Apply weighted incidence rates to population totals:**

Example:
- Total SMBs (5-200 employees) in market: 150,000 (from official data)
- Weighted % using cloud accounting: 45%
- Projected cloud users: 150,000 × 0.45 = 67,500

### Confidence Intervals
- Calculate 95% confidence intervals for all TAM/SAM/SOM estimates
- Account for:
  - Sample size
  - Weighting efficiency
  - Design effect from stratification
- Report ranges, not point estimates

---

## Common Mistakes to Avoid

- **Top-down sizing without validation**
  *Wrong:* Starting from industry reports only  
  *Correct:* Use survey data to validate or challenge external estimates  
  *Why it matters:* Published figures often mask assumptions.

- **Using intent as demand**
  *Wrong:* "Would you consider buying?"  
  *Correct:* Measure current behavior and realistic adoption intent with timeline  
  *Why it matters:* Intent overstates reachable demand.

- **Double counting**
  *Wrong:* Summing overlapping segments  
  *Correct:* Ensure segments are mutually exclusive or de-duplicated  
  *Why it matters:* Double counting inflates market size.

- **Unbounded spend questions**
  *Wrong:* "How much do you spend?" (open numeric)  
  *Correct:* Use realistic ranges with caps and "Not sure" option  
  *Why it matters:* Outliers distort totals.

- **Ignoring access constraints**
  *Wrong:* Assuming all users are reachable  
  *Correct:* Apply channel, geographic, regulatory, and technical filters  
  *Why it matters:* Not all demand is serviceable.

- **Binary screener questions**
  *Wrong:* "Do you use accounting software? Yes/No"
  *Correct:* "Which type of accounting software do you use? Cloud/Desktop/Spreadsheets/Manual/Outsourced/None"
  *Why it matters:* Need categorical options to properly segment TAM and identify addressable market.

- **Confusing sample size with market quotas**
  *Wrong:* "We need 500 respondents" is treated as total market size
  *Correct:* "We need 500 respondents" is sample; quotas define how they're distributed
  *Why it matters:* Sample quotas enable proper weighting; they don't define the market.

- **Missing growth indicators**
  *Wrong:* Only measuring current state
  *Correct:* Include adoption timeline, growth expectations, technology orientation
  *Why it matters:* Cannot forecast without temporal inputs.

- **Ignoring competitive dynamics**
  *Wrong:* Sizing total market without understanding current provider landscape
  *Correct:* Map current providers, satisfaction, switching intent, consideration set
  *Why it matters:* SOM requires understanding competitive reality and market fluidity.

- **Weak barrier analysis**
  *Wrong:* Not asking why non-users haven't adopted
  *Correct:* Detailed barrier identification with "Select all that apply"
  *Why it matters:* Barriers define non-addressable portions of TAM; without this, SAM is guesswork.

- **No weighting to population**
  *Wrong:* Using raw survey percentages directly
  *Correct:* Weight to match known population distributions before projecting
  *Why it matters:* Survey samples don't naturally match market distributions.

---

## Analysis & Output Requirements

The survey must enable the following calculations:

### TAM (Total Addressable Market)
- **Definition:** All entities in the defined universe, regardless of current usage
- **Customer count:** Total population in qualifying size/demo ranges
- **Revenue value:** Total potential spend if 100% penetration achieved
- **Calculation:** Defined population × category incidence × average annual spend
- **Assumptions:** No access, competitive, or behavioral constraints
- **Segmentation:** TAM by company size, industry, geography, use case

### SAM (Serviceable Available Market)
- **Definition:** Portion of TAM that could realistically be served
- **Exclusions from TAM:**
  - Hard barriers (regulatory, technical incompatibility)
  - Geographic/channel access constraints
  - Segments with irreconcilable objections (never considered, structural barriers)
- **Calculation:** TAM - (% with hard barriers × TAM)
- **Segments within SAM:**
  - Current users (already in market)
  - High intent adopters (strong near-term demand)
  - Medium intent (2-3 year pipeline)
  - Latent demand (long-term potential)

### SOM (Serviceable Obtainable Market)
- **Definition:** Realistic market capture in defined timeframe (typically 12 months)
- **Calculation:** Current users with switching intent + Non-users with high adoption intent
- **Refinement:** SOM × expected market share % (based on competitive analysis)
- **Competitive SOM:** Portion of market "in play" (active evaluation + dissatisfied users)
- **Scenario-based:** Conservative / Moderate / Aggressive assumptions

### Growth Forecasting
- **Year 1:** Current SAM + early adopter cohort
- **Year 2:** Y1 + fast follower cohort
- **Year 3:** Y2 + mainstream cohort
- **Year 4-5:** Y3 + late adopter cohort
- **CAGR:** [(Year 5 / Year 1)^(1/5)] - 1
- **Sensitivity analysis:** Impact of key assumption changes

### Competitive Landscape
- **Current provider market share** (volume and value)
- **Satisfaction benchmarks** by provider
- **Switching intent** by current provider
- **Consideration set share** among active evaluators
- **Feature gap analysis** by provider

### Segment Prioritization
- **Segment scoring framework:**
  - Size (revenue potential)
  - Growth rate
  - Penetration gap (underpenetrated = opportunity)
  - Technology readiness (adoption orientation)
  - Unmet needs intensity
  - Competitive intensity (existing provider strength)
- **Priority matrix:** High priority vs low priority segments
- **Entry strategy:** Beachhead segment recommendations

### Barrier Analysis
- **Adoption barriers** by segment (what prevents TAM → SAM)
- **Switching barriers** by provider (what prevents market fluidity)
- **Addressability assessment:** Which barriers can be overcome vs structural limits

### Sample Size Requirements
- **Consumer market sizing:** Minimum n=500
- **B2B market sizing:** Minimum n=300 per country
- **Key segments:** n=100+ per segment for reliable estimates
- **Rare but valuable segments:** Oversample, then weight back
- **Multi-country:** Adequate sample per country for separate projections

---

## Validation and Quality Assurance

### Survey Design Validation
- [ ] Universe is explicitly and objectively defined
- [ ] All screener questions use categorical options, not binary yes/no
- [ ] Category incidence measured behaviorally with defined time window
- [ ] Solution type distinctions clear (cloud vs desktop, free vs paid, etc.)
- [ ] Primary vs secondary usage distinguished
- [ ] Frequency and spend measured separately
- [ ] Current provider captured (primary and all used)
- [ ] Satisfaction and switching intent measured for current users
- [ ] Adoption barriers measured for non-users
- [ ] Adoption timeline and intent measured with specific timeframes
- [ ] Growth indicators included (business growth, tech orientation, budget trends)
- [ ] Firmographics comprehensive (for weighting)
- [ ] Sample size adequate for segmentation and projection

### Analysis Validation
- [ ] Data weighted to match population benchmarks
- [ ] Weighting efficiency checked (effective sample size)
- [ ] TAM calculation traceable to survey inputs
- [ ] SAM exclusions justified and documented
- [ ] SOM assumptions conservative and defensible
- [ ] No double counting across segments
- [ ] Competitive shares sum to 100% (within rounding)
- [ ] Growth scenarios based on explicit assumptions
- [ ] Sensitivity analysis shows assumption impact
- [ ] Confidence intervals calculated and reported
- [ ] External data sources cited and recent

### Output Validation
- [ ] TAM/SAM/SOM definitions clearly stated
- [ ] All assumptions explicitly documented
- [ ] Calculations auditable (inputs → logic → outputs)
- [ ] Segments mutually exclusive or properly de-duplicated
- [ ] Growth forecasts tied to specific adoption cohorts
- [ ] Competitive analysis internally consistent
- [ ] Barrier analysis informs SAM boundaries
- [ ] Results directionally align with external benchmarks (if available)
- [ ] Confidence intervals acknowledge uncertainty
- [ ] Recommendations follow logically from findings

---

## Integration with Other Methods

- **Usage & Attitudes (U&A)**
  Market sizing often reuses U&A incidence, frequency, and spend modules. U&A provides deeper behavioral context.

- **Segmentation**
  Segments provide structure for differentiated market size and prioritization. Latent class or cluster analysis enables needs-based sizing.

- **Pricing Studies**
  Pricing inputs refine spend assumptions, willingness to pay, and revenue projections. Conjoint or Van Westendorp inform elasticity scenarios.

- **Win–Loss Analysis**
  Helps constrain SOM assumptions based on competitive win rates and decision factors in real evaluations.

- **Brand Tracking**
  Provides longitudinal validation of penetration growth and competitive share shifts over time.

- **Competitive Intelligence**
  External data on competitor customer counts, revenue, pricing validates survey-based share estimates.

---

## Quality Checklist

### Survey Design
- [ ] Target universe is explicitly and objectively defined  
- [ ] All screener questions use categorical options, NOT binary yes/no
- [ ] Category incidence is measured behaviorally with time window
- [ ] Solution types distinguished (cloud vs desktop, free vs paid, etc.)
- [ ] Current provider captured (primary and all used)
- [ ] Satisfaction and tenure measured for current users
- [ ] Switching intent measured with 5-point likelihood scale
- [ ] Adoption barriers measured for non-users (select all that apply)
- [ ] Adoption timeline measured with specific time ranges
- [ ] Adoption intent measured with 5-point likelihood scale
- [ ] Growth expectations captured (revenue, headcount, budget)
- [ ] Technology adoption orientation measured
- [ ] Frequency and spend captured separately  
- [ ] Firmographics comprehensive for weighting (size, industry, region)
- [ ] Sample size adequate (n=500 consumer, n=300+ B2B per country)

### Weighting and Projection
- [ ] Weighting variables identified (match to population benchmarks)
- [ ] Population benchmark sources cited and recent
- [ ] Post-stratification weights calculated correctly
- [ ] Effective sample size checked (weighting efficiency)
- [ ] Projection method documented (weighted incidence × population)
- [ ] Confidence intervals calculated and reported

### Analysis and Outputs
- [ ] TAM calculated as: defined population × incidence × spend
- [ ] SAM exclusions justified (hard barriers, access constraints)
- [ ] SOM realistic (competitive, near-term achievable)
- [ ] No double counting across segments  
- [ ] Competitive shares sum to 100%
- [ ] Growth forecast tied to adoption timeline data
- [ ] CAGR calculated for TAM, SAM, SOM separately
- [ ] Three scenarios modeled (conservative, moderate, aggressive)
- [ ] Assumptions are conservative and transparent  
- [ ] Segment prioritization framework applied
- [ ] Barrier analysis informs SAM boundaries
- [ ] All calculations auditable (inputs traceable)
- [ ] Sensitivity analysis shows assumption impact
- [ ] Results align directionally with external benchmarks
- [ ] Results directly support strategic decision-making

---

## Market Sizing Survey Template Structure

A complete market sizing survey should follow this structure:

### 1. SCREENER (3-5 minutes)
- Decision-maker validation (for B2B)
- Geographic qualification
- Universe qualification (size, demographics, firmographics)
- Industry/category relevance
- **All questions use categorical options, not binary yes/no**

### 2. CURRENT USAGE & COMPETITIVE LANDSCAPE (4-6 minutes)
- Category incidence (which solution type currently used)
- Current provider identification (all used + primary)
- Solution type (cloud vs desktop, free vs paid, etc.)
- Tenure with current provider
- Current spend (monthly/annual, total company or per user)
- Satisfaction with current provider
- Feature requirements (must-haves)
- Unmet needs (gaps in current solution)

### 3. NON-USER SECTION (3-4 minutes, branched)
- Only for those not using the target category
- Why haven't adopted (barriers - select all)
- Ever considered category (consideration funnel)
- What prevented adoption when considered
- Adoption intent (12 month, 5-point scale)

### 4. CURRENT USER RETENTION (2-3 minutes, branched)
- Only for current category users
- Switching intent (12 month, 5-point scale)
- Providers would consider if switching (consideration set)
- Reasons would switch
- Barriers to switching

### 5. ADOPTION INTENT & TIMELINE (3-4 minutes)
- Likelihood to adopt/upgrade within timeframes (12mo, 1-2yr, 2-3yr, etc.)
- Primary trigger for adoption/change
- Biggest barrier preventing sooner adoption/change
- Expected spend over next 12 months

### 6. GROWTH PROJECTIONS (2-3 minutes)
- Business/personal revenue growth expectations (3 years)
- Headcount/household size expectations (3 years)
- Technology adoption orientation (early adopter to laggard)
- Investment in category spending trajectory (increasing, stable, decreasing)

### 7. FIRMOGRAPHICS / DEMOGRAPHICS (2-3 minutes)
- Annual revenue (for B2B)
- Business age (for B2B)
- Multi-location status (for B2B)
- Role in organization (for B2B)
- External advisor relationship (for B2B)
- Age, gender, income, household (for consumer)

### Estimated Total LOI: 15-20 minutes
---

## Final Notes

Market sizing is both art and science. The survey provides the science—hard data on incidence, spend, and behavior. The art is in the assumptions—how barriers are weighted, how adoption curves are modeled, how competitive dynamics unfold.

The best market sizing studies:
- **Ground every assumption in data** (from the survey or external sources)
- **Show their work** (calculations fully auditable)
- **Acknowledge uncertainty** (confidence intervals, scenario ranges)
- **Connect to decisions** (which segments to target, what investment is justified)

A market size estimate is only as good as its weakest assumption. The survey's job is to minimize guesswork and maximize defensibility.