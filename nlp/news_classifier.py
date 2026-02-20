"""
News article classifier
"""

from typing import Dict, List

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer


class NewsClassifier:
    """Classify financial news by category and impact"""
    
    CATEGORIES = [
        "earnings",
        "merger_acquisition",
        "product_launch",
        "regulatory",
        "market_movement",
        "executive_changes",
        "legal",
        "macroeconomic",
        "other",
    ]
    
    def __init__(self):
        self.model_name = "ProsusAI/finbert"  # Would use fine-tuned model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load classification model"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=len(self.CATEGORIES),
        )
        self.model.to(self.device)
        self.model.eval()
    
    def classify(self, title: str, content: str = "") -> Dict:
        """Classify news article"""
        text = f"{title}. {content}"[:512]
        
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
        
        category = self.CATEGORIES[probs.argmax()]
        confidence = float(probs.max())
        
        # Determine impact level
        impact = self._determine_impact(title, content, category)
        
        return {
            "category": category,
            "confidence": round(confidence, 4),
            "impact": impact,
            "all_scores": {
                cat: round(float(prob), 4)
                for cat, prob in zip(self.CATEGORIES, probs)
            },
        }
    
    def _determine_impact(self, title: str, content: str, category: str) -> str:
        """Determine news impact level"""
        text = (title + " " + content).lower()
        
        high_impact_keywords = [
            "crash", "colapso", "falência", "bankruptcy", "merger", "aquisição",
            "acquisition", "ipo", "dividendo extraordinário", "lucro recorde",
        ]
        
        medium_impact_keywords = [
            "resultado", "earnings", "guidance", "projeção", "forecast",
            "upgrade", "downgrade", "rating",
        ]
        
        if any(kw in text for kw in high_impact_keywords):
            return "high"
        elif any(kw in text for kw in medium_impact_keywords):
            return "medium"
        else:
            return "low"
    
    def classify_batch(self, articles: List[Dict]) -> List[Dict]:
        """Classify multiple articles"""
        return [
            {
                **article,
                "classification": self.classify(
                    article.get("title", ""),
                    article.get("content", ""),
                ),
            }
            for article in articles
        ]
