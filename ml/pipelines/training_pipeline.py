"""
End-to-end training pipeline
"""

from typing import Any, Dict

from ml.pipelines.data_pipeline import DataPipeline
from ml.training.trainer import ModelTrainer


class TrainingPipeline:
    """Complete training pipeline"""
    
    def __init__(self):
        self.data_pipeline = DataPipeline()
        self.trainer = None
    
    def run(
        self,
        raw_data: Dict[str, Any],
        model_config: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Run complete training pipeline"""
        # 1. Data ingestion
        print("Step 1: Data ingestion")
        df = self._ingest_data(raw_data)
        
        # 2. Data preprocessing
        print("Step 2: Data preprocessing")
        df = self.data_pipeline.run(df)
        
        # 3. Feature engineering
        print("Step 3: Feature engineering")
        from ml.features.feature_engineering import FeatureEngineer
        engineer = FeatureEngineer()
        features = engineer.prepare_features(df)
        
        # 4. Model training
        print("Step 4: Model training")
        self.trainer = ModelTrainer(model_type=model_config.get("type", "ensemble"))
        training_result = self.trainer.train(features)
        
        # 5. Model evaluation
        print("Step 5: Model evaluation")
        # Evaluation happens during training
        
        # 6. Model registration
        print("Step 6: Model registration")
        model_id = model_config.get("model_id", "default")
        version = model_config.get("version", "v1")
        
        from ml.inference.model_registry import ModelRegistry
        registry = ModelRegistry()
        
        registry.register(
            model=self.trainer.model,
            model_id=model_id,
            version=version,
            metadata={
                "training_result": training_result,
                "model_config": model_config,
            },
        )
        
        return {
            "status": "success",
            "model_id": model_id,
            "version": version,
            "metrics": training_result["metrics"],
        }
    
    def _ingest_data(self, raw_data: Dict) -> Any:
        """Ingest data from various sources"""
        import pandas as pd
        
        if "dataframe" in raw_data:
            return raw_data["dataframe"]
        elif "csv_path" in raw_data:
            return pd.read_csv(raw_data["csv_path"])
        else:
            raise ValueError("No data source provided")
