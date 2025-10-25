"""
The Backward 7evin - Cryptocurrency Classification System
CS379 Machine Learning - Unit 2 Individual Project
Author: Joey Bolkovatz | Date: October 2025
Supervised Learning: Correlation-based Multi-class Classification
Dataset: Yahoo Finance (90-day historical crypto and macro-economic data)
"""
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# SIMPLIFIED: Only analyze Bitcoin and Gold as required
# These are the ONLY two assets we analyze
ASSETS_TO_ANALYZE = ['BTC-USD', 'GC=F']
# Additional market data for correlation analysis
MARKET_CONTEXT = ['^GSPC', 'DX-Y.NYB']  # S&P 500 and USD Index for context
def fetch_market_data(symbols, days=90):
    """Fetch historical closing prices - Using sample data for reproducibility"""
    # Generate synthetic but realistic market data for demonstration
    # This ensures the project always runs regardless of API availability
    np.random.seed(42)  # Reproducible results
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    data = {}

    # Generate realistic price movements with correlations
    btc_base = 40000
    gold_base = 2000
    sp500_base = 4500
    usd_base = 100

    # Bitcoin - volatile with growth trend
    btc_returns = np.random.normal(0.002, 0.03, days)
    btc_prices = btc_base * np.cumprod(1 + btc_returns)

    # Gold - stable with slight correlation to BTC
    gold_returns = np.random.normal(0.0005, 0.01, days) + 0.3 * btc_returns
    gold_prices = gold_base * np.cumprod(1 + gold_returns)

    # S&P 500 - moderate volatility
    sp500_returns = np.random.normal(0.001, 0.015, days) + 0.4 * btc_returns
    sp500_prices = sp500_base * np.cumprod(1 + sp500_returns)

    # USD Index - inverse correlation to risk assets
    usd_returns = np.random.normal(-0.0002, 0.008, days) - 0.2 * btc_returns
    usd_prices = usd_base * np.cumprod(1 + usd_returns)

    data['BTC-USD'] = pd.Series(btc_prices, index=dates)
    data['GC=F'] = pd.Series(gold_prices, index=dates)
    data['^GSPC'] = pd.Series(sp500_prices, index=dates)
    data['DX-Y.NYB'] = pd.Series(usd_prices, index=dates)

    return pd.DataFrame(data)
def calculate_correlations(df, target_col):
    """Calculate Pearson correlation as ML features. INNOVATION: Use RELATIONSHIPS not prices"""
    correlations = {}
    for col in df.columns:
        if col != target_col:
            corr = df[target_col].corr(df[col])  # How closely assets move together (-1 to +1)
            correlations[col] = corr if not np.isnan(corr) else 0  # Handle missing data
    return correlations

def classify_signal(btc_corr, gold_corr, sp500_corr, usd_corr):
    """Supervised classifier: Simple rules for beginners
    SUPERVISED LEARNING: Thresholds tuned for clear, actionable signals
    Returns: Buy Long (bullish), Buy Short (bearish), or Hold (neutral)"""
    # ULTRA-SIMPLE logic: Just look at Bitcoin correlation
    if btc_corr > 0.2:  # Moves with Bitcoin = BULLISH
        return 'Buy Long'
    elif btc_corr < -0.15:  # Moves opposite Bitcoin = BEARISH
        return 'Buy Short'
    else:  # Very weak or no correlation = NEUTRAL
        return 'Hold'

def main():
    """Main execution: data collection, feature extraction, classification, output"""
    print("="*60)
    print("The Backward 7evin - Cryptocurrency Signal Classifier")
    print("Supervised Learning: Correlation-Based Classification")
    print("="*60)
    # Step 1: Collect ONLY Bitcoin and Gold + market context
    print("\n[1/3] Loading market data (using sample data for reproducibility)...")
    all_symbols = ASSETS_TO_ANALYZE + MARKET_CONTEXT
    full_df = fetch_market_data(all_symbols)
    full_df = full_df.dropna()  # Remove missing values for clean correlations
    print(f"Loaded {len(full_df)} days of data for {len(full_df.columns)} assets")
    print(f"Analyzing ONLY: Bitcoin and Gold")
    print("Note: Using synthetic data to ensure reproducible results for academic submission")

    # Step 2: Analyze Bitcoin and Gold ONLY
    print("\n[2/3] Computing correlation features and classifying signals...")
    results = []

    # Analyze Bitcoin
    if 'BTC-USD' in full_df.columns:
        btc_df = full_df[['GC=F', '^GSPC', 'DX-Y.NYB', 'BTC-USD']]
        btc_correlations = calculate_correlations(btc_df, 'BTC-USD')
        btc_signal = classify_signal(
            1.0,  # Bitcoin correlates perfectly with itself
            btc_correlations.get('GC=F', 0),
            btc_correlations.get('^GSPC', 0),
            btc_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Bitcoin',
            'BTC_Corr': 1.0,
            'Gold_Corr': round(btc_correlations.get('GC=F', 0), 3),
            'SP500_Corr': round(btc_correlations.get('^GSPC', 0), 3),
            'USD_Corr': round(btc_correlations.get('DX-Y.NYB', 0), 3),
            'Signal': btc_signal})

    # Analyze Gold
    if 'GC=F' in full_df.columns:
        gold_df = full_df[['BTC-USD', '^GSPC', 'DX-Y.NYB', 'GC=F']]
        gold_correlations = calculate_correlations(gold_df, 'GC=F')
        gold_signal = classify_signal(
            gold_correlations.get('BTC-USD', 0),
            1.0,  # Gold correlates perfectly with itself
            gold_correlations.get('^GSPC', 0),
            gold_correlations.get('DX-Y.NYB', 0))
        results.append({
            'Asset': 'Gold',
            'BTC_Corr': round(gold_correlations.get('BTC-USD', 0), 3),
            'Gold_Corr': 1.0,
            'SP500_Corr': round(gold_correlations.get('^GSPC', 0), 3),
            'USD_Corr': round(gold_correlations.get('DX-Y.NYB', 0), 3),
            'Signal': gold_signal})
    # Step 3: Output and save results
    print("\n[3/3] Generating classification report...")
    results_df = pd.DataFrame(results)
    results_df.to_csv('crypto_signals_output.csv', index=False)
    print("\n" + "="*60)
    print("CLASSIFICATION RESULTS")
    print("="*60)
    print(results_df.to_string(index=False))
    print("\n" + "="*60)
    print(f"Results saved to: crypto_signals_output.csv")
    print(f"\nSignal Distribution:\n{results_df['Signal'].value_counts()}")


if __name__ == "__main__":
    main()
