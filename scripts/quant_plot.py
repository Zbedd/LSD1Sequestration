#Activate virtual environment before running this script
#.\.venv\Scripts\Activate.ps1

import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path
import sys

module_dir = Path(__file__).resolve().parents[1]
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
      
from image_quant import fiji_output_preprocessing as fiji_preprocess
from image_quant import plotting
from image_quant import stats

def main(cfg):
    # Preprocess the Fiji CSV file
    base_path = cfg['lsd1_image_group_path']
    csv_rel_path = cfg['fiji_seq_table_rel_path']
    csv_path = os.path.join(base_path, csv_rel_path)
        
    df = fiji_preprocess.preprocess_fiji_csv(csv_path)

    groups = cfg.get('groups')
    if groups:
        df = df[df['group'].isin(groups)]

    df_collapsed_to_img = fiji_preprocess.collapse_fracIn(df)
    
    # Statistics
    comparisons = cfg.get('comparisons')
    mixed_lme_results = stats.run_mixed_lme(df, comparisons=comparisons)

    # Plots
    display_plots = cfg.get('display_plots', False)
    barplot_fracin = plotting.plot_barplot_fracIn(
        df_collapsed_to_img,
        show=display_plots,
        stats_df=mixed_lme_results,
    )
    
    save_artifacts = cfg.get('save_artifacts', True)
    if save_artifacts:
        output_path = cfg.get('output_path', base_path)
        date = pd.to_datetime('today').strftime('%Y-%m-%d')
        
        # Sets file names for saving
        barplot_fracin_name = f"barplot_fracin_{date}"
        mixed_lme_results_name = f"mixed_lme_results_{date}"
        
        from image_quant import write
        write.save_artifacts(
            dataframes=[(mixed_lme_results_name, mixed_lme_results)],
            plots=[(barplot_fracin_name, barplot_fracin)],
            base_path=output_path
        )
    
if __name__ == "__main__":
    with open('config/default.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
        
    main(cfg)
