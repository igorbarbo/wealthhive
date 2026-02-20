"""
Text preprocessing for financial NLP
"""

import re
from typing import List

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


class TextPreprocessor:
    """Preprocess financial text"""
    
    def __init__(self, language: str = "portuguese"):
        self.language = language
        self.stop_words = set(stopwords.words(language))
        
        # Financial-specific stopwords
        self.financial_stopwords = {
            "rs", "reais", "mil", "milhões", "bilhões", "trilhões",
            "company", "inc", "corp", "ltd", "sa", "s/a",
        }
        self.stop_words.update(self.financial_stopwords)
    
    def clean(self, text: str) -> str:
        """Clean text"""
        # Lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r"http\S+|www\S+|https\S+", "", text, flags=re.MULTILINE)
        
        # Remove user mentions and hashtags
        text = re.sub(r"@\w+|#\w+", "", text)
        
        # Remove extra whitespace
        text = " ".join(text.split())
        
        return text
    
    def tokenize(self, text: str) -> List[str]:
        """Tokenize text"""
        tokens = word_tokenize(text, language=self.language)
        return tokens
    
    def remove_stopwords(self, tokens: List[str]) -> List[str]:
        """Remove stopwords"""
        return [t for t in tokens if t not in self.stop_words and len(t) > 2]
    
    def preprocess(self, text: str) -> str:
        """Full preprocessing pipeline"""
        text = self.clean(text)
        tokens = self.tokenize(text)
        tokens = self.remove_stopwords(tokens)
        return " ".join(tokens)
    
    def extract_tickers(self, text: str) -> List[str]:
        """Extract stock tickers from text"""
        # Brazilian tickers: 4-5 uppercase letters ending with number
        brazilian = re.findall(r"\b[A-Z]{4}[0-9]{1,2}\b", text.upper())
        
        # US tickers: 1-5 uppercase letters
        us = re.findall(r"\b[A-Z]{1,5}\b", text.upper())
        
        return list(set(brazilian + us))
