"""
Portfolio heatmap visualization
"""

import plotly.express as px


def create_correlation_heatmap(returns_df):
    """Create correlation heatmap"""
    corr = returns_df.corr()
    
    fig = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu",
        range_color=[-1, 1],
    )
    
    fig.update_layout(
        title="Matriz de Correlação",
    )
    
    return fig


def create_sector_heatmap(portfolio, sector_mapping):
    """Create sector allocation heatmap"""
    sector_weights = {}
    
    for asset, weight in portfolio.items():
        sector = sector_mapping.get(asset, "Outros")
        sector_weights[sector] = sector_weights.get(sector, 0) + weight
    
    fig = px.treemap(
        names=list(sector_weights.keys()),
        values=list(sector_weights.values()),
        title="Alocação por Setor",
    )
    
    return fig
  
