import pandas as pd
import statsmodels.formula.api as smf
from itertools import combinations
import numpy as np


def run_mixed_lme(df: pd.DataFrame,
                  dep_var: str = 'fracIn') -> pd.DataFrame:
    """
    Run a random-intercepts mixed-effects model comparing groups on a chosen outcome
    and return a DataFrame of all pairwise group contrasts.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: 'image_id', 'file', 'series', 'group', 'intIn', 'intTot', 'fracIn'.
    dep_var : str
        One of 'intIn', 'intTot', 'fracIn'.

    Returns
    -------
    pd.DataFrame
        Contains: group1, group2, estimate, se, t_value, p_value, ci_lower, ci_upper.
    """
    # Validate dependent variable
    allowed = {'intIn', 'intTot', 'fracIn'}
    if dep_var not in allowed:
        raise ValueError(f"dep_var must be one of {allowed}, got {dep_var!r}")

    # Fit the mixed-effects model
    formula = f"{dep_var} ~ C(group)"
    model = smf.mixedlm(formula, df, groups=df['image_id'])
    result = model.fit()

    # Prepare pairwise contrasts
    groups = sorted(df['group'].unique())
    exog_names = result.model.exog_names
    idx_map = {name: idx for idx, name in enumerate(exog_names)}
    baseline = groups[0]

    rows = []
    for g1, g2 in combinations(groups, 2):
        # Build contrast vector
        cont = [0.0] * len(exog_names)
        if g1 != baseline:
            cont[idx_map[f"C(group)[T.{g1}]"]] = 1.0
        if g2 != baseline:
            cont[idx_map[f"C(group)[T.{g2}]"]] = -1.0

        # Convert to 2D array for t_test
        contrast = np.array(cont).reshape(1, -1)
        ct = result.t_test(contrast)

        # Extract stats
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
    return 