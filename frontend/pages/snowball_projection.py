"""
Snowball projection page
"""

import streamlit as st


def show():
    """Show snowball projection"""
    st.header("🍯 Projeção Bola de Neve")
    
    st.write("Simule o efeito composto do reinvestimento de dividendos")
    
    # Inputs
    col1, col2 = st.columns(2)
    
    with col1:
        initial = st.number_input(
            "Investimento Inicial",
            min_value=0,
            value=10000,
        )
        
        monthly = st.number_input(
            "Aporte Mensal",
            min_value=0,
            value=1000,
        )
        
        years = st.slider("Horizonte (anos)", 1, 40, 20)
    
    with col2:
        return_rate = st.slider(
            "Retorno Anual Esperado (%)",
            0.0,
            20.0,
            12.0,
        ) / 100
        
        dividend_yield = st.slider(
            "Dividend Yield (%)",
            0.0,
            10.0,
            4.0,
        ) / 100
        
        reinvest = st.checkbox("Reinvestir Dividendos", value=True)
    
    if st.button("Calcular Projeção", type="primary"):
        # Calculate projection
        from core.use_cases.portfolio.snowball_simulation import SnowballSimulationUseCase
        
        simulator = SnowballSimulationUseCase()
        result = simulator.calculate(
            initial_investment=initial,
            monthly_contribution=monthly,
            annual_return_rate=return_rate,
            years=years,
            reinvest_dividends=reinvest,
            dividend_yield=dividend_yield,
        )
        
        # Display results
        st.subheader("Resultados")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Valor Final", f"R$ {result.final_value:,.2f}")
        
        with col2:
            st.metric("Total Aportado", f"R$ {result.total_contributions:,.2f}")
        
        with col3:
            st.metric("Dividendos", f"R$ {result.total_dividends:,.2f}")
        
        with col4:
            st.metric("Retorno Total", f"R$ {result.total_return:,.2f}")
        
        # Chart
        st.subheader("Evolução do Patrimônio")
        
        # Convert monthly data to chart
        import pandas as pd
        
        df = pd.DataFrame(result.monthly_data)
        df["date"] = pd.to_datetime(df[["year", "month"]].assign(day=1))
        
        st.line_chart(df.set_index("date")[["balance", "contributions"]])
        
        # Milestones
        st.subheader("Marcos")
        
        for milestone in result.milestones:
            st.write(f"💰 R$ {milestone['amount']:,.0f} em {milestone['year']:.1f} anos")
          
