""" 
    reverse order of the fields separated by | in column B (labels)
"""

file_path = 'data/_obsolete/Tempo Online ctgs & filters.xlsx - dimension_labels.csv'  # Replace with the path to your file
output_path = 'data/_obsolete/tempo-online-options-reversed-dimLabels.csv'  # Replace with your desired output file name

import pandas as pd

# Load your CSV or Excel file

df = pd.read_csv(file_path)  # Use `pd.read_excel` if the file is an Excel file

# Reverse the order of fields in the 'labels' column
df['labels'] = df['labels'].apply(lambda x: '|'.join(x.split('|')[::-1]))

# Save the modified dataframe back to a new file

df.to_csv(output_path, index=False)

print(f"File saved to {output_path}")
