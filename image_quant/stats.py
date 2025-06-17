import pandas as pd
import statsmodels.formula.api as smf
from itertools import combinations

'''
Conceptually:
    intIn represents nuclear intensity of LSD1,
    intTot represents total intensity of LSD1,
    fracIn represents nuclear localization of LSD1,
'''

def run_mixed_lme(df: pd.DataFrame,
                  dep_var: str = 'fracIn') -> pd.DataFrame:
    """
    Run a random-intercepts mixed-effects model comparing groups on a chosen outcome.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: 'image_id', 'file', 'series', 'group', 'intIn', 'intTot', 'fracIn'.
    dep_var : str, default 'fracIn'
        Which column to model: one of 'intIn', 'intTot', 'fracIn'.

    Returns
    -------
    pd.DataFrame
        One row per pairwise group comparison, with estimate, SE, t, p, and 95% CI.
    """
    # Validate dependent variable
    allowed = ['intIn', 'intTot', 'fracIn']
    if dep_var not in allowed:
        raise ValueError(f"dep_var must be one of {allowed}")

    # Fit the mixed model
    formula = f"{dep_var} ~ C(group)"
    model = smf.mixedlm(formula, df, groups=df['image_id'])
    result = model.fit()

    # Prepare for pairwise contrasts
    groups = sorted(df['group'].unique())
    exog_names = result.model.exog_names
    name_idx = {name: idx for idx, name in enumerate(exog_names)}
    baseline = groups[0]

    comparisons = []
    for g1, g2 in combinations(groups, 2):
        # Build contrast: E[g1] - E[g2]
        contrast = [0.0] * len(exog_names)
        # Add +1 for g1 if not baseline
        if g1 != baseline:
            contrast[name_idx[f"C(group)[T.{g1}]"]] = 1.0
        # Add -1 for g2 if not baseline
        if g2 != baseline:
            contrast[name_idx[f"C(group)[T.{g2}]"]] = -1.0

        ct = result.t_test(contrast)
        est = ct.effect[0]
        se  = ct.sd[0]
        tval = ct.tvalue[0]
        pval = float(ct.pvalue)
        ci_low, ci_high = ct.conf_int()[0]

        comparisons.append({
            'group1': g1,
            'group2': g2,
            'estimate': est,
            'se': se,
            't_value': tval,
            'p_value': pval,
            'ci_lower': ci_low,
            'ci_upper': ci_high
        })

    results_df = pd.DataFrame(comparisons)
    return results_df