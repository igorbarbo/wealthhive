"""
NLP and sentiment analysis endpoints
"""

from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Settings, get_settings
from app.dependencies import get_current_active_user, get_db
from nlp.sentiment_analyzer import SentimentAnalyzer

router = APIRouter()


@router.post("/analyze", response_model=dict)
async def analyze_text(
    text: str,
    language: str = "auto",  # auto, pt, en
    model: str = "finbert",  # finbert, bertimbau
    current_user: dict = Depends(get_current_active_user),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Analyze sentiment of text"""
    if not settings.ENABLE_NLP_SENTIMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP sentiment analysis is disabled",
        )
    
    analyzer = SentimentAnalyzer(model_name=model)
    result = await analyzer.analyze(text, language=language)
    
    return {
        "text": text[:200] + "..." if len(text) > 200 else text,
        "language": result["language"],
        "model": model,
        "sentiment": result["sentiment"],  # positive, negative, neutral
        "confidence": result["confidence"],
        "scores": result["scores"],  # {positive: 0.8, negative: 0.1, neutral: 0.1}
        "entities": result.get("entities", []),
    }


@router.get("/asset-sentiment/{asset_id}", response_model=dict)
async def get_asset_sentiment(
    asset_id: UUID,
    days: int = 7,
    current_user: dict = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Get aggregated sentiment for asset from news"""
    if not settings.ENABLE_NLP_SENTIMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP sentiment analysis is disabled",
        )
    
    from infrastructure.database.repositories.asset_repository import AssetRepository
    
    asset_repo = AssetRepository(db)
    asset = await asset_repo.get_by_id(asset_id)
    
    if not asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Asset not found",
        )
    
    from nlp.scrapers.news_scraper import NewsScraper
    
    scraper = NewsScraper()
    articles = await scraper.get_news_for_asset(asset.symbol, days=days)
    
    analyzer = SentimentAnalyzer()
    sentiments = []
    
    for article in articles:
        sentiment = await analyzer.analyze(article["title"] + " " + article.get("summary", ""))
        sentiments.append({
            "title": article["title"],
            "source": article["source"],
            "published_at": article["published_at"],
            "sentiment": sentiment["sentiment"],
            "confidence": sentiment["confidence"],
        })
    
    # Aggregate
    positive = sum(1 for s in sentiments if s["sentiment"] == "positive")
    negative = sum(1 for s in sentiments if s["sentiment"] == "negative")
    neutral = sum(1 for s in sentiments if s["sentiment"] == "neutral")
    total = len(sentiments)
    
    if total == 0:
        overall = "neutral"
        score = 0.5
    else:
        score = (positive * 1 + neutral * 0.5) / total
        if score > 0.6:
            overall = "positive"
        elif score < 0.4:
            overall = "negative"
        else:
            overall = "neutral"
    
    return {
        "asset_id": asset_id,
        "asset_symbol": asset.symbol,
        "period_days": days,
        "articles_analyzed": total,
        "overall_sentiment": overall,
        "sentiment_score": round(score, 2),
        "breakdown": {
            "positive": positive,
            "neutral": neutral,
            "negative": negative,
        },
        "recent_articles": sentiments[:10],
        "trend": "improving" if score > 0.6 else "declining" if score < 0.4 else "stable",
    }


@router.post("/summarize", response_model=dict)
async def summarize_text(
    text: str,
    max_length: int = 150,
    current_user: dict = Depends(get_current_active_user),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Summarize financial text"""
    if not settings.ENABLE_NLP_SENTIMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP is disabled",
        )
    
    from nlp.summarizer import TextSummarizer
    
    summarizer = TextSummarizer()
    summary = await summarizer.summarize(text, max_length=max_length)
    
    return {
        "original_length": len(text),
        "summary_length": len(summary),
        "summary": summary,
        "compression_ratio": round(len(summary) / len(text) * 100, 1),
    }


@router.get("/entities", response_model=dict)
async def extract_entities(
    text: str,
    current_user: dict = Depends(get_current_active_user),
    settings: Settings = Depends(get_settings),
) -> Any:
    """Extract financial entities from text"""
    if not settings.ENABLE_NLP_SENTIMENT:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="NLP is disabled",
        )
    
    from nlp.entity_extractor import EntityExtractor
    
    extractor = EntityExtractor()
    entities = await extractor.extract(text)
    
    return {
        "text": text[:200] + "..." if len(text) > 200 else text,
        "entities": entities,
        "categories": list(set(e["type"] for e in entities)),
    }
