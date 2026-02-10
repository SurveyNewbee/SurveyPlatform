# Brand Tracking Analysis Skill

## When to Use
Trigger when:
- `study_type = "market_measurement"`
- `primary_methodology = "tracking"`
- Survey contains brand funnel, equity metrics, NPS

## Required Analyses

### 1. Brand Funnel Analysis
Calculate conversion rates at each stage:
```python
def calculate_brand_funnel(df, brand_col_map):
    """
    Args:
        brand_col_map: {
            'awareness': 'Q_aided_awareness',
            'consideration': 'Q_consideration',
            'trial': 'Q_ever_tried',
            'usage': 'Q_current_usage',
            'primary': 'Q_most_often'
        }
    
    Returns:
        {
            'FreshStart Dairy': {
                'awareness': 975,
                'consideration': 634,
                'trial': 439,
                'usage': 292,
                'primary': 122,
                'awareness_to_consideration': 0.65,
                'consideration_to_trial': 0.69,
                # ... all conversion rates
            },
            # ... other brands
        }
    """
```

### 2. Brand Equity Composite Index
```python
def calculate_equity_index(df, brand, weights=None):
    """
    Weighted composite of:
    - Awareness (0.2)
    - Image attributes mean (0.3)
    - Emotional connection (0.25)
    - NPS normalized (0.25)
    
    Returns: 0-100 score
    """
```

### 3. Perceptual Mapping
```python
from sklearn.decomposition import PCA

def create_perceptual_map(image_df, brands):
    """
    PCA on brand image attribute ratings
    
    Returns:
        {
            'brands': [
                {'name': 'FreshStart', 'x': 0.45, 'y': -0.12},
                # ...
            ],
            'attributes': [
                {'name': 'Quality', 'x': 0.78, 'y': 0.22},
                # ... loadings
            ],
            'variance_explained': [0.42, 0.28]
        }
    """
```

### 4. NPS Calculation & Segmentation
```python
def calculate_nps(df, nps_col, segment_cols=None):
    """
    Returns:
        {
            'overall': {
                'promoters_pct': 30,
                'passives_pct': 50,
                'detractors_pct': 20,
                'nps': 10
            },
            'segments': {
                'age_18_24': {'nps': 15, ...},
                'age_25_34': {'nps': 8, ...},
                # ... all segments
            }
        }
    """
```

### 5. Strength/Weakness Matrix
```python
def strength_weakness_analysis(df, brand, attributes, importance_metric='nps'):
    """
    Correlation of each attribute with NPS = importance
    Brand rating on attribute = performance
    
    Returns:
        {
            'maintain': ['Quality', 'Trust'],      # High imp, high perf
            'improve': ['Innovation', 'Value'],     # High imp, low perf
            'monitor': ['Premium'],                 # Low imp, low perf
            'overkill': ['NZ-made']                # Low imp, high perf
        }
    """
```

### 6. Switching Flow Analysis
```python
def switching_analysis(df, from_col, to_col, trigger_col):
    """
    Sankey diagram data
    
    Returns:
        {
            'flows': [
                {'from': 'Anchor', 'to': 'FreshStart', 'count': 45},
                # ...
            ],
            'triggers': {
                'Price': 128,
                'Quality': 67,
                # ...
            }
        }
    """
```

## Output Format

```python
results = {
    "executive_summary": [
        "FreshStart awareness at 65% trails category leader Anchor (95%)",
        "Strong consideration-to-trial conversion (69%) indicates brand appeal",
        # ... 5-7 key insights
    ],
    
    "demographics": {
        "age": {"18-24": 150, "25-34": 300, ...},
        "region": {"Auckland": 525, ...}
    },
    
    "questions": [
        {
            "question_id": "MS2_Q3",
            "question_text": "Which dairy brands have you heard of?",
            "type": "multiple_choice",
            "results": {
                "FreshStart Dairy": 975,
                "Anchor": 1425,
                # ...
            },
            "chart_type": "horizontal_bar",
            "crosstabs": {
                "by_age": {
                    "18-24": {"FreshStart": 98, "Anchor": 142, ...},
                    # ...
                }
            }
        },
        # ... all questions
    ],
    
    "specialty_analyses": [
        {
            "type": "brand_funnel",
            "title": "Brand Funnel Conversion Rates",
            "data": {
                "FreshStart Dairy": {...},
                "Anchor": {...}
            }
        },
        {
            "type": "perceptual_map",
            "title": "Competitive Brand Positioning",
            "data": {...}
        },
        {
            "type": "nps_segmentation",
            "title": "Net Promoter Score by Segment",
            "data": {...}
        }
    ]
}

# Save
with open(OUTPUT_PATH, 'w') as f:
    json.dump(results, f, indent=2)

print(f"Results saved to: {OUTPUT_PATH}")
```

