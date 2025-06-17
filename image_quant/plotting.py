import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def plot_barplot_fracin(df, show = True):
    """
    Plots a barplot of average 'fracin' per image grouped by 'group' with a 95% CI.
    
    Parameters:
        df (pandas.DataFrame): A dataframe containing columns:
                               'image_id', 'file', 'series', 'group', 'fracin', 'sample_size'.
    """
    # Aggregate to get the average 'fracin' per image for each group
    df_agg = df.groupby(['image_id', 'group'], as_index=False)['fracin'].mean()
    
    # Create the barplot
    plt.figure(figsize=(8, 6))
    sns.barplot(x='group', y='fracin', data=df_agg, ci=95)
    plt.xlabel('Group')
    plt.ylabel('Average fracin per image')
    plt.title('Average Fracin by Group with 95% CI')
    plt.tight_layout()
    
    if show:
        # Show the plot if requested
        plt.show()
    
    return plt.gcf()  # Return the current figure for further use if needed
