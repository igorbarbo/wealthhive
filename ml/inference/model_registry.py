"""
Model registry for versioning and management
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import joblib


class ModelRegistry:
    """Model registry for versioning"""
    
    def __init__(self, registry_path: str = "./models/registry"):
        self.registry_path = registry_path
        os.makedirs(registry_path, exist_ok=True)
    
    def register(
        self,
        model: Any,
        model_id: str,
        version: str,
        metadata: Dict[str, Any],
    ) -> str:
        """Register new model version"""
        model_dir = os.path.join(self.registry_path, model_id, version)
        os.makedirs(model_dir, exist_ok=True)
        
        # Save model
        model_path = os.path.join(model_dir, "model.joblib")
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata_path = os.path.join(model_dir, "metadata.json")
        with open(metadata_path, "w") as f:
            json.dump({
                "model_id": model_id,
                "version": version,
                "registered_at": datetime.utcnow().isoformat(),
                **metadata,
            }, f, indent=2)
        
        # Update latest symlink
        latest_link = os.path.join(self.registry_path, model_id, "latest")
        if os.path.islink(latest_link):
            os.remove(latest_link)
        os.symlink(version, latest_link)
        
        return model_dir
    
    def load(self, model_id: str, version: str = "latest") -> Any:
        """Load model from registry"""
        if version == "latest":
            version = os.readlink(
                os.path.join(self.registry_path, model_id, "latest")
            )
        
        model_path = os.path.join(
            self.registry_path, model_id, version, "model.joblib"
        )
        
        return joblib.load(model_path)
    
    def get_metadata(self, model_id: str, version: str = "latest") -> Dict:
        """Get model metadata"""
        if version == "latest":
            version = os.readlink(
                os.path.join(self.registry_path, model_id, "latest")
            )
        
        metadata_path = os.path.join(
            self.registry_path, model_id, version, "metadata.json"
        )
        
        with open(metadata_path, "r") as f:
            return json.load(f)
    
    def list_models(self) -> Dict[str, list]:
        """List all registered models"""
        models = {}
        
        for model_id in os.listdir(self.registry_path):
            model_dir = os.path.join(self.registry_path, model_id)
            if os.path.isdir(model_dir):
                versions = [
                    d for d in os.listdir(model_dir)
                    if os.path.isdir(os.path.join(model_dir, d)) and d != "latest"
                ]
                models[model_id] = versions
        
        return models
