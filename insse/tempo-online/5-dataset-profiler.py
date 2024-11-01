import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Dict, Any, List
import os

class NumpyEncoder(json.JSONEncoder):
    """Custom encoder for numpy data types"""
    def default(self, obj):
        if isinstance(obj, (np.int_, np.intc, np.intp, np.int8,
                          np.int16, np.int32, np.int64, np.uint8,
                          np.uint16, np.uint32, np.uint64)):
            return int(obj)
        elif isinstance(obj, (np.float_, np.float16, np.float32, np.float64)):
            return float(obj)
        elif isinstance(obj, (np.bool_)):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class CSVProfiler:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.df = pd.read_csv(file_path)
        
    def _detect_value_column(self) -> str:
        """Detect the main value column (usually the last numeric column)"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            return numeric_cols[-1]
        return None

    def _analyze_column(self, column: pd.Series) -> Dict[str, Any]:
        """Analyze a single column"""
        result = {
            "unique_count": int(column.nunique()),
            "null_count": int(column.isnull().sum()),
            "total_count": len(column)
        }
        
        # Detect type
        if pd.api.types.is_numeric_dtype(column):
            result["type"] = "numeric"
            non_null = column.dropna()
            if len(non_null) > 0:
                result.update({
                    "min": float(non_null.min()),
                    "max": float(non_null.max()),
                    "mean": float(non_null.mean()),
                    "median": float(non_null.median())
                })
        else:
            # Get value frequencies for categorical data
            value_counts = column.value_counts()
            
            # Check if it might be a date
            if (column.name.lower().find('date') >= 0 or 
                column.name.lower().find('time') >= 0):
                try:
                    pd.to_datetime(column.dropna().head())
                    result["type"] = "datetime"
                except:
                    result["type"] = "categorical"
            # Check if it might be an ID
            elif (column.name.lower().find('id') >= 0 and 
                  result["unique_count"] / len(self.df) > 0.8):
                result["type"] = "id"
            else:
                result["type"] = "categorical"
            
            # Store value frequencies (top 10)
            if result["type"] == "categorical":
                value_counts_dict = {}
                for value, count in value_counts.head(10).items():
                    value_counts_dict[str(value)] = int(count)
                result["value_counts"] = value_counts_dict
                result["other_count"] = int(value_counts[10:].sum()) if len(value_counts) > 10 else 0
        
        return result

    def generate_profile(self) -> Dict[str, Any]:
        """Generate complete profile of the CSV file"""
        filesize = os.path.getsize(self.file_path)
        
        profile = {
            "file_stats": {
                "filename": os.path.basename(self.file_path),
                "row_count": len(self.df),
                "column_count": len(self.df.columns),
                "file_size_bytes": filesize,
                "file_size_mb": round(filesize / (1024 * 1024), 2)
            },
            "value_column": self._detect_value_column(),
            "columns": {}
        }
        
        # Profile each column
        for column in self.df.columns:
            profile["columns"][str(column)] = self._analyze_column(self.df[column])
        
        return profile

def process_directory(input_dir: str, output_dir: str):
    """Process all CSV files in a directory and generate profiles"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    csv_files = list(input_path.glob('*.csv'))
    total_files = len(csv_files)
    
    print(f"Found {total_files} CSV files to process")
    
    for i, csv_file in enumerate(csv_files, 1):
        try:
            print(f"Processing {i}/{total_files}: {csv_file.name}")
            
            # Generate profile
            profiler = CSVProfiler(str(csv_file))
            profile = profiler.generate_profile()
            
            # Save profile
            output_file = output_path / f"{csv_file.stem}_profile.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, cls=NumpyEncoder)
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")

if __name__ == "__main__":
    input_dir = "data/3-datasets/ro"
    input_dir = "/Users/pax/devbox/gov2/scrapers2/insse/tempo-online/data/_obsolete/csv"
    output_dir = "4-meta/ro"
    
    process_directory(input_dir, output_dir)
    print("Processing complete!")