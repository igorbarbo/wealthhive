"""
Risk visualization charts
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots


def create_var_chart(returns, var_threshold):
    """Create VaR distribution chart"""
    fig = go.Figure()
    
    # Histogram of returns
    fig.add_trace(go.Histogram(
        x=returns,
        nbinsx=50,
        name="Retornos",
        opacity=0.7,
    ))
    
    # VaR line
    fig.add_vline(
        x=var_threshold,
        line_dash="dash",
        line_color="red",
        annotation_text=f"VaR: {var_threshold:.2%}",
    )
    
    fig.update_layout(
        title="Distribuição de Retornos - Value at Risk",
        xaxis_title="Retorno",
        yaxis_title="Frequência",
    )
    
    return fig


def create_drawdown_chart(equity_curve):
    """Create drawdown chart"""
    # Calculate drawdown
    peak = equity_curve.expanding().max()
    drawdown = (equity_curve - peak) / peak
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown,
        fill="tozeroy",
        name="Drawdown",
        line=dict(color="red"),
    ))
    
    fig.update_layout(
        title="Drawdown ao Longo do Tempo",
        xaxis_title="Data",
        yaxis_title="Drawdown %",
        yaxis_tickformat=".1%",
    )
    
    return fig
  
