import pandas as pd
from collections import defaultdict

def pivot_labels_csv(input_csv, output_csv):
    """
    Pivot the labels CSV to show label counts and associated documents.
    """
    # Read the CSV file
    df = pd.read_csv(input_csv)
    
    # Initialize dictionaries to store label information
    label_counts = defaultdict(int)
    label_docs = defaultdict(set)
    
    # Process each row
    for _, row in df.iterrows():
        doc_id = row['id']
        # Split labels by | and process each label
        labels = str(row['labels']).split('|')
        for label in labels:
            label = label.strip()
            if label:  # Skip empty labels
                label_counts[label] += 1
                label_docs[label].add(doc_id)
    
    # Create lists for the new dataframe
    result_data = {
        'label': [],
        'count': [],
        'docs': []
    }
    
    # Build the result data
    for label in sorted(label_counts.keys()):
        result_data['label'].append(label)
        result_data['count'].append(label_counts[label])
        result_data['docs'].append(sorted(list(label_docs[label])))
    
    # Create and save the result dataframe
    result_df = pd.DataFrame(result_data)
    result_df.to_csv(output_csv, index=False)
    
    return result_df

# Example usage with the sample data
 

# Process the sample data and show first few rows
result = pivot_labels_csv('data/dimension_labels.csv', 'data/pivoted_labels.csv')
print("\nFirst few rows of the pivoted data:")
print(result.head())