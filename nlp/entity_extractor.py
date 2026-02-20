"""
Named Entity Recognition for financial text
"""

import re
from typing import Dict, List

import spacy


class EntityExtractor:
    """Extract financial entities from text"""
    
    def __init__(self):
        # Would load custom financial NER model
        self.nlp = spacy.load("en_core_web_sm")
    
    async def extract(self, text: str) -> List[Dict]:
        """Extract entities"""
        doc = self.nlp(text)
        
        entities = []
        
        # Standard NER
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "type": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char,
            })
        
        # Custom financial entities
        entities.extend(self._extract_financial_entities(text))
        
        return entities
    
    def _extract_financial_entities(self, text: str) -> List[Dict]:
        """Extract financial-specific entities"""
        entities = []
        
        # Money amounts
        money_pattern = r"(?:R\$|US\$|\$)\s*[\d.,]+(?:\s*(?:milhões|bilhões|milhão|bilhão|million|billion))?"
        for match in re.finditer(money_pattern, text, re.IGNORECASE):
            entities.append({
                "text": match.group(),
                "type": "MONEY",
                "start": match.start(),
                "end": match.end(),
            })
        
        # Percentages
        percent_pattern = r"\d+(?:\.\d+)?\s*%"
        for match in re.finditer(percent_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "PERCENT",
                "start": match.start(),
                "end": match.end(),
            })
        
        # Dates
        date_pattern = r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2}"
        for match in re.finditer(date_pattern, text):
            entities.append({
                "text": match.group(),
                "type": "DATE",
                "start": match.start(),
                "end": match.end(),
            })
        
        return entities
