import pandas as pd

def preprocess_fiji_csv(csv_path: str) -> pd.DataFrame:
    #Expected output columns:
    # 'image_id', 'file', 'series', 'group', 
    # 'intIn', 'intTot', 'fracIn'
    
    # Read CSV and rename columns to all lowercase.
    df = pd.read_csv(csv_path, sep=',')
    if ' ' in df.columns:
        df = df.drop(' ', axis=1)
    # Define new columns based on the existing ones.
    # 'group' is the first character of the file name.
    df['group'] = df['file'].str[0]
    
    # 'image_id' is constructed from the 'file' string up to the second underscore and appended with 'series'.
    def extract_image_id(file_value, series_value):
        # Split on '_' and reconstruct string until second underscore is reached.
        parts = file_value.split('_')
        if len(parts) >= 2:
            base = '_'.join(parts[:2])
        else:
            base = file_value  # fallback if less than 2 parts present
        return f"{base}_{series_value}"
    
    df['image_id'] = df.apply(lambda row: extract_image_id(row['file'], row['series']), axis=1)
    
    start_order = ['image_id', 'file', 'series', 'group']
    cols = start_order + [col for col in df.columns if col not in start_order]
    df = df[cols]
    
    return df

def collapse_fracIn(df: pd.DataFrame) -> pd.DataFrame:
    # Group rows by image_id, taking the first value for file, series, and group, and
    # calculating mean of fracIn
    # Output df has columns: image_id, file, series, group, fracIn, sample_size
    grouped = df.groupby('image_id').agg({
        'file': 'first',
        'series': 'first',
        'group': 'first',
        'fracIn': 'mean'
    })
    # Add sample_size as the number of rows for each image_id
    grouped['sample_size'] = df.groupby('image_id').size()
    # Return the new dataframe with the grouped image_id as a column.
    return grouped.reset_index()
