"""
LSD1 Sequestration Image Quantification Analysis

This script processes fluorescence microscopy data from Fiji/ImageJ to analyze
LSD1 protein sequestration. It performs statistical comparisons between experimental
groups and generates publication-ready plots with significance testing.

Usage:
    Activate virtual environment: .\.venv\Scripts\Activate.ps1
    Run: python scripts/quant_plot.py

Configuration is read from config/default.yaml which specifies:
- Input file paths and experimental groups
- Statistical comparison pairs
- Output settings and artifact saving options
"""

import pandas as pd
import numpy as np
import yaml
import os
from pathlib import Path
import sys

# Add the parent directory to path so we can import our custom modules
module_dir = Path(__file__).resolve().parents[1]
if str(module_dir) not in sys.path:
    sys.path.insert(0, str(module_dir))
      
from image_quant import fiji_output_preprocessing as fiji_preprocess
from image_quant import plotting
from image_quant import stats

def main(cfg):
    """
    Main analysis pipeline for LSD1 sequestration quantification.
    
    Processes Fiji CSV output, applies group filtering, performs statistical
    analysis using mixed-effects models, and generates plots with significance bars.
    
    Parameters
    ----------
    cfg : dict
        Configuration dictionary loaded from YAML file containing paths,
        group specifications, and output settings.
    """
    # Load and preprocess the Fiji CSV file
    base_path = cfg['lsd1_image_group_path']
    csv_rel_path = cfg['fiji_seq_table_rel_path']
    csv_path = os.path.join(base_path, csv_rel_path)
        
    df = fiji_preprocess.preprocess_fiji_csv(csv_path)
    
    # Apply group filtering if specified in config
    groups = cfg.get('groups')
    if groups:
        df = df[df['group'].isin(groups)]
    
    # Collapse measurements to one value per image for statistical analysis
    df_collapsed_to_img = fiji_preprocess.collapse_fracIn(df)
    
    # Run statistical comparisons using mixed-effects models
    comparisons = cfg.get('comparisons')
    mixed_lme_results = stats.run_mixed_lme(df, comparisons=comparisons)

    # Generate plots with optional display
    display_plots = cfg.get('display_plots', False)
    
    # Save all analysis artifacts if requested
    save_artifacts = cfg.get('save_artifacts', True)
    if save_artifacts:
        output_path = cfg.get('output_path', base_path)
        date = pd.to_datetime('today').strftime('%Y-%m-%d')
        
        # Create descriptive file names with timestamps
        barplot_fracin_name = f"barplot_fracin_{date}"
        mixed_lme_results_name = f"mixed_lme_results_{date}"
        
        # Generate bar plot with significance testing results
        barplot_fracin = plotting.plot_barplot_fracIn(
            df_collapsed_to_img,
            show=display_plots,
            stats_df=mixed_lme_results,
            )
        
        # Save both statistical results and plots to dated folder
        from image_quant import write
        write.save_artifacts(
            dataframes=[(mixed_lme_results_name, mixed_lme_results)],
            plots=[(barplot_fracin_name, barplot_fracin)],
            base_path=output_path
        )
    
if __name__ == "__main__":
    # Load configuration settings from YAML file
    with open('config/default.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
        
    main(cfg)
