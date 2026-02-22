"""
Table components
"""

import pandas as pd
import streamlit as st


def styled_dataframe(df, highlight_column=None):
    """Create styled dataframe"""
    def color_negative_red(val):
        color = 'red' if val < 0 else 'green'
        return f'color: {color}'
    
    styled = df.style
    
    if highlight_column:
        styled = styled.applymap(
            color_negative_red,
            subset=[highlight_column],
        )
    
    return styled


def paginated_table(df, page_size=10):
    """Create paginated table"""
    total_pages = len(df) // page_size + (1 if len(df) % page_size > 0 else 0)
    
    page = st.number_input(
        "Página",
        min_value=1,
        max_value=total_pages,
        value=1,
    )
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    
    st.dataframe(df.iloc[start_idx:end_idx])
    
    st.write(f"Página {page} de {total_pages} ({len(df)} registros)")


def sortable_table(df, default_sort=None):
    """Create sortable table"""
    sort_column = st.selectbox(
        "Ordenar por",
        df.columns,
        index=df.columns.get_loc(default_sort) if default_sort else 0,
    )
    
    sort_order = st.radio("Ordem", ["Ascendente", "Descendente"])
    
    ascending = sort_order == "Ascendente"
    
    sorted_df = df.sort_values(by=sort_column, ascending=ascending)
    
    st.dataframe(sorted_df)
  
