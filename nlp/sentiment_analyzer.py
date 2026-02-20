"""
Financial sentiment analysis
"""

from typing import Any, Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

from app.config import settings


class SentimentAnalyzer:
    """Analyze sentiment of financial text"""
    
    def __init__(self, model_name: str = "finbert"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load appropriate model"""
        if self.model_name == "finbert":
            model_path = settings.FINBERT_MODEL
        elif self.model_name == "bertimbau":
            model_path = settings.BERTIMBAU_MODEL
        else:
            model_path = self.model_name
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
        self.model.to(self.device)
        self.model.eval()
    
    async def analyze(self, text: str, language: str = "auto") -> Dict[str, Any]:
        """Analyze sentiment of text"""
        # Detect language if auto
        if language == "auto":
            language = self._detect_language(text)
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True,
        ).to(self.device)
        
        # Predict
        with torch.no_grad():
            outputs = self.model(**inputs)
            probabilities = torch.softmax(outputs.logits, dim=1)
        
        # Get scores
        scores = probabilities[0].cpu().numpy()
        
        # Map to labels
        if len(scores) == 3:
            labels = ["negative", "neutral", "positive"]
        else:
            labels = ["negative", "positive"]
        
        score_dict = {label: float(score) for label, score in zip(labels, scores)}
        
        # Determine dominant sentiment
        dominant = max(score_dict, key=score_dict.get)
        
        return {
            "text": text[:100] + "..." if len(text) > 100 else text,
            "language": language,
            "sentiment": dominant,
            "confidence": round(score_dict[dominant], 4),
            "scores": {k: round(v, 4) for k, v in score_dict.items()},
        }
    
    def _detect_language(self, text: str) -> str:
        """Detect text language"""
        # Simple heuristic - would use langdetect in production
        portuguese_words = ["ação", "empresa", "mercado", "financeiro", "lucro", "prejuízo"]
        if any(word in text.lower() for word in portuguese_words):
            return "pt"
        return "en"
    
    async def analyze_batch(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Analyze multiple texts"""
        results = []
        for text in texts:
            result = await self.analyze(text)
            results.append(result)
        return results
