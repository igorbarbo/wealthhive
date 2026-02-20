"""
Data pipeline for ML
"""

from typing import Any, Dict

import pandas as pd


class DataPipeline:
    """ETL pipeline for ML data"""
    
    def __init__(self):
        self.steps = []
    
    def add_step(self, name: str, transform_func):
        """Add transformation step"""
        self.steps.append((name, transform_func))
    
    def run(self, data: pd.DataFrame) -> pd.DataFrame:
        """Execute pipeline"""
        result = data.copy()
        
        for name, transform in self.steps:
            print(f"Running step: {name}")
            result = transform(result)
        
        return result
    
    def create_default_pipeline(self) -> "DataPipeline":
        """Create default preprocessing pipeline"""
        pipeline = DataPipeline()
        
        # Add default steps
        pipeline.add_step("drop_na", lambda df: df.dropna())
        pipeline.add_step("remove_outliers", self._remove_outliers)
        pipeline.add_step("normalize", self._normalize)
        
        return pipeline
    
    @staticmethod
    def _remove_outliers(df: pd.DataFrame, threshold: float = 3.0) -> pd.DataFrame:
        """Remove statistical outliers"""
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        
        for col in numeric_cols:
            mean = df[col].mean()
            std = df[col].std()
            df = df[abs(df[col] - mean) < threshold * std]
        
        return df
    
    @staticmethod
    def _normalize(df: pd.DataFrame) -> pd.DataFrame:
        """Min-max normalization"""
        numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns
        
        for col in numeric_cols:
            min_val = df[col].min()
            max_val = df[col].max()
            if max_val > min_val:
                df[col] = (df[col] - min_val) / (max_val - min_val)
        
        return df
