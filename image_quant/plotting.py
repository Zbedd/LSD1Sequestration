"""
Scientific Plotting Module for Image Quantification

This module provides publication-ready plotting functions with statistical
significance annotations. It specializes in creating bar plots with error bars
and significance testing results displayed as horizontal bars with star notation.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def _star_string(p: float) -> str:
    """
    Convert p-value to standard significance star notation.
    
    Parameters
    ----------
    p : float
        P-value to convert.
        
    Returns
    -------
    str
        Star notation: '****' for p<0.0001, '***' for p<0.001, 
        '**' for p<0.01, '*' for p<0.05, 'ns' for non-significant.
    """
    if p < 0.0001:
        return "****"
    elif p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    return "ns"


def _add_significance_bars(ax: plt.Axes, stats_df: pd.DataFrame, *, alpha: float = 0.05) -> None:
    """
    Add horizontal significance bars with star annotations to a bar plot.

    Automatically positions significance bars above error bars and handles
    multiple comparisons by stacking bars at different vertical levels.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis containing a bar plot grouped by category.
    stats_df : pandas.DataFrame
        Statistical results with columns 'group1', 'group2' and 'p_value_adj'
        (or 'p_value' as fallback).
    alpha : float, default 0.05
        Significance threshold. Only comparisons below this p-value are shown.
        
    Notes
    -----
    The function automatically detects error bars and positions significance
    bars appropriately above them. Multiple comparisons are stacked vertically.
    """
    # Map group names to x-axis positions
    groups = [t.get_text() for t in ax.get_xticklabels()]
    pos = {g: i for i, g in enumerate(groups)}
    bars = {g: ax.patches[i].get_height() for i, g in enumerate(groups)}

    # Account for error bars by finding the highest point of each error bar
    # Error bars appear as Line2D objects when seaborn draws them
    for line in ax.lines:
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        # Error bars have vertical lines (same x-coordinate for both points)
        if len(xdata) == 2 and xdata[0] == xdata[1]:
            idx = int(round(xdata[0]))
            if 0 <= idx < len(groups):
                g = groups[idx]
                # Update bar height to include error bar extent
                bars[g] = max(bars[g], float(ydata.max()))

    # Calculate spacing for significance bars
    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    line_height = 0.05 * y_range      # Height of horizontal significance bars
    offset = 0.02 * y_range           # Space between tallest bar and first sig bar
    text_offset = 0.01 * y_range      # Space above bar for star text

    # Track occupied vertical space to avoid overlapping bars
    used: list[tuple[int, int, int]] = []  # (x1, x2, level)
    max_y = 0.0

    # Draw significance bars for each significant comparison
    for _, row in stats_df.iterrows():
        p = row.get("p_value_adj", row.get("p_value"))
        if not pd.notna(p) or p >= alpha:
            continue

        g1, g2 = str(row["group1"]), str(row["group2"])
        if g1 not in pos or g2 not in pos:
            continue
        x1, x2 = sorted([pos[g1], pos[g2]])

        # Find appropriate vertical level to avoid overlaps
        level = 0
        for a1, a2, lvl in used:
            # Check if this comparison overlaps with existing ones
            if not (x2 < a1 or x1 > a2):
                level = max(level, lvl + 1)
        used.append((x1, x2, level))

        # Calculate y-position based on highest bar in comparison and level
        y = max(bars[g1], bars[g2]) + offset + level * (line_height + text_offset)        
        
        # Draw horizontal bar with short vertical connectors
        bar_x = [x1, x1, x2, x2]
        bar_y = [y, y + line_height * 0.2, y + line_height * 0.2, y]
        ax.plot(bar_x, bar_y, c="k", lw=1.5)
        
        # Add significance stars centered above the bar
        ax.text((x1 + x2) / 2, y + line_height * 0.2 + text_offset,
                _star_string(row.get("p_value_adj", row.get("p_value"))),
                ha="center", va="bottom", color="k")

        max_y = max(max_y, y + line_height * 0.2 + text_offset)

    # Extend y-axis if needed to accommodate significance bars
    if max_y > ax.get_ylim()[1]:
        ax.set_ylim(top=max_y + offset)
        
def plot_barplot_fracIn(df, show: bool = True, stats_df: pd.DataFrame | None = None):    
    """
    Create a bar plot of fraction intensities with error bars and significance testing.
    
    Generates a publication-ready bar plot showing mean fracIn values per group
    with 95% confidence intervals. If statistical results are provided, adds
    horizontal significance bars with star notation.
    
    Parameters
    ----------
    df : pandas.DataFrame
        Dataframe containing columns: 'image_id', 'group', 'fracIn'.
        Should be aggregated so each image contributes one data point.
    show : bool, default True
        Whether to display the plot immediately.
    stats_df : pandas.DataFrame, optional
        Statistical comparison results from mixed-effects analysis.
        Must contain 'group1', 'group2', and 'p_value_adj' columns.
        
    Returns
    -------
    matplotlib.figure.Figure
        The generated figure object for saving or further customization.
        
    Notes
    -----
    The function expects data aggregated to one value per image. Error bars
    represent 95% confidence intervals of the mean.
    """
    # Create the bar plot with confidence intervals
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x='group', y='fracIn', data=df, ci=95)    
    plt.xlabel('Group')
    plt.ylabel('Average fracIn per image')
    plt.title('Average fracIn by Group with 95% CI')
    plt.tight_layout()
    
    # Add significance testing results if provided
    if stats_df is not None:
        _add_significance_bars(ax, stats_df)

    if show:
        plt.show()
    
    return plt.gcf()  # Return figure for saving or further manipulation
