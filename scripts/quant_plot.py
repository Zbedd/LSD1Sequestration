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

def main(cfg):
    # Preprocess the Fiji CSV file
    base_path = cfg['lsd1_image_group_path']
    csv_rel_path = cfg['fiji_seq_table_rel_path']
    csv_path = os.path.join(base_path, csv_rel_path)
        
    df = fiji_preprocess.preprocess_fiji_csv(csv_path)
    df_collapsed_to_img = fiji_preprocess.collapse_fracin(df)
    
    plotting.plot_barplot_fracin(df_collapsed_to_img)

    
    # # Save the preprocessed DataFrame to a new CSV file
    # output_csv_path = cfg['output_csv_path']
    # df.to_csv(output_csv_path, index=False)
    
    # print(f"Preprocessed data saved to {output_csv_path}")

if __name__ == "__main__":
    with open('config/default.yaml', 'r') as file:
        cfg = yaml.safe_load(file)
        
    main(cfg)
