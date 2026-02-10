# Dummy Survey Data Generation Skill

## Purpose
Generate realistic synthetic survey response data that matches study design, quotas, skip logic, and exhibits market-realistic patterns.

## Core Principles

### 1. Quota Compliance
- **Hard quotas**: Generate EXACT targets (e.g., Auckland n=525)
- **Soft quotas**: Generate approximate targets with ±5% variance
- **Screener terminations**: Simulate realistic qualification rates

### 2. Realistic Response Patterns

#### Brand Funnel Attrition
```python
# Natural drop-off rates
awareness = 1.0          # 100% of aware
consideration = 0.65     # 65% would consider
trial = 0.45             # 45% have tried
current_usage = 0.30     # 30% currently use
primary_brand = 0.15     # 15% use most often
```

#### Correlated Attributes
- High quality → High NPS (r ≈ 0.6)
- High price → Lower value rating (r ≈ -0.4)
- Innovation → Premium perception (r ≈ 0.4)

### 3. Code Template Structure

```python
import pandas as pd
import numpy as np
from faker import Faker

np.random.seed(42)
fake = Faker()

n = {SAMPLE_SIZE}  # From schema

# Step 1: Generate quota variables
data = pd.DataFrame({'respondent_id': range(1, n + 1)})

# Step 2: Hard quotas (EXACT targets)
# Step 3: Soft quotas (approximate with variance)
# Step 4: Screening qualification
# Step 5: Brand funnel with attrition
# Step 6: Image ratings (correlated)
# Step 7: NPS (correlated with quality)
# Step 8: Verbatims matching scores
# Step 9: Demographics

# Save
data.to_csv(OUTPUT_PATH, index=False)
print(f"Generated {len(data)} responses")
print(f"Saved to: {OUTPUT_PATH}")
```

### 4. Market Share Patterns (NZ)

```python
# Dairy category example
brand_shares = {
    'Anchor': 0.42,
    'Mainland': 0.18,
    'Meadow Fresh': 0.12,
    # ... client brand typically 5-15%
}

# Awareness levels by brand size
awareness_rates = {
    'major_brand': 0.90,      # Top 3 brands
    'secondary_brand': 0.65,  # Mid-tier
    'niche_brand': 0.35       # Smaller players
}
```

### 5. Skip Logic Implementation

```python
# Example: Only show NPS to brand-aware respondents
data.loc[
    ~data['brand_awareness'].str.contains('ClientBrand'),
    'nps_score'
] = None
```

### 6. Quality Flags

```python
# Add realistic data quality issues
data['speeder_flag'] = np.random.random(n) < 0.05      # 5% speeders
data['straightline_flag'] = np.random.random(n) < 0.03 # 3% straightliners
```

## Output Requirements

1. CSV file with all question_ids as columns
2. Print summary statistics showing quota compliance
3. Include validation assertions
4. Generate data dictionary

## Validation Checks

```python
# Must pass these assertions
assert len(data) == EXPECTED_SAMPLE_SIZE
assert data['hard_quota_var'].value_counts()['Target1'] == EXACT_TARGET
assert SOFT_MIN <= data['soft_quota_var'].value_counts()['Target2'] <= SOFT_MAX
```

## Regional Demographics (New Zealand)

```python
# Population proportions for regional quotas
nz_regions = {
    'Auckland': 0.35,
    'Wellington': 0.11,
    'Canterbury': 0.13,
    'Waikato': 0.09,
    'Bay of Plenty': 0.07,
    'Other': 0.25
}

# Age distribution (18+)
nz_age = {
    '18-24': 0.12,
    '25-34': 0.18,
    '35-44': 0.17,
    '45-54': 0.17,
    '55-64': 0.16,
    '65+': 0.20
}

# Gender
nz_gender = {
    'Male': 0.49,
    'Female': 0.49,
    'Other': 0.02
}
```

## Response Time Simulation

```python
# Realistic survey completion times
base_time = 15  # minutes for typical survey
time_variance = 0.3  # ±30% variance

# Calculate based on question count
estimated_loi = len(questions) * 0.5  # 30 seconds per question
response_times = np.random.normal(estimated_loi, estimated_loi * time_variance, n)

# Add speeders (< 50% of median time)
speeder_threshold = np.median(response_times) * 0.5
data['is_speeder'] = response_times < speeder_threshold
```

## Verbatim Generation Patterns

```python
# Generate verbatims that match numeric ratings
def generate_verbatim(score, aspect):
    """Generate realistic open-ended response based on rating"""
    if score >= 9:
        templates = [
            f"Excellent {aspect}, very impressed",
            f"Outstanding {aspect}, highly recommend",
            f"Love the {aspect}, will definitely use again"
        ]
    elif score >= 7:
        templates = [
            f"Good {aspect}, meets expectations",
            f"Satisfied with the {aspect}",
            f"Decent {aspect} overall"
        ]
    else:
        templates = [
            f"Disappointed with the {aspect}",
            f"The {aspect} needs improvement",
            f"Not happy with the {aspect}"
        ]
    
    return np.random.choice(templates)

# Apply to verbatim columns
data['quality_verbatim'] = data.apply(
    lambda row: generate_verbatim(row['quality_rating'], 'quality'),
    axis=1
)
```

## Important Notes

1. **Always set random seed for reproducibility**: `np.random.seed(42)`
2. **Match column names EXACTLY to survey schema question IDs**
3. **Respect skip logic**: Set skipped questions to `None` or `NaN`
4. **Include metadata columns**: respondent_id, completion_time, data_quality_flags
5. **Print summary statistics** at the end for validation
