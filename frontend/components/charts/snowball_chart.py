"""
Snowball effect visualization
"""

import plotly.graph_objects as go


def create_snowball_chart(monthly_data):
    """Create snowball effect chart"""
    fig = go.Figure()
    
    # Balance line
    fig.add_trace(go.Scatter(
        x=list(range(len(monthly_data))),
        y=[m["balance"] for m in monthly_data],
        name="Patrimônio Total",
        fill="tozeroy",
        line=dict(color="green"),
    ))
    
    # Contributions line
    fig.add_trace(go.Scatter(
        x=list(range(len(monthly_data))),
        y=[m["contributions"] for m in monthly_data],
        name="Total Aportado",
        line=dict(color="blue"),
    ))
    
    fig.update_layout(
        title="Efeito Bola de Neve",
        xaxis_title="Meses",
        yaxis_title="Valor (R$)",
        hovermode="x unified",
    )
    
    return fig
  
