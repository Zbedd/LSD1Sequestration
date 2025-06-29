import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def _star_string(p: float) -> str:
    """Return significance stars for a p-value."""
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
    """Draw significance bars with stars on ``ax`` using ``stats_df``.

    Parameters
    ----------
    ax : matplotlib.axes.Axes
        Axis containing a bar plot grouped by ``group``.
    stats_df : pandas.DataFrame
        DataFrame produced by ``run_mixed_lme`` with columns ``group1``,
        ``group2`` and ``p_value_adj``.
    alpha : float, default 0.05
        Only comparisons with ``p_value_adj`` (or ``p_value`` if absent)
        below this threshold are plotted.
    """

    groups = [t.get_text() for t in ax.get_xticklabels()]
    pos = {g: i for i, g in enumerate(groups)}
    bars = {g: ax.patches[i].get_height() for i, g in enumerate(groups)}

    # Account for error bars by using the highest y-position of the
    # vertical line associated with each bar. ``ax.lines`` will contain
    # three Line2D objects when ``sns.barplot`` draws error bars.  Each
    # line corresponds to the vertical part of the error bar at a given
    # x-position.
    for line in ax.lines:
        xdata = line.get_xdata()
        ydata = line.get_ydata()
        if len(xdata) == 2 and xdata[0] == xdata[1]:
            idx = int(round(xdata[0]))
            if 0 <= idx < len(groups):
                g = groups[idx]
                bars[g] = max(bars[g], float(ydata.max()))

    y_range = ax.get_ylim()[1] - ax.get_ylim()[0]
    line_height = 0.05 * y_range
    # distance between the top of the tallest bar in a comparison and the
    # start of its significance bar
    offset = 0.02 * y_range
    # additional space above each bar for the star text
    text_offset = 0.01 * y_range

    used: list[tuple[int, int, int]] = []
    max_y = 0.0

    for _, row in stats_df.iterrows():
        p = row.get("p_value_adj", row.get("p_value"))
        if not pd.notna(p) or p >= alpha:
            continue

        g1, g2 = str(row["group1"]), str(row["group2"])
        if g1 not in pos or g2 not in pos:
            continue
        x1, x2 = sorted([pos[g1], pos[g2]])

        level = 0
        for a1, a2, lvl in used:
            if not (x2 < a1 or x1 > a2):
                level = max(level, lvl + 1)
        used.append((x1, x2, level))

        y = max(bars[g1], bars[g2]) + offset + level * (line_height + text_offset)        
        bar_x = [x1, x1, x2, x2]
        bar_y = [y, y + line_height * 0.2, y + line_height * 0.2, y]
        ax.plot(bar_x, bar_y, c="k", lw=1.5)
        ax.text((x1 + x2) / 2, y + line_height * 0.2 + text_offset,
                _star_string(row.get("p_value_adj", row.get("p_value"))),
                ha="center", va="bottom", color="k")

        max_y = max(max_y, y + line_height * 0.2 + text_offset)

    if max_y > ax.get_ylim()[1]:
        ax.set_ylim(top=max_y + offset)
        
def plot_barplot_fracIn(df, show: bool = True, stats_df: pd.DataFrame | None = None):    
    """
    Plots a barplot of average 'fracIn' per image grouped by 'group' with a 95% CI.
    
    Parameters:
        df (pandas.DataFrame): A dataframe containing columns:
                               'image_id', 'file', 'series', 'group', 'fracIn', 'sample_size'.
    """
    # Aggregate to get the average 'fracIn' per image for each group
    df_agg = df.groupby(['image_id', 'group'], as_index=False)['fracIn'].mean()
    
    # Create the barplot
    plt.figure(figsize=(8, 6))
    ax = sns.barplot(x='group', y='fracIn', data=df_agg, ci=95)    
    plt.xlabel('Group')
    plt.ylabel('Average fracIn per image')
    plt.title('Average fracIn by Group with 95% CI')
    plt.tight_layout()
    
    if stats_df is not None:
        _add_significance_bars(ax, stats_df)

    if show:
        # Show the plot if requested
        plt.show()
    
    return plt.gcf()  # Return the current figure for further use if needed
