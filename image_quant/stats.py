"""
Statistical Analysis Module for Image Quantification

This module provides statistical testing functionality for fluorescence microscopy
data using mixed-effects models. It handles group comparisons with proper correction
for multiple testing and accounts for random effects from image-level variation.
"""

import pandas as pd
import statsmodels.formula.api as smf
from itertools import combinations
import numpy as np
from statsmodels.stats.multitest import multipletests


def run_mixed_lme(
    df: pd.DataFrame,
    dep_var: str = 'fracIn',
    comparisons: list | None = None,
    p_adjust_method: str = 'holm',) -> pd.DataFrame:    
    """
    Perform pairwise group comparisons using mixed-effects models.
    
    Fits a random-intercepts model to account for image-level variation
    and tests specific group contrasts. This approach is appropriate for
    nested data where multiple measurements come from the same images.
    
    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: 'image_id', 'file', 'series', 'group', 
        'intIn', 'intTot', 'fracIn'.
    dep_var : str, default 'fracIn'
        Dependent variable for analysis. One of 'intIn', 'intTot', 'fracIn'.
    comparisons : list of pairs, optional
        Specific group comparisons to perform. Each pair should contain two 
        group identifiers. If omitted, all pairwise combinations are tested.
    p_adjust_method : str, default 'holm'
        Multiple comparison correction method passed to 
        ``statsmodels.stats.multitest.multipletests``.

    Returns
    -------
    pd.DataFrame
        Results table with columns: group1, group2, estimate, se, t_value, 
        p_value, p_value_adj, ci_lower, ci_upper.
        
    Notes
    -----
    The model treats 'image_id' as a random effect to account for 
    within-image correlation of measurements.
    """
    # Validate the dependent variable choice
    allowed = {'intIn', 'intTot', 'fracIn'}
    if dep_var not in allowed:
        raise ValueError(f"dep_var must be one of {allowed}, got {dep_var!r}")

    # Fit mixed-effects model with group as fixed effect and image as random effect
    formula = f"{dep_var} ~ C(group)"
    model = smf.mixedlm(formula, df, groups=df['image_id'])
    result = model.fit()

    # Set up contrast testing framework
    groups = sorted(df['group'].unique())
    exog_names = result.model.exog_names
    idx_map = {name: idx for idx, name in enumerate(exog_names)}
    baseline = groups[0]  # First group serves as reference level
    
    # Validate and prepare comparison pairs
    if comparisons is not None:
        pairs = [(str(a), str(b)) for a, b in comparisons]
        # Check that all specified groups exist in the data
        for g1, g2 in pairs:
            if g1 not in groups or g2 not in groups:
                raise ValueError(f"Comparison ({g1}, {g2}) contains unknown group")
    else:
        # Test all possible pairwise combinations
        pairs = list(combinations(groups, 2))

    # Perform contrast testing for each comparison
    rows = []
    for g1, g2 in pairs:
        # Build contrast vector for testing g1 - g2 = 0
        cont = [0.0] * len(exog_names)
        if g1 != baseline:
            cont[idx_map[f"C(group)[T.{g1}]"]] = 1.0
        if g2 != baseline:
            cont[idx_map[f"C(group)[T.{g2}]"]] = -1.0

        # Convert to required 2D array format and run test
        contrast = np.array(cont).reshape(1, -1)
        ct = result.t_test(contrast)

        # Extract test statistics and confidence intervals
        effect = ct.effect[0]
        se = ct.sd[0]
        t_value = ct.tvalue[0]
        p_value = float(ct.pvalue)
        ci_lower, ci_upper = ct.conf_int()[0]

        rows.append({
            'group1': g1,
            'group2': g2,
            'estimate': effect,
            'se': se,
            't_value': t_value,
            'p_value': p_value,
            'ci_lower': ci_lower,
            'ci_upper': ci_upper
        })

    results_df = pd.DataFrame(rows)

    # Apply multiple testing correction to p-values
    if not results_df.empty:
        _, p_adj, _, _ = multipletests(results_df['p_value'], method=p_adjust_method)
        results_df['p_value_adj'] = p_adj

    return results_df