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

    def _is_year(self, value: str) -> bool:
        """Check if a string represents a year after removing 'anul' prefix"""
        cleaned = str(value).lower().replace('anul', '').strip()
        try:
            year = int(cleaned)
            return 1900 <= year <= 2100  # reasonable year range
        except (ValueError, TypeError):
            return False

    def _detect_semantic_type(self, column_name: str) -> List[str]:
        """Detect semantic type based on column name patterns"""
        column_name = column_name.lower()
        semantic_types = []
        
        # Time-related terms
        time_terms = ["perioade", "luni", "trimestre", "ani"]
        if any(term.lower() in column_name for term in time_terms):
            semantic_types.append("time")
            
        # Geographic terms
        geo_terms = ["localitati", "regiuni", "municipii", "orase", "tari", "continente"]
        if any(term.lower() in column_name for term in geo_terms):
            semantic_types.append("geo")
            
        # Demographic terms
        demo_terms = ["varsta", "sexe"]
        if any(term.lower() in column_name for term in demo_terms):
            semantic_types.append("demographics")
            
        # Unit of measure
        if "um:" in column_name:
            semantic_types.append("um")
            
        # Percentage
        if "procent" in column_name:
            semantic_types.append("procent")
            
        return semantic_types

    def _analyze_column(self, column: pd.Series) -> Dict[str, Any]:
        """Analyze a single column"""
        result = {
            "unique_count": int(column.nunique()),
            "null_count": int(column.isnull().sum()),
            "total_count": len(column)
        }
        
        # Detect semantic type based on column name
        semantic_types = self._detect_semantic_type(str(column.name))
        if semantic_types:
            result["type2"] = ",".join(semantic_types)
        
        # Check for years with "anul" prefix
        if not pd.api.types.is_numeric_dtype(column):
            non_null = column.dropna()
            if len(non_null) > 0:
                years_count = sum(1 for val in non_null if self._is_year(val))
                if years_count / len(non_null) > 0.8:  # 80% or more are years
                    if "type2" not in result:
                        result["type2"] = "time,years"
                    else:
                        result["type2"] += ",years"

    def _is_numeric_string(self, value: str) -> bool:
        """Check if a string represents a number, handling spaces and thousands separators"""
        # Remove spaces and replace comma thousands separator
        cleaned = str(value).strip().replace(' ', '').replace(',', '')
        try:
            float(cleaned)
            return True
        except (ValueError, TypeError):
            return False

    def _analyze_column(self, column: pd.Series) -> Dict[str, Any]:
        """Analyze a single column"""
        result = {
            "unique_count": int(column.nunique()),
            "null_count": int(column.isnull().sum()),
            "total_count": len(column)
        }
        
        # Detect semantic type based on column name
        semantic_types = self._detect_semantic_type(str(column.name))
        if semantic_types:
            result["type2"] = ",".join(semantic_types)
        
        # Enhanced numeric detection
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
            # Check if it's a string column that might contain numeric values
            non_null = column.dropna()
            if len(non_null) > 0:
                numeric_count = sum(1 for val in non_null if self._is_numeric_string(val))
                numeric_percentage = numeric_count / len(non_null)
                
                if numeric_percentage >= 0.8:  # 80% or more are numeric
                    result["type"] = "numeric+"
                    result["warnings"] = f"{round((1-numeric_percentage)*100, 1)}% non-numeric values"
                    
                    # Convert numeric values for statistics
                    numeric_values = []
                    for val in non_null:
                        try:
                            cleaned = str(val).strip().replace(' ', '').replace(',', '')
                            numeric_values.append(float(cleaned))
                        except (ValueError, TypeError):
                            continue
                    
                    if numeric_values:
                        result.update({
                            "min": min(numeric_values),
                            "max": max(numeric_values),
                            "mean": sum(numeric_values) / len(numeric_values),
                            "median": sorted(numeric_values)[len(numeric_values)//2]
                        })
                else:
                    # Original categorical/datetime detection logic
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
    input_path = Path(input_dir).resolve()
    output_path = Path(output_dir).resolve()
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Input directory: {input_path}")
    print(f"Output directory: {output_path}")
    
    csv_files = list(input_path.glob('*.csv'))
    total_files = len(csv_files)
    
    print(f"Found {total_files} CSV files to process")
    
    for i, csv_file in enumerate(csv_files, 1):
        try:
            # print(f"Processing {i}/{total_files}: {csv_file.name}")
            
            # Generate profile
            profiler = CSVProfiler(str(csv_file))
            profile = profiler.generate_profile()
            
            # Save profile
            output_file = output_path / f"{csv_file.stem}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, indent=2, cls=NumpyEncoder)
            # print(f"  -- {output_file}")
            print(f"  -- {csv_file.stem}")
                
        except Exception as e:
            print(f"Error processing {csv_file.name}: {str(e)}")

 
 
if __name__ == "__main__":
    # Get the absolute path of the script's directory
    script_dir = Path(__file__).parent.resolve()
    
    # Construct absolute paths for input and output directories
    input_dir = "data/_obsolete/csv"
    output_dir = "data/4-meta/ro"
    
    process_directory(str(input_dir), str(output_dir))
    print("\nProcessing complete!")
    print(f"Profiles have been saved to: {output_dir}")