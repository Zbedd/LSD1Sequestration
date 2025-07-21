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
    dataframes : list of (name, pd.DataFrame)
        Tuples of filename (no extension) and DataFrame; None entries will be skipped.
    plots : list of (name, matplotlib.figure.Figure)
        Tuples of filename and Figure; None entries will be skipped.
    base_path : str or Path
        Root folder under which the dated folder will be created.

    Returns
    -------
    Path
        Path of the created output directory.
    """
    base = Path(base_path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    out_dir = base / date_str
    out_dir.mkdir(parents=True, exist_ok=True)

    # Save dataframes
    for name, df in dataframes:
        if df is None:
            print(f"Warning: DataFrame '{name}' is None, skipping.")
            continue
        if not isinstance(df, pd.DataFrame):
            raise TypeError(f"Expected pandas DataFrame for '{name}', got {type(df)}")
        file_path = out_dir / f"{name}.csv"
        df.to_csv(file_path, index=False)
        print(f"Saved DataFrame '{name}' to {file_path}")

    # Save plots
    for name, fig in plots:
        if fig is None:
            print(f"Warning: Figure '{name}' is None, skipping.")
            continue
        if not isinstance(fig, Figure):
            raise TypeError(f"Expected matplotlib.figure.Figure for '{name}', got {type(fig)}")
        file_path = out_dir / f"{name}.png"
        fig.savefig(file_path, bbox_inches='tight')
        print(f"Saved plot '{name}' to {file_path}")
        
    project_root = Path(__file__).resolve().parents[1]
    default_yaml_path = project_root / "config" / "default.yaml"
    default_txt_path  = out_dir / "default.txt"

    if default_yaml_path.is_file():
        # read & write in one go:
        content = default_yaml_path.read_text(encoding="utf-8")
        default_txt_path.write_text(content, encoding="utf-8")
        print(f"Copied {default_yaml_path} → {default_txt_path}")
    else:
        print(f"⚠️  Could not find {default_yaml_path}, skipping default.txt")
    
    return out_dir