# LSD1 Sequestration Image Quantification

A Python pipeline for analyzing fluorescence microscopy data to quantify LSD1 protein sequestration in response to tau protein treatments. This tool processes Fiji/ImageJ output files, performs statistical analysis using mixed-effects models, and generates publication-ready visualizations with significance testing.

## Overview

This analysis pipeline was developed to study LSD1 (Lysine-Specific Demethylase 1) protein localization changes in cellular models. The software takes fluorescence intensity measurements from microscopy images and applies rigorous statistical methods to compare experimental conditions.

### Key Features

- **Automated data preprocessing** from Fiji/ImageJ CSV exports
- **Mixed-effects statistical modeling** to account for image-level variation
- **Multiple comparison correction** using established methods (Holm, Bonferroni, etc.)
- **Publication-ready plots** with automated significance bar placement
- **Reproducible analysis** with configuration management and timestamped outputs

## Installation

### Prerequisites

- Python 3.8 or higher
- Virtual environment (recommended)

### Setup

1. Clone this repository:
```bash
git clone https://github.com/Zbedd/LSD1Sequestration.git
cd LSD1Sequestration
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows PowerShell
# or
source .venv/bin/activate     # Linux/Mac
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Workflow

1. **Configure analysis parameters** in `config/default.yaml`
2. **Run the analysis pipeline** using the main script
3. **Review outputs** in the timestamped results folder

### Configuration

Edit `config/default.yaml` to specify:

```yaml
# Data paths
lsd1_image_group_path: 'path/to/your/images/'
fiji_seq_table_rel_path: 'your_fiji_output.csv'

# Analysis settings
display_plots: False
save_artifacts: True
output_path: 'path/to/save/results/'

# Optional group filtering
groups: ['A', 'B', 'C', 'D']  # Analyze only these groups

# Statistical comparisons
comparisons: [['A', 'B'], ['C', 'D']]  # Specific pairwise tests
```

### Running the Analysis

```bash
# Activate virtual environment first
.\.venv\Scripts\Activate.ps1

# Run the complete analysis pipeline
python scripts/quant_plot.py
```

### Expected Input Format

The pipeline expects Fiji/ImageJ CSV output with columns:
- `file`: Image filename (first character defines experimental group)
- `series`: Image series number
- `intIn`: Intensity inside region of interest
- `intTot`: Total intensity
- `fracIn`: Fraction of intensity inside (intIn/intTot)

## Output Structure

Results are saved in timestamped directories (YYYY-MM-DD format):

```
output_folder/
├── 2025-08-08/
│   ├── barplot_fracin_2025-08-08.png
│   ├── mixed_lme_results_2025-08-08.csv
│   └── default.txt  # Configuration snapshot
```

### Output Files

- **Bar plots**: Mean fracIn values per group with 95% confidence intervals and significance bars
- **Statistical results**: Complete mixed-effects model results with adjusted p-values
- **Configuration snapshot**: Copy of analysis parameters for reproducibility

## Analysis Methods

### Statistical Approach

The pipeline uses **random-intercepts mixed-effects models** to analyze group differences while accounting for image-level variation. This approach is appropriate for nested data where multiple measurements come from the same images.

**Model specification**: `fracIn ~ C(group) + (1|image_id)`

- Fixed effects: Experimental group
- Random effects: Image-level intercepts
- Multiple comparison correction: Holm method (default)

### Significance Testing

Statistical comparisons are visualized using horizontal bars with standard notation:
- `****` p < 0.0001
- `***` p < 0.001  
- `**` p < 0.01
- `*` p < 0.05
- `ns` not significant

## Project Structure

```
LSD1Sequestration/
├── config/
│   └── default.yaml          # Analysis configuration
├── image_quant/              # Main analysis package
│   ├── __init__.py
│   ├── fiji_output_preprocessing.py
│   ├── plotting.py
│   ├── stats.py
│   └── write.py
├── scripts/
│   └── quant_plot.py         # Main analysis script
├── requirements.txt          # Python dependencies
└── README.md
```

### Module Functions

- **`fiji_output_preprocessing`**: Data cleaning and standardization
- **`stats`**: Mixed-effects modeling and group comparisons
- **`plotting`**: Publication-ready visualizations with significance testing
- **`write`**: Output management and artifact saving

## Dependencies

Core scientific computing libraries:
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `matplotlib` - Plotting and visualization
- `seaborn` - Statistical data visualization
- `statsmodels` - Statistical modeling
- `PyYAML` - Configuration file handling

See `requirements.txt` for complete dependency list with versions.

## Customization

### Adding New Plot Types

Extend the `plotting` module with additional visualization functions:

```python
from image_quant import plotting

# Create custom plots
custom_plot = plotting.create_your_plot(data, parameters)
```

### Modifying Statistical Tests

The `stats` module supports different dependent variables and comparison methods:

```python
from image_quant import stats

# Analyze different measures
results = stats.run_mixed_lme(df, dep_var='intTot', p_adjust_method='bonferroni')
```

## Troubleshooting

### Common Issues

**Import errors**: Ensure virtual environment is activated and dependencies are installed
**File path errors**: Use absolute paths in configuration files
**Missing data columns**: Verify Fiji CSV output contains expected column names
**Statistical convergence**: Check for sufficient sample sizes in each group

### Getting Help

For analysis questions or technical issues:
1. Check that input data matches expected format
2. Verify configuration file syntax
3. Review error messages for specific guidance
4. Ensure adequate sample sizes for statistical testing

## Citation

If you use this pipeline in your research, please cite the associated publication and consider acknowledging the software:

```
LSD1 Sequestration Image Quantification Pipeline
GitHub: https://github.com/Zbedd/LSD1Sequestration
```

## License

This project is available under standard academic use terms. Please contact the authors for commercial applications.

## Contributing

Contributions are welcome through pull requests. Please ensure:
- Code follows existing style conventions
- Functions include comprehensive docstrings
- Changes are tested with sample data
- Documentation is updated accordingly

---

*Developed for LSD1 protein sequestration research in the Katz Laboratory*
