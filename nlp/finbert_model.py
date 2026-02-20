"""
FinBERT model wrapper for English financial text
"""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import settings


class FinBERTModel:
    """FinBERT for English financial sentiment"""
    
    def __init__(self):
        self.model_name = settings.FINBERT_MODEL
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load()
    
    def _load(self):
        """Load model and tokenizer"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=3,  # negative, neutral, positive
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
    
    def predict_batch(self, texts: list) -> list:
        """Predict batch of texts"""
        return [self.predict(text) for text in texts]
