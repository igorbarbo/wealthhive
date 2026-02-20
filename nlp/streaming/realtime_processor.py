"""
Real-time NLP processing for streaming data
"""

import asyncio
from typing import Any, Callable, Dict, List

from nlp.news_classifier import NewsClassifier
from nlp.sentiment_analyzer import SentimentAnalyzer


class RealtimeNLPProcessor:
    """Process news in real-time"""
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.news_classifier = NewsClassifier()
        self.callbacks: List[Callable] = []
        self.processing_queue = asyncio.Queue()
    
    def register_callback(self, callback: Callable):
        """Register callback for processed news"""
        self.callbacks.append(callback)
    
    async def process_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Process single article"""
        # Analyze sentiment
        sentiment = await self.sentiment_analyzer.analyze(
            article.get("title", "") + " " + article.get("summary", "")
        )
        
        # Classify
        classification = self.news_classifier.classify(
            article.get("title", ""),
            article.get("content", ""),
        )
        
        # Extract entities
        from nlp.entity_extractor import EntityExtractor
        extractor = EntityExtractor()
        entities = await extractor.extract(
            article.get("title", "") + " " + article.get("content", "")
        )
        
        # Combine results
        processed = {
            **article,
            "sentiment": sentiment,
            "classification": classification,
            "entities": entities,
            "processed_at": asyncio.get_event_loop().time(),
        }
        
        # Notify callbacks
        for callback in self.callbacks:
            await callback(processed)
        
        return processed
    
    async def start_processing_loop(self):
        """Start continuous processing"""
        while True:
            article = await self.processing_queue.get()
            await self.process_article(article)
            self.processing_queue.task_done()
    
    async def submit(self, article: Dict[str, Any]):
        """Submit article for processing"""
        await self.processing_queue.put(article)
      
