"""
Backtesting page
"""

import streamlit as st


def show():
    """Show backtest page"""
    st.header("Backtesting")
    
    # Strategy configuration
    st.subheader("Configuração da Estratégia")
    
    col1, col2 = st.columns(2)
    
    with col1:
        strategy = st.selectbox(
            "Estratégia",
            ["Média Móvel", "Momentum", "Mean Reversion", "ML"],
        )
        
        symbol = st.text_input("Ativo", "PETR4")
        
        start_date = st.date_input("Data Início")
        end_date = st.date_input("Data Fim")
    
    with col2:
        initial_capital = st.number_input(
            "Capital Inicial",
            min_value=10000,
            value=100000,
        )
        
        if strategy == "Média Móvel":
            short_window = st.slider("Média Curta", 5, 50, 20)
            long_window = st.slider("Média Longa", 20, 200, 50)
    
    if st.button("Executar Backtest", type="primary"):
        with st.spinner("Executando backtest..."):
            # Run backtest
            st.success("Backtest concluído!")
            
            # Results
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Retorno Total", "45.2%")
            
            with col2:
                st.metric("Sharpe Ratio", "1.45")
            
            with col3:
                st.metric("Max Drawdown", "-12.3%")
            
            with col4:
                st.metric("Total Trades", "156")
            
            # Charts
            st.subheader("Curva de Equity")
            # Show equity curve
            
            st.subheader("Trades")
            # Show trade list
          
