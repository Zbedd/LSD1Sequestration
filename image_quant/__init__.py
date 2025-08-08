"""
Image Quantification Analysis Package

This package provides a complete pipeline for analyzing fluorescence microscopy
data from Fiji/ImageJ. It handles data preprocessing, statistical analysis using
mixed-effects models, and publication-ready visualization with significance testing.

Main Components:
- fiji_output_preprocessing: Data cleaning and standardization
- stats: Mixed-effects statistical modeling and group comparisons  
- plotting: Publication-ready plots with significance annotations
- write: Output management and artifact saving

Typical Usage:
    import image_quant
    df = image_quant.fiji_output_preprocessing.preprocess_fiji_csv(csv_path)
    results = image_quant.stats.run_mixed_lme(df, comparisons=pairs)
    plot = image_quant.plot_barplot_fracIn(df, stats_df=results)
"""

from . import fiji_output_preprocessing, plotting, stats, write

from .plotting import plot_barplot_fracIn

__all__ = [
    'fiji_output_preprocessing',
    'plotting',
    'stats',
    'write',
    'plot_barplot_fracIn',
]
