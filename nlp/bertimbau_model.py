"""
BERTimbau model wrapper for Portuguese financial text
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import settings


class BERTimbauModel:
    """BERTimbau for Portuguese financial sentiment"""
    
    def __init__(self):
        self.model_name = settings.BERTIMBAU_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load()
    
    def _load(self):
        """Load model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        # Would load fine-tuned version for financial sentiment
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=3,
        )
        self.model.to(self.device)
        self.model.eval()
        
        self.labels = ["negative", "neutral", "positive"]
    
    def predict(self, text: str) -> dict:
        """Predict sentiment"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            probs = torch.softmax(outputs.logits, dim=1)[0].cpu().numpy()
        
        return {
            "label": self.labels[probs.argmax()],
            "confidence": float(probs.max()),
            "scores": {label: float(prob) for label, prob in zip(self.labels, probs)},
        }
