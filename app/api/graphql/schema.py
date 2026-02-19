"""
GraphQL Schema Definition
"""

import strawberry
from typing import List, Optional
from datetime import datetime
from uuid import UUID


@strawberry.type
class User:
    id: UUID
    email: str
    full_name: str
    role: str
    is_active: bool
    created_at: datetime


@strawberry.type
class Asset:
    id: UUID
    symbol: str
    name: str
    asset_type: str
    exchange: Optional[str]
    currency: str
    sector: Optional[str]
    industry: Optional[str]
    current_price: Optional[float]


@strawberry.type
class Position:
    asset: Asset
    quantity: float
    avg_price: float
    current_price: Optional[float]
    market_value: Optional[float]
    unrealized_pnl: Optional[float]


@strawberry.type
class Portfolio:
    id: UUID
    name: str
    description: Optional[str]
    total_value: float
    total_return: float
    total_return_percent: float
    positions: List[Position]


@strawberry.type
class BacktestResult:
    id: UUID
    strategy_name: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float
    sharpe_ratio: float
    max_drawdown: float


@strawberry.type
class Query:
    @strawberry.field
    async def me(self, info) -> Optional[User]:
        """Get current user"""
        # Implementation
        pass
    
    @strawberry.field
    async def assets(self, info, search: Optional[str] = None) -> List[Asset]:
        """List assets"""
        # Implementation
        pass
    
    @strawberry.field
    async def asset(self, info, id: UUID) -> Optional[Asset]:
        """Get asset by ID"""
        # Implementation
        pass
    
    @strawberry.field
    async def portfolios(self, info) -> List[Portfolio]:
        """List user portfolios"""
        # Implementation
        pass
    
    @strawberry.field
    async def portfolio(self, info, id: UUID) -> Optional[Portfolio]:
        """Get portfolio by ID"""
        # Implementation
        pass
    
    @strawberry.field
    async def backtests(self, info) -> List[BacktestResult]:
        """List backtests"""
        # Implementation
        pass


@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_portfolio(self, info, name: str, description: Optional[str] = None) -> Portfolio:
        """Create new portfolio"""
        # Implementation
        pass
    
    @strawberry.mutation
    async def add_position(self, info, portfolio_id: UUID, asset_id: UUID, quantity: float, price: float) -> Position:
        """Add position to portfolio"""
        # Implementation
        pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
