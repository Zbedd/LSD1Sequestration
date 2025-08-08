"""
File Output and Artifact Management Module

This module handles the saving of analysis results including dataframes, plots,
and configuration files. It creates dated output directories and provides
comprehensive logging of the analysis workflow.
"""

import os
from pathlib import Path
from datetime import datetime
import pandas as pd
from matplotlib.figure import Figure
from typing import List, Tuple, Union


def save_artifacts(
    dataframes: List[Tuple[str, pd.DataFrame]],
    plots: List[Tuple[str, Figure]],
    base_path: Union[str, Path]
) -> Path:
    """
    Create a dated output directory and save analysis artifacts.

    Organizes all analysis outputs into a timestamped folder for reproducibility
    and version control. Saves dataframes as CSV files, plots as PNG images,
    and includes a copy of the configuration file for reference.

    Parameters
    ----------
    dataframes : list of (name, pd.DataFrame)
        Tuples of filename (without extension) and DataFrame to save.
        None entries are skipped with a warning.
    plots : list of (name, matplotlib.figure.Figure)
        Tuples of filename and Figure object to save as PNG.
        None entries are skipped with a warning.
    base_path : str or Path
        Root directory where the dated output folder will be created.

    Returns
    -------
    Path
        Path to the created output directory containing all artifacts.
        
    Notes
    -----
    The output directory is named with the current date (YYYY-MM-DD format).
    Configuration files are automatically copied for analysis provenance.
    """
    base = Path(base_path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = base / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save statistical results and processed data as CSV files
    for name, df in dataframes:
        if df is None:
            print(f"Warning: DataFrame '{name}' is None, skipping.")
            continue
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame for '{name}', got {type(df)}")
        file_path = out_dir / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"Saved DataFrame '{name}' to {file_path}")

    # Save plots as high-quality PNG images
    for name, fig in plots:
        if fig is None:
            print(f"Warning: Figure '{name}' is None, skipping.")
            continue
        if not isinstance(fig, Figure):
            raise TypeError(f"Expected matplotlib.figure.Figure for '{name}', got {type(fig)}")
        file_path = out_dir / f"{name}.png"
        fig.savefig(file_path, bbox_inches='tight')
        print(f"Saved plot '{name}' to {file_path}")
        
    # Copy configuration file for analysis provenance
    project_root = Path(__file__).resolve().parents[1]
    default_yaml_path = project_root / "config" / "default.yaml"
    default_txt_path  = out_dir / "default.txt"

    if default_yaml_path.is_file():
        # Read and copy configuration settings to output directory
        content = default_yaml_path.read_text(encoding="utf-8")
        default_txt_path.write_text(content, encoding="utf-8")
        print(f"Copied {default_yaml_path} → {default_txt_path}")
    else:
        print(f"Warning: Could not find {default_yaml_path}, skipping default.txt")
    
    return out_dir