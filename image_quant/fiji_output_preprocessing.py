"""
Fiji/ImageJ Output Preprocessing Module

This module handles the preprocessing of CSV files exported from Fiji/ImageJ
fluorescence intensity measurements. It standardizes column names, extracts
experimental group information, and aggregates measurements per image.
"""

import pandas as pd

def preprocess_fiji_csv(csv_path: str) -> pd.DataFrame:
    """
    Clean and standardize Fiji CSV output for downstream analysis.
    
    Reads a CSV file from Fiji/ImageJ containing fluorescence measurements
    and adds derived columns for experimental grouping and image identification.
    
    Parameters
    ----------
    csv_path : str
        Path to the Fiji CSV output file.
    
    Returns
    -------
    pd.DataFrame
        Processed dataframe with columns:
        'image_id', 'file', 'series', 'group', 'intIn', 'intTot', 'fracIn'
        
    Notes
    -----
    - 'group' is extracted as the first character of the filename
    - 'image_id' combines file base name (up to second underscore) with series
    """
    # Read CSV and handle potential empty column issues
    df = pd.read_csv(csv_path, sep=',')
    if ' ' in df.columns:
        df = df.drop(' ', axis=1)
    
    # Extract experimental group from filename (first character)
    df['group'] = df['file'].str[0]
    
    # Create unique image identifier from filename and series
    def extract_image_id(file_value, series_value):
        """Create a unique image ID from file name and series number."""
        # Split on underscores and reconstruct base name
        parts = file_value.split('_')
        if len(parts) >= 2:
            base = '_'.join(parts[:2])
        else:
            base = file_value  # fallback if filename format is unexpected
        return f"{base}_{series_value}"
    
    df['image_id'] = df.apply(lambda row: extract_image_id(row['file'], row['series']), axis=1)
    
    # Reorder columns to put key identifiers first
    start_order = ['image_id', 'file', 'series', 'group']
    cols = start_order + [col for col in df.columns if col not in start_order]
    df = df[cols]
    
    return df

def collapse_fracIn(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate multiple measurements per image to single values.
    
    Groups measurements by image_id and calculates mean fracIn values.
    This is necessary for statistical analysis where each image should
    contribute one data point rather than multiple ROI measurements.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe with multiple rows per image.
    
    Returns
    -------
    pd.DataFrame
        Aggregated dataframe with columns:
        'image_id', 'file', 'series', 'group', 'fracIn', 'sample_size'
        
    Notes
    -----
    sample_size indicates the number of original measurements per image
    """
    # Group by image and aggregate metadata and measurements
    grouped = df.groupby('image_id').agg({
        'file': 'first',         # Keep first occurrence of metadata
        'series': 'first',
        'group': 'first',
        'fracIn': 'mean'         # Average the intensity measurements
    })
    
    # Track how many original measurements went into each averaged value
    grouped['sample_size'] = df.groupby('image_id').size()
    
    # Reset index to make image_id a regular column
    return grouped.reset_index()