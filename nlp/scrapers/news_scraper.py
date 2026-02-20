"""
News scraping from various sources
"""

from typing import Any, Dict, List

import httpx
from bs4 import BeautifulSoup


class NewsScraper:
    """Scrape financial news"""
    
    SOURCES = {
        "infomoney": "https://www.infomoney.com.br",
        "valor": "https://valor.globo.com",
        "investing": "https://www.investing.com/news",
        "seeking_alpha": "https://seekingalpha.com",
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            timeout=30.0,
        )
    
    async def get_news_for_asset(
        self,
        symbol: str,
        days: int = 7,
    ) -> List[Dict[str, Any]]:
        """Get news for specific asset"""
        # This would scrape from multiple sources
        # Simplified implementation
        
        articles = []
        
        # Example: scrape from Investing.com
        try:
            url = f"{self.SOURCES['investing']}/equities/{symbol.lower()}"
            response = await self.client.get(url)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract articles (structure varies)
            news_items = soup.find_all("div", class_="textDiv")
            
            for item in news_items[:10]:
                title = item.find("a", class_="title")
                if title:
                    articles.append({
                        "title": title.text.strip(),
                        "source": "investing.com",
                        "published_at": None,  # Would parse date
                        "url": title.get("href"),
                    })
        
        except Exception as e:
            print(f"Error scraping {symbol}: {e}")
        
        return articles
    
    async def get_latest_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get latest market news"""
        # Aggregate from all sources
        all_news = []
        
        for source, base_url in self.SOURCES.items():
            try:
                news = await self._scrape_source(source, base_url, limit)
                all_news.extend(news)
            except Exception as e:
                print(f"Error scraping {source}: {e}")
        
        # Sort by date (newest first)
        all_news.sort(key=lambda x: x.get("published_at", ""), reverse=True)
        
        return all_news[:limit]
    
    async def _scrape_source(
        self,
        source: str,
        base_url: str,
        limit: int,
    ) -> List[Dict[str, Any]]:
        """Scrape specific source"""
        # Implementation varies by source structure
        return []
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
