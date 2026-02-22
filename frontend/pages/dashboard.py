"""
Dashboard page
"""

import streamlit as st


def show():
    """Show dashboard"""
    st.header("Dashboard")
    
    # Portfolio summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Valor Total",
            value="R$ 150.000,00",
            delta="R$ 5.000,00",
        )
    
    with col2:
        st.metric(
            label="Retorno Total",
            value="15.3%",
            delta="2.1%",
        )
    
    with col3:
        st.metric(
            label="Sharpe Ratio",
            value="1.85",
            delta="0.12",
        )
    
    with col4:
        st.metric(
            label="Drawdown Máx",
            value="-8.5%",
            delta="-1.2%",
        )
    
    # Charts
    st.subheader("Evolução do Portfólio")
    # Would show chart
    
    st.subheader("Alocação")
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart of allocation
        pass
    
    with col2:
        # Table of positions
        pass
    
    # Recent activity
    st.subheader("Atividade Recente")
    # Show recent trades, alerts, etc.
  
