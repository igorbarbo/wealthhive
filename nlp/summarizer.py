"""
Text summarization for financial documents
"""

from typing import List

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


class TextSummarizer:
    """Summarize financial text"""
    
    def __init__(self):
        self.model_name = "facebook/bart-large-cnn"  # Would use financial summarizer
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_model()
    
    def _load_model(self):
        """Load summarization model"""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
    
    async def summarize(self, text: str, max_length: int = 150) -> str:
        """Summarize text"""
        # Preprocess
        text = text.replace("\n", " ").strip()
        
        # Tokenize
        inputs = self.tokenizer(
            text,
            max_length=1024,
            truncation=True,
            return_tensors="pt",
        ).to(self.device)
        
        # Generate summary
        with torch.no_grad():
            summary_ids = self.model.generate(
                inputs["input_ids"],
                max_length=max_length,
                min_length=30,
                length_penalty=2.0,
                num_beams=4,
                early_stopping=True,
            )
        
        summary = self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True,
        )
        
        return summary
    
    async def summarize_batch(self, texts: List[str]) -> List[str]:
        """Summarize multiple texts"""
        summaries = []
        for text in texts:
            summary = await self.summarize(text)
            summaries.append(summary)
        return summaries
    
    def extract_key_sentences(self, text: str, n: int = 3) -> List[str]:
        """Extract most important sentences (extractive summarization)"""
        sentences = text.split(". ")
        
        # Simple scoring based on financial keywords
        financial_keywords = [
            "lucro", "receita", "ebitda", "dividendo", "projeção",
            "profit", "revenue", "guidance", "dividend", "forecast",
        ]
        
        scored = []
        for sent in sentences:
            score = sum(1 for kw in financial_keywords if kw in sent.lower())
            scored.append((sent, score))
        
        # Return top N
        scored.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored[:n]]
      
