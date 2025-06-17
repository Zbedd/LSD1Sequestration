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
    Create a dated folder under base_path and save each DataFrame and plot into it.

    Parameters
    ----------
    dataframes : List of (name, DataFrame)
        Each tuple contains a desired filename (without extension) and the DataFrame to save.
    plots : List of (name, matplotlib.figure.Figure)
        Each tuple contains a desired filename (without extension) and the Figure to save.
    base_path : str or Path
        Root folder under which the dated folder will be created.

    Returns
    -------
    Path
        Path of the created output directory.
    """
    # Resolve base path and create dated directory
    base = Path(base_path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = base / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save dataframes
    for name, df in dataframes:
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame for '{name}', got {type(df)}")
        file_path = out_dir / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"Saved DataFrame '{name}' to {file_path}")

    # Save plots
    for name, fig in plots:
        if not isinstance(fig, Figure):
            raise TypeError(f"Expected matplotlib.figure.Figure for '{name}', got {type(fig)}")
        file_path = out_dir / f"{name}.png"
        fig.savefig(file_path, bbox_inches='tight')
        print(f"Saved plot '{name}' to {file_path}")

    return out_dir
