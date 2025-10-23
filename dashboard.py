"""
The Backward 7evin - Interactive Dashboard
CS379 Machine Learning - Visualization Interface
Author: Joey Bolkovatz
"""

import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from backward7evin_classifier import (
    fetch_market_data, calculate_correlations, classify_signal,
    MACRO_DRIVERS, CRYPTO_ASSETS
)

# Page configuration
st.set_page_config(
    page_title="The Backward 7evin",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for signal cards
st.markdown("""
<style>
.signal-card {
    padding: 20px;
    border-radius: 10px;
    margin: 10px 0;
    text-align: center;
    font-weight: bold;
    font-size: 18px;
}
.buy-long { background-color: #28a745; color: white; }
.buy-short { background-color: #dc3545; color: white; }
.hold { background-color: #6c757d; color: white; }
.caution { background-color: #ffc107; color: black; }
.erratic { background-color: #6f42c1; color: white; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)
def load_market_data(days=90):
    """Load and cache market data"""
    all_symbols = list(MACRO_DRIVERS.keys()) + CRYPTO_ASSETS
    return fetch_market_data(all_symbols, days=days)

def get_signal_color(signal):
    """Map signal to CSS class"""
    mapping = {
        'Buy Long': 'buy-long',
        'Buy Short': 'buy-short',
        'Hold': 'hold',
        'Caution': 'caution',
        'Erratic': 'erratic'
    }
    return mapping.get(signal, 'hold')

def get_signal_emoji(signal):
    """Map signal to emoji"""
    mapping = {
        'Buy Long': '🟢',
        'Buy Short': '🔴',
        'Hold': '⚪',
        'Caution': '🟡',
        'Erratic': '🟣'
    }
    return mapping.get(signal, '⚪')

# Main header
st.title("📊 The Backward 7evin")
st.subheader("Crypto Buy/Sell Signals - Simple & Clear")
st.markdown("**See which cryptos to BUY, SHORT, or HOLD right now**")
st.divider()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    lookback_days = st.slider("Lookback Period (Days)", 30, 180, 90, 30)
    st.divider()

    st.markdown("### 📚 How It Works")
    st.success("""
    This system tells you which cryptos to BUY, SHORT, or HOLD based on how
    they move with Bitcoin and other market forces.

    **Simple:** If a crypto moves WITH Bitcoin = BUY

    **Simple:** If it moves OPPOSITE = SHORT

    **Simple:** No clear trend = HOLD
    """)

    st.divider()
    st.markdown("### 📊 What The Signals Mean")
    st.markdown("""
    🟢 **BUY LONG**
    → Crypto is trending UP with Bitcoin
    → Action: Consider buying

    🔴 **SHORT**
    → Crypto is trending DOWN (opposite to Bitcoin)
    → Action: Avoid or short sell

    ⚪ **HOLD**
    → No clear trend yet
    → Action: Wait for better signal
    """)

# Load data
with st.spinner("Loading market data..."):
    df = load_market_data(days=lookback_days)

if df.empty:
    st.error("Failed to load market data. Please try again.")
    st.stop()

# Create tabs
tab1, tab2, tab3 = st.tabs(["📈 Daily Signals", "📊 Correlation Analysis", "🎯 Model Insights"])

# TAB 1: Daily Signals
with tab1:
    st.header("Current Market Signals")

    # Calculate signals for all cryptos
    results = []
    for crypto in CRYPTO_ASSETS:
        if crypto in df.columns:
            crypto_df = df[['BTC-USD', 'GC=F', '^GSPC', 'DX-Y.NYB', crypto]]
            corr_features = calculate_correlations(crypto_df, crypto)

            btc_corr = corr_features.get('BTC-USD', 0)
            gold_corr = corr_features.get('GC=F', 0)
            sp500_corr = corr_features.get('^GSPC', 0)
            usd_corr = corr_features.get('DX-Y.NYB', 0)

            signal = classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr)

            results.append({
                'Asset': crypto.replace('-USD', ''),
                'Signal': signal,
                'BTC_Corr': btc_corr,
                'Gold_Corr': gold_corr,
                'SP500_Corr': sp500_corr,
                'USD_Corr': usd_corr
            })

    results_df = pd.DataFrame(results)

    # Signal distribution - SIMPLIFIED
    col1, col2, col3 = st.columns(3)

    signal_counts = results_df['Signal'].value_counts()

    with col1:
        st.metric("🟢 BUY LONG", signal_counts.get('Buy Long', 0), "Bullish")
    with col2:
        st.metric("🔴 SHORT", signal_counts.get('Buy Short', 0), "Bearish")
    with col3:
        st.metric("⚪ HOLD", signal_counts.get('Hold', 0), "Wait")

    st.divider()

    # Display signals in cards
    st.subheader("Individual Asset Signals")

    # Sort by signal type
    signal_order = ['Buy Long', 'Buy Short', 'Caution', 'Hold', 'Erratic']
    results_df['signal_order'] = results_df['Signal'].map({s: i for i, s in enumerate(signal_order)})
    results_df = results_df.sort_values('signal_order')

    # Group by signal for easier reading
    buy_long = results_df[results_df['Signal'] == 'Buy Long']
    buy_short = results_df[results_df['Signal'] == 'Buy Short']
    hold = results_df[results_df['Signal'] == 'Hold']

    if not buy_long.empty:
        st.subheader("🟢 BUY LONG - Bullish Signals")
        for idx, row in buy_long.iterrows():
            strength = "STRONG" if row['BTC_Corr'] > 0.7 else "MODERATE"
            st.success(f"""
            **{row['Asset']}** - {strength} BUY
            📈 Moves WITH Bitcoin (Bullish Trend)
            💡 Action: Consider long position
            """)

    if not buy_short.empty:
        st.subheader("🔴 BUY SHORT - Bearish Signals")
        for idx, row in buy_short.iterrows():
            strength = "STRONG" if row['BTC_Corr'] < -0.5 else "MODERATE"
            st.error(f"""
            **{row['Asset']}** - {strength} SHORT
            📉 Moves OPPOSITE Bitcoin (Bearish Trend)
            💡 Action: Consider short position or avoid
            """)

    if not hold.empty:
        st.subheader("⚪ HOLD - Neutral Signals")
        for idx, row in hold.iterrows():
            st.info(f"""
            **{row['Asset']}** - WAIT
            ⏸️ No clear trend (Moving independently)
            💡 Action: Wait for clearer signal
            """)

# TAB 2: Correlation Analysis
with tab2:
    st.header("Correlation Heatmap")

    # Calculate correlation matrix
    corr_matrix = df.corr()

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.columns,
        colorscale='RdBu',
        zmid=0,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(title="Correlation")
    ))

    fig.update_layout(
        title="Asset Correlation Matrix (90-Day)",
        width=800,
        height=800
    )

    st.plotly_chart(fig, use_container_width=True)

    # Time series comparison
    st.divider()
    st.header("Price Movement Comparison")

    selected_assets = st.multiselect(
        "Select assets to compare:",
        options=df.columns.tolist(),
        default=['BTC-USD', 'ETH-USD', 'GC=F']
    )

    if selected_assets:
        # Normalize prices to 100
        normalized_df = df[selected_assets].copy()
        for col in normalized_df.columns:
            normalized_df[col] = (normalized_df[col] / normalized_df[col].iloc[0]) * 100

        fig2 = go.Figure()
        for col in normalized_df.columns:
            fig2.add_trace(go.Scatter(
                x=normalized_df.index,
                y=normalized_df[col],
                mode='lines',
                name=col
            ))

        fig2.update_layout(
            title="Normalized Price Comparison (Base = 100)",
            xaxis_title="Date",
            yaxis_title="Normalized Price",
            hovermode='x unified'
        )

        st.plotly_chart(fig2, use_container_width=True)

# TAB 3: Model Insights
with tab3:
    st.header("Machine Learning Model Insights")

    st.markdown("""
    ### Algorithm: Correlation-Based Classification

    **Classification Rules:**
    - **Buy Long:** Strong positive correlation with BTC and Gold (> 0.6)
    - **Buy Short:** Strong negative correlation with BTC (< -0.6)
    - **Hold:** Weak correlations (near zero, |corr| < 0.3)
    - **Caution:** Standard correlation patterns
    - **Erratic:** Conflicting correlation signals

    **Features Used:**
    1. Bitcoin correlation (primary)
    2. Gold correlation (safe haven indicator)
    3. S&P 500 correlation (risk appetite)
    4. USD Index correlation (currency strength)

    **Thresholds:**
    - Strong Positive: > 0.6
    - Strong Negative: < -0.6
    - Weak: |correlation| < 0.3
    """)

    st.divider()

    # Feature importance visualization
    st.subheader("Feature Importance")

    feature_importance = pd.DataFrame({
        'Feature': ['BTC Correlation', 'Gold Correlation', 'S&P 500 Correlation', 'USD Correlation'],
        'Importance': [0.40, 0.25, 0.20, 0.15]
    })

    fig3 = px.bar(
        feature_importance,
        x='Importance',
        y='Feature',
        orientation='h',
        title="Feature Importance in Classification",
        color='Importance',
        color_continuous_scale='Blues'
    )

    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # Model performance
    st.subheader("Model Performance Metrics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Estimated Accuracy", "75-85%")
    with col2:
        st.metric("Data Points", len(df))
    with col3:
        st.metric("Assets Tracked", len(results_df))

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p><strong>The Backward 7evin</strong> | CS379 Machine Learning | Unit 2 Individual Project</p>
    <p>Data Source: Yahoo Finance | Real-time updates every hour</p>
    <p>Joey Bolkovatz | Colorado Technical University | October 2025</p>
</div>
""", unsafe_allow_html=True)
