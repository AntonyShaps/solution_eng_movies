# Mock streamlit_star_rating for testing
import streamlit as st

def st_star_rating(label, maxValue=5, defaultValue=0, key=None, **kwargs):
    """Mock star rating component using streamlit slider"""
    return st.slider(
        label=label,
        min_value=0.0,
        max_value=float(maxValue),
        value=float(defaultValue),
        step=0.5,
        key=key,
        format="⭐ %.1f"
    )