## Statistical Testing

```python
from scipy.stats import chi2_contingency, ttest_ind

def test_significance(group1, group2, test_type='proportion'):
    """
    Returns:
        {
            'statistic': 2.45,
            'p_value': 0.014,
            'significant': True,  # p < 0.05
            'interpretation': 'Significantly higher'
        }
    """
```

## Key Insights Framework

When generating executive summary, focus on:

1. **Market Position**: Where does the brand stand vs. competitors?
2. **Funnel Health**: Where are the conversion bottlenecks?
3. **Equity Drivers**: What attributes drive loyalty and advocacy?
4. **Segment Opportunities**: Which demographics over/under-index?
5. **Action Priorities**: What should the brand fix/leverage first?

## Example Executive Summary

```python
insights = [
    f"{brand_name} awareness at {awareness_pct}% {'trails' if awareness_pct < leader_pct else 'leads'} category leader {leader_name} ({leader_pct}%)",
    f"Strong consideration-to-trial conversion ({conv_rate}%) suggests effective brand appeal once considered",
    f"Quality perception (score: {quality_score}) significantly correlates with NPS (r={correlation})",
    f"18-34 year olds show {younger_nps - older_nps} points higher NPS, indicating generational appeal strength",
    f"Price dissatisfaction ranks as top switching trigger ({switch_pct}% of switchers), suggesting vulnerability",
    f"Innovation perception lags competitors by {gap} points despite R&D investment messaging",
    f"Recommend prioritizing value communication to reduce price sensitivity among detractors"
]
```

## Crosstab Generation

```python
def generate_crosstabs(df, question_col, demo_cols):
    """
    Create crosstabs for key demographics
    
    Args:
        question_col: Column name of the question
        demo_cols: List of demographic columns ['age', 'region', 'gender']
    
    Returns:
        {
            'by_age': {
                '18-24': {'Option A': 45, 'Option B': 30, ...},
                '25-34': {...}
            },
            'by_region': {...},
            'by_gender': {...}
        }
    """
    crosstabs = {}
    
    for demo in demo_cols:
        crosstabs[f'by_{demo}'] = {}
        for segment in df[demo].unique():
            segment_df = df[df[demo] == segment]
            crosstabs[f'by_{demo}'][segment] = segment_df[question_col].value_counts().to_dict()
    
    return crosstabs
```

## Chart Type Recommendations

```python
CHART_TYPE_MAP = {
    'multiple_choice': 'horizontal_bar',
    'single_choice': 'pie' if len(options) <= 5 else 'horizontal_bar',
    'rating_scale': 'stacked_bar',
    'nps': 'nps_gauge',
    'brand_funnel': 'funnel_chart',
    'perceptual_map': 'scatter_2d',
    'time_series': 'line_chart',
    'crosstab': 'heatmap'
}
```

## Data Quality Checks

```python
# Include in analysis output
data_quality = {
    'total_responses': len(df),
    'complete_responses': len(df[df['completion_status'] == 'complete']),
    'speeders_removed': len(df[df['is_speeder'] == True]),
    'straightliners_removed': len(df[df['straightline_flag'] == True]),
    'quota_compliance': {
        'age': check_quota_compliance(df, 'age', target_quotas['age']),
        'region': check_quota_compliance(df, 'region', target_quotas['region'])
    }
}
```

## Required Libraries

```python
import pandas as pd
import numpy as np
import json
from scipy.stats import chi2_contingency, pearsonr, ttest_ind
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
```

## Error Handling

```python
try:
    # Analysis code
    results = perform_analysis(df)
except KeyError as e:
    print(f"Error: Column not found - {e}")
    print(f"Available columns: {df.columns.tolist()}")
except Exception as e:
    print(f"Analysis error: {e}")
    raise
```
